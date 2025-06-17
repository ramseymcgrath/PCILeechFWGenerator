//==============================================================================
// MSI-X Table Testbench
// Test file for PCILeech MSI-X Table template validation
//==============================================================================

`timescale 1ns / 1ps

module test_msix_table();

    // Clock and reset
    logic clk = 0;
    logic reset_n = 0;
    
    // BAR access interface
    logic [31:0] bar_addr = 32'h0;
    logic [2:0]  bar_index = 3'h0;
    logic [31:0] bar_wr_data = 32'h0;
    logic        bar_wr_en = 1'b0;
    logic [3:0]  bar_wr_be = 4'h0;
    logic        bar_rd_en = 1'b0;
    logic [31:0] bar_rd_data;
    logic        bar_access_match;
    
    // MSI-X control interface
    logic        msix_enable = 1'b1;
    logic        msix_function_mask = 1'b0;
    
    // Interrupt interface
    logic        msix_interrupt;
    logic [10:0] msix_vector;
    logic        msix_interrupt_ack = 1'b0;
    
    // Clock generation
    always #5 clk = ~clk;
    
    // DUT instantiation (would be generated from template)
    // This is a placeholder for template-generated module
    
    // Test sequence
    initial begin
        $display("Starting MSI-X Table test...");
        
        // Reset sequence
        #10 reset_n = 1'b1;
        #20;
        
        // Test MSI-X table write (vector 0, message address low)
        bar_index = 3'h0;  // Assuming MSI-X table is in BAR 0
        bar_addr = 32'h0000;  // Vector 0, DWORD 0 (message address low)
        bar_wr_data = 32'hFEE00000;  // Typical MSI address
        bar_wr_be = 4'hF;
        bar_wr_en = 1'b1;
        #10 bar_wr_en = 1'b0;
        
        // Write message address high
        bar_addr = 32'h0004;  // Vector 0, DWORD 1 (message address high)
        bar_wr_data = 32'h00000000;
        bar_wr_en = 1'b1;
        #10 bar_wr_en = 1'b0;
        
        // Write message data
        bar_addr = 32'h0008;  // Vector 0, DWORD 2 (message data)
        bar_wr_data = 32'h12345678;
        bar_wr_en = 1'b1;
        #10 bar_wr_en = 1'b0;
        
        // Write vector control (unmask)
        bar_addr = 32'h000C;  // Vector 0, DWORD 3 (vector control)
        bar_wr_data = 32'h00000000;  // Unmasked
        bar_wr_en = 1'b1;
        #10 bar_wr_en = 1'b0;
        
        // Test MSI-X table read
        bar_addr = 32'h0000;
        bar_rd_en = 1'b1;
        #10 bar_rd_en = 1'b0;
        
        // Test PBA access
        bar_addr = 32'h1000;  // Assuming PBA at offset 0x1000
        bar_rd_en = 1'b1;
        #10 bar_rd_en = 1'b0;
        
        // Simulate interrupt trigger (would normally come from DUT task)
        // This would test the interrupt delivery state machine
        
        // Test interrupt acknowledgment
        #50;
        if (msix_interrupt) begin
            $display("MSI-X interrupt detected, acknowledging...");
            msix_interrupt_ack = 1'b1;
            #10 msix_interrupt_ack = 1'b0;
        end
        
        #100;
        $display("MSI-X Table test completed");
        $finish;
    end
    
    // Monitor outputs
    always @(posedge clk) begin
        if (bar_access_match && bar_rd_en)
            $display("Time %0t: MSI-X read addr=0x%08x data=0x%08x", 
                    $time, bar_addr, bar_rd_data);
        if (msix_interrupt)
            $display("Time %0t: MSI-X interrupt vector=%0d", $time, msix_vector);
    end

endmodule