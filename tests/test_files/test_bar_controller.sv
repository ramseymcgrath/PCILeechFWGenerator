//==============================================================================
// BAR Controller Testbench
// Test file for PCILeech BAR Controller template validation
//==============================================================================

`timescale 1ns / 1ps

module test_bar_controller();

    // Clock and reset
    logic clk = 0;
    logic reset_n = 0;
    
    // BAR selector
    logic [2:0] bar_index = 3'h0;
    
    // PCIe BAR interface
    logic [31:0] bar_addr = 32'h0;
    logic [31:0] bar_wr_data = 32'h0;
    logic [3:0]  bar_wr_be = 4'h0;
    logic        bar_wr_en = 1'b0;
    logic        bar_rd_en = 1'b0;
    logic [31:0] bar_rd_data;
    
    // PCIe configuration space interface
    logic        cfg_ext_read_received = 1'b0;
    logic        cfg_ext_write_received = 1'b0;
    logic [9:0]  cfg_ext_register_number = 10'h0;
    logic [3:0]  cfg_ext_function_number = 4'h0;
    logic [31:0] cfg_ext_write_data = 32'h0;
    logic [3:0]  cfg_ext_write_byte_enable = 4'h0;
    logic [31:0] cfg_ext_read_data;
    logic        cfg_ext_read_data_valid;
    
    // MSI-X interrupt interface
    logic        msix_interrupt;
    logic [10:0] msix_vector;
    logic        msix_interrupt_ack = 1'b0;
    
    // Custom window hook
    logic        custom_win_sel;
    logic [11:0] custom_win_addr;
    logic [31:0] custom_win_wdata;
    logic [3:0]  custom_win_be;
    logic        custom_win_we;
    logic        custom_win_re;
    logic [31:0] custom_win_rdata = 32'hDEADBEEF;
    
    // Clock generation
    always #5 clk = ~clk;
    
    // DUT instantiation (would be generated from template)
    // This is a placeholder for template-generated module
    
    // Test sequence
    initial begin
        $display("Starting BAR Controller test...");
        
        // Reset sequence
        #10 reset_n = 1'b1;
        #20;
        
        // Test BAR memory access
        bar_addr = 32'h1000;
        bar_wr_data = 32'hDEADBEEF;
        bar_wr_be = 4'hF;
        bar_wr_en = 1'b1;
        #10 bar_wr_en = 1'b0;
        
        // Test BAR read
        #10 bar_rd_en = 1'b1;
        #10 bar_rd_en = 1'b0;
        
        // Test configuration space access
        cfg_ext_register_number = 10'h001;
        cfg_ext_write_data = 32'h12345678;
        cfg_ext_write_byte_enable = 4'hF;
        cfg_ext_write_received = 1'b1;
        #10 cfg_ext_write_received = 1'b0;
        
        #10 cfg_ext_read_received = 1'b1;
        #10 cfg_ext_read_received = 1'b0;
        
        #100;
        $display("BAR Controller test completed");
        $finish;
    end
    
    // Monitor outputs
    always @(posedge clk) begin
        if (bar_rd_data !== 32'hx)
            $display("Time %0t: BAR read data = 0x%08x", $time, bar_rd_data);
        if (cfg_ext_read_data_valid)
            $display("Time %0t: Config read data = 0x%08x", $time, cfg_ext_read_data);
        if (msix_interrupt)
            $display("Time %0t: MSI-X interrupt vector = %0d", $time, msix_vector);
    end

endmodule