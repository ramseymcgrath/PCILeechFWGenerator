//==============================================================================
// Option ROM BAR Window Testbench
// Test file for PCILeech Option ROM BAR Window template validation
//==============================================================================

`timescale 1ns / 1ps

module test_option_rom_bar_window();

    // Clock and reset
    logic clk = 0;
    logic reset_n = 0;
    
    // PCIe BAR interface
    logic [31:0] bar_addr = 32'h0;
    logic [31:0] bar_wr_data = 32'h0;
    logic        bar_wr_en = 1'b0;
    logic        bar_rd_en = 1'b0;
    logic [31:0] bar_rd_data;
    logic [2:0]  bar_index = 3'h5;  // Default ROM BAR
    logic        bar_access_match;
    
    // PCIe configuration space interface
    logic        cfg_ext_read_received = 1'b0;
    logic        cfg_ext_write_received = 1'b0;
    logic [9:0]  cfg_ext_register_number = 10'h0;
    logic [3:0]  cfg_ext_function_number = 4'h0;
    logic [31:0] cfg_ext_write_data = 32'h0;
    logic [3:0]  cfg_ext_write_byte_enable = 4'h0;
    
    // Legacy ROM access interface
    logic        legacy_rom_access = 1'b0;
    logic [31:0] legacy_rom_addr = 32'h0;
    logic [31:0] legacy_rom_data;
    
    // Clock generation
    always #5 clk = ~clk;
    
    // DUT instantiation (would be generated from template)
    // This is a placeholder for template-generated module
    
    // Test sequence
    initial begin
        $display("Starting Option ROM BAR Window test...");
        
        // Reset sequence
        #10 reset_n = 1'b1;
        #20;
        
        // Test ROM signature read (first DWORD should contain 0x55AA)
        bar_addr = 32'h0000;
        bar_rd_en = 1'b1;
        #10 bar_rd_en = 1'b0;
        #10;
        
        if (bar_access_match) begin
            $display("ROM signature read: 0x%08x", bar_rd_data);
            if ((bar_rd_data & 16'hFFFF) == 16'hAA55) begin
                $display("Valid ROM signature detected");
            end else begin
                $display("Warning: Invalid ROM signature");
            end
        end
        
        // Test sequential ROM reads
        for (int i = 0; i < 16; i++) begin
            bar_addr = i * 4;
            bar_rd_en = 1'b1;
            #10 bar_rd_en = 1'b0;
            #10;
            if (bar_access_match) begin
                $display("ROM[0x%04x] = 0x%08x", bar_addr, bar_rd_data);
            end
        end
        
        // Test ROM write (if enabled)
        bar_addr = 32'h0100;
        bar_wr_data = 32'hDEADBEEF;
        bar_wr_en = 1'b1;
        #10 bar_wr_en = 1'b0;
        
        // Read back written data
        #10 bar_rd_en = 1'b1;
        #10 bar_rd_en = 1'b0;
        #10;
        
        if (bar_access_match && bar_rd_data == 32'hDEADBEEF) begin
            $display("ROM write/read test passed");
        end else begin
            $display("ROM write/read test failed or writes disabled");
        end
        
        // Test legacy ROM access
        legacy_rom_addr = 32'h0000;
        legacy_rom_access = 1'b1;
        #10 legacy_rom_access = 1'b0;
        #10;
        $display("Legacy ROM access: addr=0x%08x data=0x%08x", 
                legacy_rom_addr, legacy_rom_data);
        
        // Test out-of-range access
        bar_addr = 32'hFFFF0;  // Beyond ROM size
        bar_rd_en = 1'b1;
        #10 bar_rd_en = 1'b0;
        #10;
        
        if (bar_access_match) begin
            $display("Out-of-range access returned: 0x%08x", bar_rd_data);
        end else begin
            $display("Out-of-range access correctly rejected");
        end
        
        #100;
        $display("Option ROM BAR Window test completed");
        $finish;
    end
    
    // Monitor bar_access_match
    always @(posedge clk) begin
        if (bar_access_match && (bar_rd_en || bar_wr_en)) begin
            $display("Time %0t: BAR access match - addr=0x%08x", $time, bar_addr);
        end
    end

endmodule