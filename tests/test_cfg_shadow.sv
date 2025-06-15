//==============================================================================
// Configuration Space Shadow Testbench
// Test file for PCILeech Configuration Space Shadow template validation
//==============================================================================

`timescale 1ns / 1ps

module test_cfg_shadow();

    // Clock and reset
    logic clk = 0;
    logic reset_n = 0;
    
    // Port A - PCIe configuration access
    logic        cfg_ext_read_received = 1'b0;
    logic        cfg_ext_write_received = 1'b0;
    logic [9:0]  cfg_ext_register_number = 10'h0;
    logic [3:0]  cfg_ext_function_number = 4'h0;
    logic [31:0] cfg_ext_write_data = 32'h0;
    logic [3:0]  cfg_ext_write_byte_enable = 4'h0;
    logic [31:0] cfg_ext_read_data;
    logic        cfg_ext_read_data_valid;
    
    // Port B - Host access
    logic        host_access_en = 1'b0;
    logic        host_write_en = 1'b0;
    logic [11:0] host_addr = 12'h0;
    logic [31:0] host_write_data = 32'h0;
    logic [31:0] host_read_data;
    
    // Clock generation
    always #5 clk = ~clk;
    
    // DUT instantiation (would be generated from template)
    // This is a placeholder for template-generated module
    
    // Test sequence
    initial begin
        $display("Starting Configuration Space Shadow test...");
        
        // Reset sequence
        #10 reset_n = 1'b1;
        #20;
        
        // Test host write to configuration space
        host_addr = 12'h004;  // Command register
        host_write_data = 32'h12345678;
        host_access_en = 1'b1;
        host_write_en = 1'b1;
        #10 host_write_en = 1'b0;
        
        // Test host read
        #10 host_write_en = 1'b0;
        #10 host_access_en = 1'b0;
        
        // Test PCIe configuration write
        cfg_ext_register_number = 10'h001;  // Command register
        cfg_ext_write_data = 32'hABCDEF00;
        cfg_ext_write_byte_enable = 4'hF;
        cfg_ext_write_received = 1'b1;
        #10 cfg_ext_write_received = 1'b0;
        
        // Test PCIe configuration read
        #20 cfg_ext_read_received = 1'b1;
        #10 cfg_ext_read_received = 1'b0;
        
        // Test overlay functionality
        cfg_ext_register_number = 10'h002;  // Status register
        cfg_ext_write_data = 32'h55AA55AA;
        cfg_ext_write_byte_enable = 4'hF;
        cfg_ext_write_received = 1'b1;
        #10 cfg_ext_write_received = 1'b0;
        
        #20 cfg_ext_read_received = 1'b1;
        #10 cfg_ext_read_received = 1'b0;
        
        #100;
        $display("Configuration Space Shadow test completed");
        $finish;
    end
    
    // Monitor outputs
    always @(posedge clk) begin
        if (cfg_ext_read_data_valid)
            $display("Time %0t: Config read reg=0x%03x data=0x%08x", 
                    $time, cfg_ext_register_number, cfg_ext_read_data);
        if (host_access_en && !host_write_en)
            $display("Time %0t: Host read addr=0x%03x data=0x%08x", 
                    $time, host_addr, host_read_data);
    end

endmodule