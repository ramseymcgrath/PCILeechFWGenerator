//==============================================================================
// Option ROM SPI Flash Testbench
// Test file for PCILeech Option ROM SPI Flash template validation
//==============================================================================

`timescale 1ns / 1ps

module test_option_rom_spi_flash();

    // Clock and reset
    logic clk = 0;
    logic reset_n = 0;
    
    // PCIe Expansion-ROM interface
    logic        exp_rom_access = 1'b0;
    logic [31:0] exp_rom_addr = 32'h0;
    logic [31:0] exp_rom_data;
    logic        exp_rom_data_valid;
    
    // Legacy ROM access interface
    logic        legacy_rom_access = 1'b0;
    logic [31:0] legacy_rom_addr = 32'h0;
    logic [31:0] legacy_rom_data;
    
    // SPI Flash interface
    logic        spi_cs_n;
    logic        spi_clk;
    logic        spi_mosi;
    logic        spi_miso = 1'b0;
    
    // QSPI Flash interface (optional)
    logic        qspi_cs_n;
    logic        qspi_clk;
    logic [3:0]  qspi_dq_o;
    logic [3:0]  qspi_dq_i = 4'h0;
    logic [3:0]  qspi_dq_oe;
    
    // Clock generation
    always #5 clk = ~clk;
    
    // Simple SPI flash model
    logic [7:0] flash_memory [0:65535];  // 64KB flash
    logic [31:0] flash_addr_reg;
    logic [7:0] flash_cmd_reg;
    logic [3:0] flash_state;
    logic [7:0] flash_bit_count;
    
    // Initialize flash memory with test pattern
    initial begin
        // ROM signature
        flash_memory[0] = 8'h55;
        flash_memory[1] = 8'hAA;
        flash_memory[2] = 8'h00;
        flash_memory[3] = 8'h00;
        
        // Test pattern
        for (int i = 4; i < 1024; i++) begin
            flash_memory[i] = i[7:0];
        end
    end
    
    // Simple SPI flash behavior model
    always @(posedge spi_clk or posedge spi_cs_n) begin
        if (spi_cs_n) begin
            flash_state <= 0;
            flash_bit_count <= 0;
        end else begin
            case (flash_state)
                0: begin // Command phase
                    flash_cmd_reg <= {flash_cmd_reg[6:0], spi_mosi};
                    flash_bit_count <= flash_bit_count + 1;
                    if (flash_bit_count == 7) begin
                        flash_state <= 1;
                        flash_bit_count <= 0;
                    end
                end
                1, 2, 3: begin // Address phase (3 bytes)
                    flash_addr_reg <= {flash_addr_reg[30:0], spi_mosi};
                    flash_bit_count <= flash_bit_count + 1;
                    if (flash_bit_count == 7) begin
                        flash_state <= flash_state + 1;
                        flash_bit_count <= 0;
                    end
                end
                4: begin // Dummy cycles (for fast read)
                    flash_bit_count <= flash_bit_count + 1;
                    if (flash_bit_count == 7) begin
                        flash_state <= 5;
                        flash_bit_count <= 0;
                    end
                end
                5: begin // Data phase
                    flash_bit_count <= flash_bit_count + 1;
                    if (flash_bit_count == 7) begin
                        flash_addr_reg <= flash_addr_reg + 1;
                        flash_bit_count <= 0;
                    end
                end
            endcase
        end
    end
    
    // SPI MISO data output
    always @(negedge spi_clk) begin
        if (!spi_cs_n && flash_state == 5) begin
            spi_miso <= flash_memory[flash_addr_reg][7 - flash_bit_count];
        end
    end
    
    // DUT instantiation (would be generated from template)
    // This is a placeholder for template-generated module
    
    // Test sequence
    initial begin
        $display("Starting Option ROM SPI Flash test...");
        
        // Reset sequence
        #10 reset_n = 1'b1;
        #20;
        
        // Test ROM signature read
        exp_rom_addr = 32'h00000000;
        exp_rom_access = 1'b1;
        #10 exp_rom_access = 1'b0;
        
        // Wait for SPI transaction to complete
        wait(exp_rom_data_valid);
        #10;
        
        $display("ROM signature read: 0x%08x", exp_rom_data);
        if ((exp_rom_data & 16'hFFFF) == 16'hAA55) begin
            $display("Valid ROM signature detected");
        end else begin
            $display("Warning: Invalid ROM signature");
        end
        
        // Test sequential reads (should hit cache on subsequent accesses)
        for (int i = 1; i < 8; i++) begin
            exp_rom_addr = i * 4;
            exp_rom_access = 1'b1;
            #10 exp_rom_access = 1'b0;
            
            wait(exp_rom_data_valid);
            #10;
            $display("ROM[0x%04x] = 0x%08x", exp_rom_addr, exp_rom_data);
        end
        
        // Test cache hit (re-read first location)
        exp_rom_addr = 32'h00000000;
        exp_rom_access = 1'b1;
        #10 exp_rom_access = 1'b0;
        
        wait(exp_rom_data_valid);
        #10;
        $display("Cache hit test: ROM[0x0000] = 0x%08x", exp_rom_data);
        
        // Test legacy ROM access
        legacy_rom_addr = 32'h00000004;
        legacy_rom_access = 1'b1;
        #10 legacy_rom_access = 1'b0;
        #10;
        $display("Legacy ROM access: addr=0x%08x data=0x%08x", 
                legacy_rom_addr, legacy_rom_data);
        
        #1000;
        $display("Option ROM SPI Flash test completed");
        $finish;
    end
    
    // Monitor SPI transactions
    always @(negedge spi_cs_n) begin
        $display("Time %0t: SPI transaction started", $time);
    end
    
    always @(posedge spi_cs_n) begin
        $display("Time %0t: SPI transaction completed", $time);
    end
    
    // Monitor data valid
    always @(posedge exp_rom_data_valid) begin
        $display("Time %0t: ROM data valid - addr=0x%08x data=0x%08x", 
                $time, exp_rom_addr, exp_rom_data);
    end

endmodule