# PCILeech Implementation Script
# Handles opt_design, place_design, and route_design with proper checkpoints and reports

puts "Starting implementation flow..."

# Ensure we're in batch mode
set_param general.maxThreads 8

# Open synthesis run
open_run synth_1

# Optimization
puts "Running opt_design..."
if {[catch {opt_design} result]} {
    puts "ERROR: opt_design failed: $result"
    exit 1
}
write_checkpoint -force post_opt.dcp
report_utilization -file post_opt_utilization.rpt
report_timing_summary -file post_opt_timing.rpt

# Placement
puts "Running place_design..."
if {[catch {place_design} result]} {
    puts "ERROR: place_design failed: $result"
    exit 1
}
write_checkpoint -force post_place.dcp
report_utilization -file post_place_utilization.rpt
report_timing_summary -file post_place_timing.rpt

# Routing
puts "Running route_design..."
if {[catch {route_design} result]} {
    puts "ERROR: route_design failed: $result"
    exit 1
}
write_checkpoint -force post_route.dcp
report_utilization -file post_route_utilization.rpt
report_timing_summary -file post_route_timing.rpt
report_drc -file post_route_drc.rpt

puts "Implementation completed successfully"