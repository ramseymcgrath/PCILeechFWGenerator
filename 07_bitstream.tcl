# PCILeech Bitstream Generation Script
# Simple bitstream generation without redundant steps

puts "Generating bitstream..."

# Generate bitstream with force flag for safe rerun
write_bitstream -force pcileech_top.bit

puts "Bitstream generation completed successfully"
puts "Output file: pcileech_top.bit"