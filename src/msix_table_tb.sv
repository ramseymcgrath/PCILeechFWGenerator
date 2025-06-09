//==============================================================================
// MSI-X Table Testbench
// 
// This testbench verifies the functionality of the MSI-X table and PBA implementation.
//==============================================================================

`timescale 1ns / 1ps

module msix_table_tb();

    // Parameters
    localparam NUM_MSIX = 8;
    localparam MSIX_TABLE_BIR = 0;
    localparam MSIX_TABLE_OFFSET = 32'h2000;
    localparam MSIX_PBA_BIR = 0;
    localparam MSIX_PBA_OFFSET = 32'h3000;
    
    // Clock and reset
    logic clk = 0;
    logic reset_n = 0;
    
    // BAR access interface
    logic [31:0] bar_addr;
    logic [2:0]  bar_index;
    logic [31:0] bar_wr_data;
    logic        bar_wr_en;
    logic [3:0]  bar_wr_be;
    logic        bar_rd_en;
    logic [31:0] bar_rd_data;
    logic        bar_access_match;
    
    // MSI-X control interface
    logic        msix_enable;
    logic        msix_function_mask;
    
    // Interrupt interface
    logic        msix_interrupt;
    logic [10:0] msix_vector;
    logic        msix_interrupt_ack;
    
    // Instantiate the MSI-X table module
    msix_table #(
        .NUM_MSIX(NUM_MSIX),
        .MSIX_TABLE_BIR(MSIX_TABLE_BIR),
        .MSIX_TABLE_OFFSET(MSIX_TABLE_OFFSET),
        .MSIX_PBA_BIR(MSIX_PBA_BIR),
        .MSIX_PBA_OFFSET(MSIX_PBA_OFFSET)
    ) dut (
        .clk(clk),
        .reset_n(reset_n),
        
        // BAR access interface
        .bar_addr(bar_addr),
        .bar_index(bar_index),
        .bar_wr_data(bar_wr_data),
        .bar_wr_en(bar_wr_en),
        .bar_wr_be(bar_wr_be),
        .bar_rd_en(bar_rd_en),
        .bar_rd_data(bar_rd_data),
        .bar_access_match(bar_access_match),
        
        // MSI-X control interface
        .msix_enable(msix_enable),
        .msix_function_mask(msix_function_mask),
        
        // Interrupt interface
        .msix_interrupt(msix_interrupt),
        .msix_vector(msix_vector),
        .msix_interrupt_ack(msix_interrupt_ack)
    );
    
    // Clock generation
    always #5 clk = ~clk;
    
    // Test sequence
    initial begin
        // Initialize signals
        bar_addr = 0;
        bar_index = 0;
        bar_wr_data = 0;
        bar_wr_en = 0;
        bar_wr_be = 4'b0000;
        bar_rd_en = 0;
        msix_enable = 0;
        msix_function_mask = 0;
        msix_interrupt_ack = 0;
        
        // Reset
        reset_n = 0;
        #20;
        reset_n = 1;
        #20;
        
        // Test 1: Write to MSI-X table entry 0
        $display("Test 1: Write to MSI-X table entry 0");
        
        // Write to address field (first DWORD of entry 0)
        bar_addr = MSIX_TABLE_OFFSET;
        bar_index = MSIX_TABLE_BIR;
        bar_wr_data = 32'hFEDCBA98;
        bar_wr_en = 1;
        bar_wr_be = 4'b1111;
        #10;
        bar_wr_en = 0;
        #10;
        
        // Write to data field (second DWORD of entry 0)
        bar_addr = MSIX_TABLE_OFFSET + 4;
        bar_wr_data = 32'h12345678;
        bar_wr_en = 1;
        #10;
        bar_wr_en = 0;
        #10;
        
        // Write to control field (third DWORD of entry 0)
        // Bit 0 = vector mask (0 = not masked)
        bar_addr = MSIX_TABLE_OFFSET + 8;
        bar_wr_data = 32'h00000000;
        bar_wr_en = 1;
        #10;
        bar_wr_en = 0;
        #10;
        
        // Test 2: Read from MSI-X table entry 0
        $display("Test 2: Read from MSI-X table entry 0");
        
        // Read address field
        bar_addr = MSIX_TABLE_OFFSET;
        bar_rd_en = 1;
        #10;
        if (bar_rd_data === 32'hFEDCBA98)
            $display("PASS: Address field read correctly");
        else
            $display("FAIL: Address field read incorrect. Expected 0xFEDCBA98, got 0x%h", bar_rd_data);
        bar_rd_en = 0;
        #10;
        
        // Read data field
        bar_addr = MSIX_TABLE_OFFSET + 4;
        bar_rd_en = 1;
        #10;
        if (bar_rd_data === 32'h12345678)
            $display("PASS: Data field read correctly");
        else
            $display("FAIL: Data field read incorrect. Expected 0x12345678, got 0x%h", bar_rd_data);
        bar_rd_en = 0;
        #10;
        
        // Read control field
        bar_addr = MSIX_TABLE_OFFSET + 8;
        bar_rd_en = 1;
        #10;
        if (bar_rd_data === 32'h00000000)
            $display("PASS: Control field read correctly");
        else
            $display("FAIL: Control field read incorrect. Expected 0x00000000, got 0x%h", bar_rd_data);
        bar_rd_en = 0;
        #10;
        
        // Test 3: Trigger an interrupt
        $display("Test 3: Trigger an interrupt");
        
        // Enable MSI-X
        msix_enable = 1;
        #10;
        
        // Trigger interrupt for vector 0
        dut.trigger_interrupt(0);
        #20;
        
        // Check if interrupt was triggered
        if (msix_interrupt === 1'b1)
            $display("PASS: Interrupt triggered");
        else
            $display("FAIL: Interrupt not triggered");
            
        // Acknowledge the interrupt
        msix_interrupt_ack = 1;
        #10;
        msix_interrupt_ack = 0;
        #10;
        
        // Check if interrupt was cleared
        if (msix_interrupt === 1'b0)
            $display("PASS: Interrupt cleared after acknowledgment");
        else
            $display("FAIL: Interrupt not cleared after acknowledgment");
        
        // Test 4: Test vector masking
        $display("Test 4: Test vector masking");
        
        // Mask vector 0
        bar_addr = MSIX_TABLE_OFFSET + 8;
        bar_wr_data = 32'h00000001;  // Set mask bit
        bar_wr_en = 1;
        #10;
        bar_wr_en = 0;
        #10;
        
        // Trigger interrupt for vector 0 (should not generate interrupt)
        dut.trigger_interrupt(0);
        #20;
        
        // Check if interrupt was not triggered (should be masked)
        if (msix_interrupt === 1'b0)
            $display("PASS: Masked interrupt not triggered");
        else
            $display("FAIL: Masked interrupt was triggered");
            
        // Check if pending bit was set in PBA
        bar_addr = MSIX_PBA_OFFSET;
        bar_rd_en = 1;
        #10;
        if (bar_rd_data & 32'h00000001)
            $display("PASS: Pending bit set in PBA");
        else
            $display("FAIL: Pending bit not set in PBA");
        bar_rd_en = 0;
        #10;
        
        // Test 5: Test function masking
        $display("Test 5: Test function masking");
        
        // Unmask vector 0
        bar_addr = MSIX_TABLE_OFFSET + 8;
        bar_wr_data = 32'h00000000;  // Clear mask bit
        bar_wr_en = 1;
        #10;
        bar_wr_en = 0;
        #10;
        
        // Set function mask
        msix_function_mask = 1;
        #10;
        
        // Trigger interrupt for vector 0 (should not generate interrupt due to function mask)
        dut.trigger_interrupt(0);
        #20;
        
        // Check if interrupt was not triggered (should be masked by function mask)
        if (msix_interrupt === 1'b0)
            $display("PASS: Function-masked interrupt not triggered");
        else
            $display("FAIL: Function-masked interrupt was triggered");
            
        // Check if pending bit was set in PBA
        bar_addr = MSIX_PBA_OFFSET;
        bar_rd_en = 1;
        #10;
        if (bar_rd_data & 32'h00000001)
            $display("PASS: Pending bit set in PBA for function-masked interrupt");
        else
            $display("FAIL: Pending bit not set in PBA for function-masked interrupt");
        bar_rd_en = 0;
        #10;
        
        // End simulation
        $display("All tests completed");
        #100;
        $finish;
    end

endmodule