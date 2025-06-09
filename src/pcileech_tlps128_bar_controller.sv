//==============================================================================
// PCIe BAR Controller with Configuration Space Shadow Integration
//
// This module implements a BAR controller that interfaces with the configuration
// space shadow BRAM to provide a complete PCIe device emulation solution.
//
// Features:
// - BAR0 memory space access handling
// - Integration with 4 KB configuration space shadow
// - Support for PCIe TLP (Transaction Layer Packet) handling
//==============================================================================

module pcileech_tlps128_bar_controller #(
    parameter BAR_APERTURE_SIZE = 131072,  // Default: 128 KB
    parameter NUM_MSIX = 1,                // Number of MSI-X table entries
    parameter MSIX_TABLE_BIR = 0,          // BAR indicator for MSI-X table
    parameter MSIX_TABLE_OFFSET = 0,       // Offset of MSI-X table in the BAR
    parameter MSIX_PBA_BIR = 0,            // BAR indicator for MSI-X PBA
    parameter MSIX_PBA_OFFSET = 0          // Offset of MSI-X PBA in the BAR
) (
    // Clock and reset
    input  logic        clk,
    input  logic        reset_n,
    
    // PCIe BAR interface
    input  logic [31:0] bar_addr,
    input  logic [31:0] bar_wr_data,
    input  logic        bar_wr_en,
    input  logic        bar_rd_en,
    output logic [31:0] bar_rd_data,
    
    // PCIe configuration space interface
    input  logic        cfg_ext_read_received,
    input  logic        cfg_ext_write_received,
    input  logic [9:0]  cfg_ext_register_number,
    input  logic [3:0]  cfg_ext_function_number,
    input  logic [31:0] cfg_ext_write_data,
    input  logic [3:0]  cfg_ext_write_byte_enable,
    output logic [31:0] cfg_ext_read_data,
    output logic        cfg_ext_read_data_valid,
    
    // MSI-X interrupt interface
    output logic        msix_interrupt,    // MSI-X interrupt request
    output logic [10:0] msix_vector,       // MSI-X vector number
    input  logic        msix_interrupt_ack  // Acknowledge from PCIe core
);

    // Instantiate the configuration space shadow module
    pcileech_tlps128_cfgspace_shadow config_space (
        .clk(clk),
        .reset_n(reset_n),
        
        // PCIe configuration access
        .cfg_ext_read_received(cfg_ext_read_received),
        .cfg_ext_write_received(cfg_ext_write_received),
        .cfg_ext_register_number(cfg_ext_register_number),
        .cfg_ext_function_number(cfg_ext_function_number),
        .cfg_ext_write_data(cfg_ext_write_data),
        .cfg_ext_write_byte_enable(cfg_ext_write_byte_enable),
        .cfg_ext_read_data(cfg_ext_read_data),
        .cfg_ext_read_data_valid(cfg_ext_read_data_valid),
        
        // Host access for initialization and monitoring
        .host_access_en(bar_access_to_config),
        .host_write_en(bar_wr_en && bar_access_to_config),
        .host_addr(bar_addr[11:0]),
        .host_write_data(bar_wr_data),
        .host_read_data(config_space_read_data)
    );
    
    // Extract MSI-X control information from config space
    logic msix_enabled;
    logic msix_function_masked;
    
    // MSI-X capability is typically at a fixed offset in config space
    // For this implementation, we'll assume it's read from the config space
    // In a real implementation, these would be connected to the actual MSI-X capability registers
    assign msix_enabled = 1'b1;  // Default to enabled for testing
    assign msix_function_masked = 1'b0;  // Default to unmasked for testing
    
    // Instantiate the MSI-X table module
    msix_table #(
        .NUM_MSIX(NUM_MSIX),
        .MSIX_TABLE_BIR(MSIX_TABLE_BIR),
        .MSIX_TABLE_OFFSET(MSIX_TABLE_OFFSET),
        .MSIX_PBA_BIR(MSIX_PBA_BIR),
        .MSIX_PBA_OFFSET(MSIX_PBA_OFFSET)
    ) msix_table_inst (
        .clk(clk),
        .reset_n(reset_n),
        
        // BAR access interface
        .bar_addr(bar_addr),
        .bar_index(3'b000),  // Assuming BAR0 for simplicity
        .bar_wr_data(bar_wr_data),
        .bar_wr_en(bar_wr_en),
        .bar_wr_be(cfg_ext_write_byte_enable),  // Reuse byte enables from config space
        .bar_rd_en(bar_rd_en),
        .bar_rd_data(msix_table_read_data),
        .bar_access_match(bar_access_to_msix),
        
        // MSI-X control interface
        .msix_enable(msix_enabled),
        .msix_function_mask(msix_function_masked),
        
        // Interrupt interface
        .msix_interrupt(msix_interrupt),
        .msix_vector(msix_vector),
        .msix_interrupt_ack(msix_interrupt_ack)
    );
    
    // BAR memory space (excluding configuration space and MSI-X table access)
    (* ram_style="block" *) logic [31:0] bar_memory[(BAR_APERTURE_SIZE/4)-1:0];
    
    // Signals for BAR access routing
    logic bar_access_to_config;
    logic bar_access_to_msix;
    logic [31:0] config_space_read_data;
    logic [31:0] msix_table_read_data;
    
    // Determine if BAR access should be routed to configuration space
    // We reserve the top 4KB of BAR space for configuration space access
    assign bar_access_to_config = (bar_addr[31:12] == 20'hFFFFF);
    
    // BAR read data multiplexer
    always_comb begin
        if (bar_access_to_config) begin
            bar_rd_data = config_space_read_data;
        end else if (bar_access_to_msix) begin
            bar_rd_data = msix_table_read_data;
        end else if (bar_addr[31:2] < (BAR_APERTURE_SIZE/4)) begin
            bar_rd_data = bar_memory[bar_addr[31:2]];
        end else begin
            bar_rd_data = 32'hDEADBEEF;  // Default value for out-of-range access
        end
    end
    
    // BAR write logic
    always_ff @(posedge clk) begin
        if (bar_wr_en && !bar_access_to_config && !bar_access_to_msix &&
            (bar_addr[31:2] < (BAR_APERTURE_SIZE/4))) begin
            bar_memory[bar_addr[31:2]] <= bar_wr_data;
        end
    end
    
    // Initialize BAR memory to zeros
    initial begin
        for (int i = 0; i < (BAR_APERTURE_SIZE/4); i++) begin
            bar_memory[i] = 32'h0;
        end
    end
    
    // Function to trigger an MSI-X interrupt
    // This can be called by other modules to trigger an interrupt
    function void trigger_msix_interrupt(input logic [10:0] vector);
        if (vector < NUM_MSIX) begin
            msix_table_inst.trigger_interrupt(vector);
        end
    endfunction

endmodule