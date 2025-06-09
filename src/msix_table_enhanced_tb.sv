//==============================================================================
// Enhanced MSI-X Table Testbench
// 
// This enhanced testbench focuses on testing:
// 1. MSI-X table with various table sizes
// 2. Interrupt delivery with different masking scenarios
// 3. PBA functionality
// 4. Edge cases and boundary conditions
//==============================================================================

`timescale 1ns / 1ps

module msix_table_enhanced_tb();

    // Parameters - configurable for different test scenarios
    parameter NUM_MSIX = 32;  // Larger table size for more thorough testing
    parameter MSIX_TABLE_BIR = 0;
    parameter MSIX_TABLE_OFFSET = 32'h2000;
    parameter MSIX_PBA_BIR = 0;
    parameter MSIX_PBA_OFFSET = 32'h3000;
    
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
    
    // Test status
    integer test_status = 0;
    integer error_count = 0;
    
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
    
    // Helper task for BAR reads
    task bar_read;
        input [31:0] addr;
        input [2:0] index;
        output [31:0] data;
        begin
            bar_addr = addr;
            bar_index = index;
            bar_rd_en = 1;
            @(posedge clk);
            data = bar_rd_data;
            bar_rd_en = 0;
            @(posedge clk);
        end
    endtask
    
    // Helper task for BAR writes
    task bar_write;
        input [31:0] addr;
        input [2:0] index;
        input [31:0] data;
        input [3:0] be;
        begin
            bar_addr = addr;
            bar_index = index;
            bar_wr_data = data;
            bar_wr_en = 1;
            bar_wr_be = be;
            @(posedge clk);
            bar_wr_en = 0;
            @(posedge clk);
        end
    endtask
    
    // Helper task to configure an MSI-X table entry
    task configure_msix_entry;
        input [10:0] entry_idx;
        input [31:0] addr_low;
        input [31:0] addr_high;
        input [31:0] data;
        input [31:0] control;
        begin
            // Calculate entry offset
            logic [31:0] entry_offset = MSIX_TABLE_OFFSET + (entry_idx * 16);
            
            // Write address low (first DWORD of entry)
            bar_write(entry_offset, MSIX_TABLE_BIR, addr_low, 4'b1111);
            
            // Write address high (second DWORD of entry)
            bar_write(entry_offset + 4, MSIX_TABLE_BIR, addr_high, 4'b1111);
            
            // Write data (third DWORD of entry)
            bar_write(entry_offset + 8, MSIX_TABLE_BIR, data, 4'b1111);
            
            // Write control (fourth DWORD of entry)
            bar_write(entry_offset + 12, MSIX_TABLE_BIR, control, 4'b1111);
        end
    endtask
    
    // Helper task to read an MSI-X table entry
    task read_msix_entry;
        input [10:0] entry_idx;
        output [31:0] addr_low;
        output [31:0] addr_high;
        output [31:0] data;
        output [31:0] control;
        begin
            // Calculate entry offset
            logic [31:0] entry_offset = MSIX_TABLE_OFFSET + (entry_idx * 16);
            
            // Read address low (first DWORD of entry)
            bar_read(entry_offset, MSIX_TABLE_BIR, addr_low);
            
            // Read address high (second DWORD of entry)
            bar_read(entry_offset + 4, MSIX_TABLE_BIR, addr_high);
            
            // Read data (third DWORD of entry)
            bar_read(entry_offset + 8, MSIX_TABLE_BIR, data);
            
            // Read control (fourth DWORD of entry)
            bar_read(entry_offset + 12, MSIX_TABLE_BIR, control);
        end
    endtask
    
    // Helper task to read a PBA DWORD
    task read_pba_dword;
        input [5:0] dword_idx;  // Up to 64 DWORDs for 2048 entries
        output [31:0] pba_data;
        begin
            // Calculate PBA offset
            logic [31:0] pba_offset = MSIX_PBA_OFFSET + (dword_idx * 4);
            
            // Read PBA DWORD
            bar_read(pba_offset, MSIX_PBA_BIR, pba_data);
        end
    endtask
    
    // Helper task to wait for and verify an interrupt
    task wait_for_interrupt;
        input [10:0] expected_vector;
        input int timeout_cycles;
        output bit success;
        begin
            success = 0;
            for (int i = 0; i < timeout_cycles; i++) begin
                if (msix_interrupt) begin
                    if (msix_vector === expected_vector) begin
                        success = 1;
                        $display("PASS: Interrupt received for vector %0d", expected_vector);
                    end else begin
                        $display("ERROR: Received interrupt for vector %0d, expected %0d", msix_vector, expected_vector);
                    end
                    break;
                end
                @(posedge clk);
            end
            
            if (!success && !msix_interrupt) begin
                $display("ERROR: No interrupt received for vector %0d within timeout", expected_vector);
            end
        end
    endtask
    
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
        
        //=======================================================================
        // Test 1: Configure and Verify Multiple MSI-X Table Entries
        //=======================================================================
        $display("Test 1: Configure and Verify Multiple MSI-X Table Entries");
        test_status = 1;
        
        // Configure multiple entries with different values
        for (int i = 0; i < 8; i++) begin
            configure_msix_entry(
                i,                      // Entry index
                32'hFEDC0000 + i*4,     // Address low
                32'h00000000 + i,       // Address high
                32'h12345670 + i,       // Data
                32'h00000000            // Control (not masked)
            );
        end
        
        // Verify entries
        logic [31:0] addr_low, addr_high, data, control;
        for (int i = 0; i < 8; i++) begin
            read_msix_entry(i, addr_low, addr_high, data, control);
            
            if (addr_low !== (32'hFEDC0000 + i*4) || 
                addr_high !== (32'h00000000 + i) || 
                data !== (32'h12345670 + i) || 
                control !== 32'h00000000) begin
                
                $display("ERROR: Entry %0d verification failed", i);
                $display("  Expected: %h, %h, %h, %h", 32'hFEDC0000 + i*4, 32'h00000000 + i, 32'h12345670 + i, 32'h00000000);
                $display("  Got: %h, %h, %h, %h", addr_low, addr_high, data, control);
                error_count++;
            end else begin
                $display("PASS: Entry %0d verification successful", i);
            end
        end
        
        //=======================================================================
        // Test 2: Test Byte-Enable Functionality
        //=======================================================================
        $display("\nTest 2: Test Byte-Enable Functionality");
        test_status = 2;
        
        // Write to entry 10 with specific byte enables
        logic [31:0] entry_offset = MSIX_TABLE_OFFSET + (10 * 16);
        
        // Write address low with only bytes 0 and 2 enabled
        bar_write(entry_offset, MSIX_TABLE_BIR, 32'h12345678, 4'b0101);
        
        // Read back
        bar_read(entry_offset, MSIX_TABLE_BIR, addr_low);
        
        // Only bytes 0 and 2 should be updated (assuming initial value was 0)
        if ((addr_low & 32'h0000FF00) !== 32'h00005600 || (addr_low & 32'h000000FF) !== 32'h00000078) begin
            $display("ERROR: Byte enable test failed. Expected bytes 0,2: 78,56, Got: %h", addr_low);
            error_count++;
        end else begin
            $display("PASS: Byte enable test successful");
        end
        
        //=======================================================================
        // Test 3: Test Interrupt Delivery with Different Masking Scenarios
        //=======================================================================
        $display("\nTest 3: Test Interrupt Delivery with Different Masking Scenarios");
        test_status = 3;
        
        // Enable MSI-X
        msix_enable = 1;
        
        // Configure entry 15 (not masked)
        configure_msix_entry(
            15,                     // Entry index
            32'hFEDCBA98,           // Address low
            32'h00000000,           // Address high
            32'h12345678,           // Data
            32'h00000000            // Control (not masked)
        );
        
        // Configure entry 16 (masked)
        configure_msix_entry(
            16,                     // Entry index
            32'hFEDCBA98,           // Address low
            32'h00000000,           // Address high
            32'h12345678,           // Data
            32'h00000001            // Control (masked)
        );
        
        // Trigger interrupt for entry 15 (should generate interrupt)
        dut.trigger_interrupt(15);
        #10;
        
        // Wait for and verify interrupt
        bit interrupt_success;
        wait_for_interrupt(15, 20, interrupt_success);
        
        if (!interrupt_success) begin
            error_count++;
        end
        
        // Acknowledge the interrupt
        msix_interrupt_ack = 1;
        #10;
        msix_interrupt_ack = 0;
        #10;
        
        // Trigger interrupt for entry 16 (should not generate interrupt due to masking)
        dut.trigger_interrupt(16);
        #20;
        
        if (msix_interrupt) begin
            $display("ERROR: Masked interrupt was triggered");
            error_count++;
        end else begin
            $display("PASS: Masked interrupt was not triggered");
        }
        
        // Check if pending bit was set in PBA for masked interrupt
        logic [31:0] pba_data;
        read_pba_dword(16 >> 5, pba_data);  // Entry 16 is in DWORD 0, bit 16
        
        if ((pba_data & (1 << (16 & 31))) === 0) begin
            $display("ERROR: Pending bit not set in PBA for masked interrupt");
            error_count++;
        end else begin
            $display("PASS: Pending bit set in PBA for masked interrupt");
        }
        
        //=======================================================================
        // Test 4: Test Function Masking
        //=======================================================================
        $display("\nTest 4: Test Function Masking");
        test_status = 4;
        
        // Enable MSI-X but set function mask
        msix_enable = 1;
        msix_function_mask = 1;
        
        // Configure entry 20 (not masked at entry level)
        configure_msix_entry(
            20,                     // Entry index
            32'hFEDCBA98,           // Address low
            32'h00000000,           // Address high
            32'h12345678,           // Data
            32'h00000000            // Control (not masked)
        );
        
        // Trigger interrupt for entry 20 (should not generate interrupt due to function mask)
        dut.trigger_interrupt(20);
        #20;
        
        if (msix_interrupt) begin
            $display("ERROR: Function-masked interrupt was triggered");
            error_count++;
        } else begin
            $display("PASS: Function-masked interrupt was not triggered");
        }
        
        // Check if pending bit was set in PBA
        read_pba_dword(20 >> 5, pba_data);  // Entry 20 is in DWORD 0, bit 20
        
        if ((pba_data & (1 << (20 & 31))) === 0) begin
            $display("ERROR: Pending bit not set in PBA for function-masked interrupt");
            error_count++;
        } else begin
            $display("PASS: Pending bit set in PBA for function-masked interrupt");
        }
        
        // Remove function mask and verify interrupt is now delivered
        msix_function_mask = 0;
        #20;
        
        wait_for_interrupt(20, 20, interrupt_success);
        
        if (!interrupt_success) begin
            error_count++;
        }
        
        // Acknowledge the interrupt
        msix_interrupt_ack = 1;
        #10;
        msix_interrupt_ack = 0;
        #10;
        
        //=======================================================================
        // Test 5: Test Multiple Pending Interrupts
        //=======================================================================
        $display("\nTest 5: Test Multiple Pending Interrupts");
        test_status = 5;
        
        // Enable MSI-X
        msix_enable = 1;
        msix_function_mask = 0;
        
        // Configure multiple entries
        for (int i = 24; i < 28; i++) begin
            configure_msix_entry(
                i,                      // Entry index
                32'hFEDC0000 + i*4,     // Address low
                32'h00000000,           // Address high
                32'h12345670 + i,       // Data
                32'h00000000            // Control (not masked)
            );
        end
        
        // Trigger multiple interrupts
        for (int i = 24; i < 28; i++) begin
            dut.trigger_interrupt(i);
        end
        
        // Verify first interrupt is delivered
        wait_for_interrupt(24, 20, interrupt_success);
        
        if (!interrupt_success) begin
            error_count++;
        }
        
        // Acknowledge the interrupt
        msix_interrupt_ack = 1;
        #10;
        msix_interrupt_ack = 0;
        #10;
        
        // Verify next interrupt is delivered
        wait_for_interrupt(25, 20, interrupt_success);
        
        if (!interrupt_success) begin
            error_count++;
        }
        
        // Acknowledge the interrupt
        msix_interrupt_ack = 1;
        #10;
        msix_interrupt_ack = 0;
        #10;
        
        // Continue for remaining interrupts
        for (int i = 26; i < 28; i++) begin
            wait_for_interrupt(i, 20, interrupt_success);
            
            if (!interrupt_success) begin
                error_count++;
            }
            
            // Acknowledge the interrupt
            msix_interrupt_ack = 1;
            #10;
            msix_interrupt_ack = 0;
            #10;
        end
        
        //=======================================================================
        // Test 6: Test PBA Functionality
        //=======================================================================
        $display("\nTest 6: Test PBA Functionality");
        test_status = 6;
        
        // Mask all entries to test PBA
        msix_function_mask = 1;
        
        // Clear any pending interrupts
        for (int i = 0; i < (NUM_MSIX + 31) / 32; i++) begin
            read_pba_dword(i, pba_data);
        end
        
        // Trigger interrupts for entries 0, 31, 32, and 63
        dut.trigger_interrupt(0);
        dut.trigger_interrupt(31);
        dut.trigger_interrupt(32);
        dut.trigger_interrupt(63);
        #10;
        
        // Read PBA and verify bits are set
        read_pba_dword(0, pba_data);
        if ((pba_data & 32'h80000001) !== 32'h80000001) begin
            $display("ERROR: PBA DWORD 0 incorrect. Expected bits 0,31 set, Got: %h", pba_data);
            error_count++;
        } else begin
            $display("PASS: PBA DWORD 0 correct with bits 0,31 set");
        }
        
        read_pba_dword(1, pba_data);
        if ((pba_data & 32'h80000001) !== 32'h80000001) begin
            $display("ERROR: PBA DWORD 1 incorrect. Expected bits 0,31 set, Got: %h", pba_data);
            error_count++;
        } else begin
            $display("PASS: PBA DWORD 1 correct with bits 0,31 set");
        }
        
        // End simulation
        #100;
        if (error_count == 0) begin
            $display("\nAll tests passed successfully!");
        end else begin
            $display("\nTests completed with %0d errors.", error_count);
        end
        $finish;
    end
    
    // Monitor for debugging
    always @(posedge clk) begin
        if (msix_interrupt) begin
            $display("Time %t: Interrupt for vector %0d", $time, msix_vector);
        end
    end

endmodule