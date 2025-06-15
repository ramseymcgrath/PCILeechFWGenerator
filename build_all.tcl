# PCILeech Master Build Script
# Sources all build scripts in correct order with proper sequencing

puts "Starting PCILeech firmware build process..."

# Set batch mode parameters
set_param general.maxThreads 8

# Source all build scripts in order
set build_scripts [list \
    "01_project_setup.tcl" \
    "02_ip_config.tcl" \
    "03_add_sources.tcl" \
    "04_constraints.tcl" \
    "05_synthesis.tcl" \
]

# Execute initial build stages
foreach script $build_scripts {
    if {[file exists $script]} {
        puts "Executing: $script"
        source $script
        puts "Completed: $script"
        puts ""
    } else {
        puts "ERROR: Required script not found: $script"
        exit 1
    }
}

# Explicitly open synthesis run before implementation
puts "Opening synthesis run..."
open_run synth_1

# Source implementation script
if {[file exists "06_implementation.tcl"]} {
    puts "Executing: 06_implementation.tcl"
    source 06_implementation.tcl
    puts "Completed: 06_implementation.tcl"
    puts ""
} else {
    puts "ERROR: Required script not found: 06_implementation.tcl"
    exit 1
}

# Source bitstream script
if {[file exists "07_bitstream.tcl"]} {
    puts "Executing: 07_bitstream.tcl"
    source 07_bitstream.tcl
    puts "Completed: 07_bitstream.tcl"
    puts ""
} else {
    puts "ERROR: Required script not found: 07_bitstream.tcl"
    exit 1
}

puts "Build process completed successfully!"