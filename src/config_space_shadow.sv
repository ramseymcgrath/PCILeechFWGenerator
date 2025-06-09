//==============================================================================
// PCIe Configuration Space Shadow BRAM
// 
// This module implements a full 4 KB configuration space shadow in BRAM
// with dual-port access and overlay RAM for writable fields.
//
// Features:
// - Full 4 KB configuration space shadow in BRAM
// - Dual-port access for simultaneous read/write
// - Overlay RAM for writable fields (Command/Status registers)
// - Initialization from donor device configuration data
//==============================================================================

module config_space_shadow #(
    parameter CONFIG_SPACE_SIZE = 4096,  // 4 KB configuration space
    parameter OVERLAY_ENTRIES = 32       // Number of overlay RAM entries
) (
    // Clock and reset
    input  logic        clk,
    input  logic        reset_n,
    
    // Port A - PCIe configuration access
    input  logic        cfg_ext_read_received,
    input  logic        cfg_ext_write_received,
    input  logic [9:0]  cfg_ext_register_number,
    input  logic [3:0]  cfg_ext_function_number,
    input  logic [31:0] cfg_ext_write_data,
    input  logic [3:0]  cfg_ext_write_byte_enable,
    output logic [31:0] cfg_ext_read_data,
    output logic        cfg_ext_read_data_valid,
    
    // Port B - Host access for initialization and monitoring
    input  logic        host_access_en,
    input  logic        host_write_en,
    input  logic [11:0] host_addr,
    input  logic [31:0] host_write_data,
    output logic [31:0] host_read_data
);

    // Main configuration space BRAM (4 KB = 1024 dwords)
    (* ram_style="block" *) logic [31:0] config_space_ram[0:1023];
    
    // Overlay RAM for writable fields (32 entries)
    logic [31:0] overlay_ram[0:OVERLAY_ENTRIES-1];
    
    // Overlay RAM address mapping
    // This maps configuration register numbers to overlay RAM indices
    // Only registers that have writable fields need entries
    function int get_overlay_index(input logic [9:0] reg_num);
        case (reg_num)
            10'h001: return 0;  // Command register (offset 0x04)
            10'h002: return 1;  // Status register (offset 0x08)
            10'h004: return 2;  // Cache Line Size register (offset 0x0C)
            10'h00D: return 3;  // Latency Timer / BIST register (offset 0x3C)
            // Add more mappings as needed for other writable registers
            default: return -1; // No overlay entry
        endcase
    endfunction
    
    // Overlay mask function - defines which bits in each register are writable
    function logic [31:0] get_overlay_mask(input logic [9:0] reg_num);
        case (reg_num)
            10'h001: return 32'h0000FFFF;  // Command register - lower 16 bits writable
            10'h002: return 32'h0000FFFF;  // Status register - lower 16 bits writable
            10'h004: return 32'h000000FF;  // Cache Line Size - lower 8 bits writable
            10'h00D: return 32'h0000FF00;  // Latency Timer - bits 8-15 writable
            // Add more masks as needed
            default: return 32'h00000000;  // No writable bits
        endcase
    endfunction
    
    // PCIe configuration access state machine
    typedef enum logic [1:0] {
        CFG_IDLE,
        CFG_READ,
        CFG_WRITE,
        CFG_COMPLETE
    } cfg_state_t;
    
    cfg_state_t cfg_state = CFG_IDLE;
    logic [9:0] current_reg_num;
    logic [31:0] read_data;
    logic read_data_valid;
    
    // Configuration access state machine
    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            cfg_state <= CFG_IDLE;
            read_data_valid <= 1'b0;
            read_data <= 32'h0;
            current_reg_num <= 10'h0;
        end else begin
            case (cfg_state)
                CFG_IDLE: begin
                    read_data_valid <= 1'b0;
                    
                    if (cfg_ext_read_received) begin
                        cfg_state <= CFG_READ;
                        current_reg_num <= cfg_ext_register_number;
                    end else if (cfg_ext_write_received) begin
                        cfg_state <= CFG_WRITE;
                        current_reg_num <= cfg_ext_register_number;
                    end
                end
                
                CFG_READ: begin
                    // Read from configuration space
                    read_data <= config_space_ram[current_reg_num];
                    
                    // Check if this register has an overlay entry
                    int overlay_idx = get_overlay_index(current_reg_num);
                    if (overlay_idx >= 0) begin
                        // Apply overlay data for writable bits
                        logic [31:0] overlay_mask = get_overlay_mask(current_reg_num);
                        read_data <= (config_space_ram[current_reg_num] & ~overlay_mask) | 
                                     (overlay_ram[overlay_idx] & overlay_mask);
                    end
                    
                    read_data_valid <= 1'b1;
                    cfg_state <= CFG_COMPLETE;
                end
                
                CFG_WRITE: begin
                    // Handle write to configuration space
                    int overlay_idx = get_overlay_index(current_reg_num);
                    if (overlay_idx >= 0) begin
                        // Only update writable bits in the overlay RAM
                        logic [31:0] overlay_mask = get_overlay_mask(current_reg_num);
                        logic [31:0] current_value = overlay_ram[overlay_idx];
                        
                        // Apply byte enables
                        if (cfg_ext_write_byte_enable[0])
                            current_value[7:0] = (cfg_ext_write_data[7:0] & overlay_mask[7:0]) | 
                                                (current_value[7:0] & ~overlay_mask[7:0]);
                        if (cfg_ext_write_byte_enable[1])
                            current_value[15:8] = (cfg_ext_write_data[15:8] & overlay_mask[15:8]) | 
                                                 (current_value[15:8] & ~overlay_mask[15:8]);
                        if (cfg_ext_write_byte_enable[2])
                            current_value[23:16] = (cfg_ext_write_data[23:16] & overlay_mask[23:16]) | 
                                                  (current_value[23:16] & ~overlay_mask[23:16]);
                        if (cfg_ext_write_byte_enable[3])
                            current_value[31:24] = (cfg_ext_write_data[31:24] & overlay_mask[31:24]) | 
                                                  (current_value[31:24] & ~overlay_mask[31:24]);
                        
                        overlay_ram[overlay_idx] <= current_value;
                    end
                    
                    cfg_state <= CFG_COMPLETE;
                end
                
                CFG_COMPLETE: begin
                    read_data_valid <= 1'b0;
                    cfg_state <= CFG_IDLE;
                end
                
                default: cfg_state <= CFG_IDLE;
            endcase
        end
    end
    
    // Output assignments
    assign cfg_ext_read_data = read_data;
    assign cfg_ext_read_data_valid = read_data_valid;
    
    // Host access port (Port B)
    always_ff @(posedge clk) begin
        if (host_access_en) begin
            if (host_write_en) begin
                // Host write to configuration space
                config_space_ram[host_addr[11:2]] <= host_write_data;
            end else begin
                // Host read from configuration space
                host_read_data <= config_space_ram[host_addr[11:2]];
                
                // Check if this register has an overlay entry
                int overlay_idx = get_overlay_index(host_addr[11:2]);
                if (overlay_idx >= 0) begin
                    // Apply overlay data for writable bits
                    logic [31:0] overlay_mask = get_overlay_mask(host_addr[11:2]);
                    host_read_data <= (config_space_ram[host_addr[11:2]] & ~overlay_mask) | 
                                     (overlay_ram[overlay_idx] & overlay_mask);
                end
            end
        end
    end
    
    // Initialize configuration space from file
    initial begin
        // Initialize the configuration space from a hex file
        $readmemh("config_space_init.hex", config_space_ram);
        
        // Initialize overlay RAM to zeros
        for (int i = 0; i < OVERLAY_ENTRIES; i++) begin
            overlay_ram[i] = 32'h0;
        end
    end

endmodule