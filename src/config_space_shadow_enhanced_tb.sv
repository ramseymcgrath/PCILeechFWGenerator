//==============================================================================
// Enhanced PCIe Configuration Space Shadow BRAM Testbench
//
// This enhanced testbench focuses on testing:
// 1. Extended configuration space access
// 2. Overlay RAM functionality for all writable fields
// 3. Edge cases and boundary conditions
//==============================================================================

`timescale 1ns / 1ps

module config_space_shadow_enhanced_tb;

    // Clock and reset
    logic clk;
    logic reset_n;
    
    // Port A - PCIe configuration access
    logic        cfg_ext_read_received;
    logic        cfg_ext_write_received;
    logic [9:0]  cfg_ext_register_number;
    logic [3:0]  cfg_ext_function_number;
    logic [31:0] cfg_ext_write_data;
    logic [3:0]  cfg_ext_write_byte_enable;
    logic [31:0] cfg_ext_read_data;
    logic        cfg_ext_read_data_valid;
    
    // Port B - Host access
    logic        host_access_en;
    logic        host_write_en;
    logic [11:0] host_addr;
    logic [31:0] host_write_data;
    logic [31:0] host_read_data;
    
    // Test status
    integer test_status = 0;
    integer error_count = 0;
    
    // Instantiate the Unit Under Test (UUT)
    config_space_shadow uut (
        .clk(clk),
        .reset_n(reset_n),
        
        // Port A
        .cfg_ext_read_received(cfg_ext_read_received),
        .cfg_ext_write_received(cfg_ext_write_received),
        .cfg_ext_register_number(cfg_ext_register_number),
        .cfg_ext_function_number(cfg_ext_function_number),
        .cfg_ext_write_data(cfg_ext_write_data),
        .cfg_ext_write_byte_enable(cfg_ext_write_byte_enable),
        .cfg_ext_read_data(cfg_ext_read_data),
        .cfg_ext_read_data_valid(cfg_ext_read_data_valid),
        
        // Port B
        .host_access_en(host_access_en),
        .host_write_en(host_write_en),
        .host_addr(host_addr),
        .host_write_data(host_write_data),
        .host_read_data(host_read_data)
    );
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 100 MHz clock
    end
    
    // Helper task for PCIe reads
    task pcie_read;
        input [9:0] reg_num;
        input [3:0] func_num;
        output [31:0] data;
        begin
            cfg_ext_read_received = 1;
            cfg_ext_register_number = reg_num;
            cfg_ext_function_number = func_num;
            @(posedge clk);
            cfg_ext_read_received = 0;
            @(posedge clk);
            while (!cfg_ext_read_data_valid) @(posedge clk);
            data = cfg_ext_read_data;
            @(posedge clk);
        end
    endtask
    
    // Helper task for PCIe writes
    task pcie_write;
        input [9:0] reg_num;
        input [3:0] func_num;
        input [31:0] data;
        input [3:0] byte_enable;
        begin
            cfg_ext_write_received = 1;
            cfg_ext_register_number = reg_num;
            cfg_ext_function_number = func_num;
            cfg_ext_write_data = data;
            cfg_ext_write_byte_enable = byte_enable;
            @(posedge clk);
            cfg_ext_write_received = 0;
            @(posedge clk);
            @(posedge clk);
        end
    endtask
    
    // Helper task for host reads
    task host_read;
        input [11:0] addr;
        output [31:0] data;
        begin
            host_access_en = 1;
            host_write_en = 0;
            host_addr = addr;
            @(posedge clk);
            data = host_read_data;
            host_access_en = 0;
            @(posedge clk);
        end
    endtask
    
    // Helper task for host writes
    task host_write;
        input [11:0] addr;
        input [31:0] data;
        begin
            host_access_en = 1;
            host_write_en = 1;
            host_addr = addr;
            host_write_data = data;
            @(posedge clk);
            host_access_en = 0;
            host_write_en = 0;
            @(posedge clk);
        end
    endtask
    
    // Test sequence
    initial begin
        // Initialize signals
        reset_n = 0;
        cfg_ext_read_received = 0;
        cfg_ext_write_received = 0;
        cfg_ext_register_number = 0;
        cfg_ext_function_number = 0;
        cfg_ext_write_data = 0;
        cfg_ext_write_byte_enable = 0;
        host_access_en = 0;
        host_write_en = 0;
        host_addr = 0;
        host_write_data = 0;
        
        // Apply reset
        #20;
        reset_n = 1;
        #20;
        
        //=======================================================================
        // Test 1: Extended Configuration Space Access
        //=======================================================================
        $display("Test 1: Extended Configuration Space Access");
        test_status = 1;
        
        // Write to extended configuration space (offset 0x100)
        host_write(12'h100, 32'h12345678);
        
        // Read back from extended configuration space
        logic [31:0] read_data;
        host_read(12'h100, read_data);
        
        // Verify data
        if (read_data !== 32'h12345678) begin
            $display("ERROR: Extended config space read mismatch. Expected: %h, Got: %h", 32'h12345678, read_data);
            error_count++;
        end else begin
            $display("PASS: Extended config space read matched");
        end
        
        // Write to last DWORD in configuration space (offset 0xFFC)
        host_write(12'hFFC, 32'hABCDEF01);
        
        // Read back from last DWORD
        host_read(12'hFFC, read_data);
        
        // Verify data
        if (read_data !== 32'hABCDEF01) begin
            $display("ERROR: Last DWORD read mismatch. Expected: %h, Got: %h", 32'hABCDEF01, read_data);
            error_count++;
        end else begin
            $display("PASS: Last DWORD read matched");
        end
        
        // Access via PCIe interface
        pcie_read(10'h040, 4'h0, read_data); // 0x100 / 4 = 0x40
        
        // Verify data
        if (read_data !== 32'h12345678) begin
            $display("ERROR: PCIe extended config space read mismatch. Expected: %h, Got: %h", 32'h12345678, read_data);
            error_count++;
        end else begin
            $display("PASS: PCIe extended config space read matched");
        end
        
        //=======================================================================
        // Test 2: Overlay RAM Functionality for All Writable Fields
        //=======================================================================
        $display("\nTest 2: Overlay RAM Functionality for All Writable Fields");
        test_status = 2;
        
        // Test Command Register (offset 0x04, register number 0x001)
        // First, initialize with a known value via host interface
        host_write(12'h004, 32'h00000000);
        
        // Read initial value via PCIe
        pcie_read(10'h001, 4'h0, read_data);
        $display("Initial Command Register: %h", read_data);
        
        // Write to Command Register via PCIe
        pcie_write(10'h001, 4'h0, 32'h00000147, 4'hF);
        
        // Read back via PCIe
        pcie_read(10'h001, 4'h0, read_data);
        
        // Verify data
        if ((read_data & 16'hFFFF) !== 16'h0147) begin
            $display("ERROR: Command register write failed. Expected: %h, Got: %h", 16'h0147, read_data & 16'hFFFF);
            error_count++;
        end else begin
            $display("PASS: Command register write successful");
        end
        
        // Read back via host interface
        host_read(12'h004, read_data);
        
        // Verify data (should include overlay)
        if ((read_data & 16'hFFFF) !== 16'h0147) begin
            $display("ERROR: Host read of command register failed. Expected: %h, Got: %h", 16'h0147, read_data & 16'hFFFF);
            error_count++;
        end else begin
            $display("PASS: Host read of command register successful");
        end
        
        // Test Status Register (offset 0x06, part of register number 0x001)
        // Write to Status Register via PCIe (only certain bits are writable)
        // Status register is in the upper 16 bits of the same DWORD as Command
        pcie_write(10'h001, 4'h0, 32'h02900000, 4'hF);
        
        // Read back via PCIe
        pcie_read(10'h001, 4'h0, read_data);
        
        // Verify data - only certain bits should be set
        // Bits that can be cleared by writing 1: 3, 5, 8, 9, 10, 11, 14, 15
        // 0x2900 = 0010 1001 0000 0000
        if ((read_data >> 16) !== 16'h0290) begin
            $display("ERROR: Status register write failed. Expected: %h, Got: %h", 16'h0290, read_data >> 16);
            error_count++;
        end else begin
            $display("PASS: Status register write successful");
        end
        
        // Test Cache Line Size Register (offset 0x0C, register number 0x003)
        // Write to Cache Line Size Register via PCIe
        pcie_write(10'h003, 4'h0, 32'h00000040, 4'h1); // Only byte 0 enabled
        
        // Read back via PCIe
        pcie_read(10'h003, 4'h0, read_data);
        
        // Verify data
        if ((read_data & 8'hFF) !== 8'h40) begin
            $display("ERROR: Cache Line Size register write failed. Expected: %h, Got: %h", 8'h40, read_data & 8'hFF);
            error_count++;
        end else begin
            $display("PASS: Cache Line Size register write successful");
        end
        
        // Test Latency Timer Register (offset 0x0D, part of register number 0x003)
        // Write to Latency Timer Register via PCIe
        pcie_write(10'h003, 4'h0, 32'h00002000, 4'h2); // Only byte 1 enabled
        
        // Read back via PCIe
        pcie_read(10'h003, 4'h0, read_data);
        
        // Verify data
        if (((read_data >> 8) & 8'hFF) !== 8'h20) begin
            $display("ERROR: Latency Timer register write failed. Expected: %h, Got: %h", 8'h20, (read_data >> 8) & 8'hFF);
            error_count++;
        end else begin
            $display("PASS: Latency Timer register write successful");
        end
        
        //=======================================================================
        // Test 3: Byte Enable Functionality
        //=======================================================================
        $display("\nTest 3: Byte Enable Functionality");
        test_status = 3;
        
        // Initialize Command Register with known value
        host_write(12'h004, 32'h00000000);
        
        // Write to Command Register with specific byte enables
        pcie_write(10'h001, 4'h0, 32'h11223344, 4'h5); // Only bytes 0 and 2 enabled
        
        // Read back via PCIe
        pcie_read(10'h001, 4'h0, read_data);
        
        // Verify data - only bytes 0 and 2 should be updated
        // Expected: 0x00220044
        if ((read_data & 16'hFFFF) !== 16'h0044) begin
            $display("ERROR: Byte enable test failed. Expected: %h, Got: %h", 16'h0044, read_data & 16'hFFFF);
            error_count++;
        end else begin
            $display("PASS: Byte enable test successful");
        }
        
        //=======================================================================
        // Test 4: Edge Cases and Boundary Conditions
        //=======================================================================
        $display("\nTest 4: Edge Cases and Boundary Conditions");
        test_status = 4;
        
        // Test access to non-existent function number
        pcie_read(10'h001, 4'hF, read_data); // Function 15 (likely doesn't exist)
        
        // Should still return data (implementation dependent)
        $display("Read from non-existent function: %h", read_data);
        
        // Test access to register number beyond valid range
        pcie_read(10'h3FF, 4'h0, read_data); // Register 0x3FF (beyond 4KB space)
        
        // Should return data from the last valid register
        $display("Read from beyond valid range: %h", read_data);
        
        // Test simultaneous access from both ports
        fork
            begin
                pcie_write(10'h001, 4'h0, 32'hAAAAAAAA, 4'hF);
            end
            begin
                host_write(12'h004, 32'hBBBBBBBB);
            end
        join
        
        // Read back to see which one took effect (implementation dependent)
        pcie_read(10'h001, 4'h0, read_data);
        $display("After simultaneous access: %h", read_data);
        
        //=======================================================================
        // Test 5: Multiple Consecutive Accesses
        //=======================================================================
        $display("\nTest 5: Multiple Consecutive Accesses");
        test_status = 5;
        
        // Perform multiple consecutive PCIe reads
        for (int i = 0; i < 10; i++) begin
            pcie_read(10'h001 + i, 4'h0, read_data);
            $display("Consecutive read %0d: %h", i, read_data);
        end
        
        // Perform multiple consecutive PCIe writes
        for (int i = 0; i < 5; i++) begin
            pcie_write(10'h001 + i, 4'h0, 32'h12345670 + i, 4'hF);
        end
        
        // Read back to verify
        for (int i = 0; i < 5; i++) begin
            pcie_read(10'h001 + i, 4'h0, read_data);
            if ((i == 0 && (read_data & 16'hFFFF) !== 16'h5670) || 
                (i > 0 && read_data !== 32'h12345670 + i)) begin
                $display("ERROR: Consecutive write/read %0d failed. Expected: %h, Got: %h", 
                         i, 32'h12345670 + i, read_data);
                error_count++;
            end else begin
                $display("PASS: Consecutive write/read %0d successful", i);
            end
        end
        
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
        if (cfg_ext_read_data_valid) begin
            $display("Time %t: Valid read data: %h", $time, cfg_ext_read_data);
        end
    end

endmodule