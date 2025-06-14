# SystemVerilog Template Migration Plan

## Overview

This document outlines the comprehensive migration of SystemVerilog generation from string-based templates to Jinja2 templates. This migration will fix the current f-string syntax errors and provide a more maintainable, modular approach to SystemVerilog code generation.

## Current Issues

1. **Syntax Errors**: 53+ f-string syntax errors across multiple files
2. **Maintainability**: Hard-coded string templates mixed with logic
3. **Code Duplication**: Similar SystemVerilog patterns across files
4. **Error Prone**: Manual string formatting leads to syntax issues

## Migration Strategy

### Phase 1: Template Infrastructure
- Create `src/templates/systemverilog/` directory structure
- Enhance `template_renderer.py` with SystemVerilog-specific filters
- Add validation and formatting utilities

### Phase 2: Template Creation
- Extract all SystemVerilog templates from existing generators
- Create modular, reusable template components
- Implement proper Jinja2 syntax with escaping

### Phase 3: Generator Refactoring
- Completely refactor `systemverilog_generator.py`
- Completely refactor `advanced_sv_generator.py`
- Remove all string-based template code
- Implement template-based generation

## Template Structure

```
src/templates/systemverilog/
├── device_config.sv.j2              # Basic device configuration module
├── top_level_wrapper.sv.j2          # Top-level PCIe wrapper
├── advanced/
│   ├── power_management.sv.j2       # Power management state machine
│   ├── error_handling.sv.j2         # Error handling logic
│   ├── performance_counters.sv.j2   # Performance monitoring
│   ├── clock_domains.sv.j2          # Clock domain crossing
│   └── interrupt_handling.sv.j2     # MSI-X interrupt logic
├── components/
│   ├── register_declarations.sv.j2  # Register signal declarations
│   ├── register_logic.sv.j2         # Register read/write logic
│   └── device_specific.sv.j2        # Device-type specific logic
└── includes/
    ├── header.sv.j2                 # Standard SystemVerilog header
    ├── common_signals.sv.j2         # Common signal declarations
    └── utility_functions.sv.j2      # Utility function definitions
```

## Template Renderer Enhancements

### New SystemVerilog Filters

```python
# Hex formatting with proper width
def sv_hex(value, width=8):
    return f"{width}'h{value:0{width//4}X}"

# Signal width calculation
def sv_width(msb, lsb=0):
    if msb == lsb:
        return ""
    return f"[{msb}:{lsb}]"

# Module parameter formatting
def sv_param(name, value, width=None):
    if width:
        return f"parameter {name} = {sv_hex(value, width)}"
    return f"parameter {name} = {value}"

# Signal declaration formatting
def sv_signal(name, width=None, initial=None):
    width_str = f"[{width-1}:0] " if width and width > 1 else ""
    init_str = f" = {initial}" if initial is not None else ""
    return f"logic {width_str}{name}{init_str};"

# SystemVerilog identifier validation
def sv_identifier(name):
    # Ensure valid SystemVerilog identifier
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid SystemVerilog identifier: {name}")
    return name
```

### Template Context Structure

```python
# Device configuration context
device_context = {
    'vendor_id': '0x1234',
    'device_id': '0x5678',
    'class_code': '0x040300',
    'revision_id': '0x01',
    'bars': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000],
    'board': 'pcileech_35t325_x4',
    'registers': [
        {'name': 'control', 'offset': 0x00, 'value': '0x00000000'},
        {'name': 'status', 'offset': 0x04, 'value': '0x00000001'},
        # ... more registers
    ]
}

# Advanced features context
advanced_context = {
    'power_management': {
        'supported_states': ['D0', 'D1', 'D3_HOT'],
        'transition_cycles': {
            'd0_to_d1': 100,
            'd1_to_d0': 50,
            'd0_to_d3': 1000,
            'd3_to_d0': 10000
        }
    },
    'performance_counters': {
        'counter_width': 32,
        'enable_bandwidth': True,
        'enable_latency': True,
        'enable_error_rate': True
    },
    'error_handling': {
        'correctable_errors': True,
        'uncorrectable_errors': True,
        'error_recovery': True,
        'max_retry_count': 3,
        'recovery_cycles': 1000
    }
}
```

## Implementation Steps

### Step 1: Create Template Directory Structure
```bash
mkdir -p src/templates/systemverilog/{advanced,components,includes}
```

### Step 2: Enhance Template Renderer
- Add SystemVerilog filters to `template_renderer.py`
- Add validation functions
- Add template caching for performance

### Step 3: Create Basic Templates

#### device_config.sv.j2
```systemverilog
{{ header | safe }}

module device_config #(
    parameter VENDOR_ID = {{ vendor_id | sv_hex(16) }},
    parameter DEVICE_ID = {{ device_id | sv_hex(16) }},
    parameter CLASS_CODE = {{ class_code | sv_hex(24) }},
    parameter SUBSYSTEM_VENDOR_ID = {{ vendor_id | sv_hex(16) }},
    parameter SUBSYSTEM_DEVICE_ID = {{ device_id | sv_hex(16) }},
{%- for i in range(6) %}
    parameter BAR{{ i }}_APERTURE = {{ bars[i] | sv_hex(32) }}{{ "," if not loop.last else "" }}
{%- endfor %}
) (
    // Configuration space interface
    output logic [31:0] cfg_device_id,
    output logic [31:0] cfg_class_code,
    output logic [31:0] cfg_subsystem_id,
    output logic [31:0] cfg_bar [0:5]
);

    // Device identification
    assign cfg_device_id = {DEVICE_ID, VENDOR_ID};
    assign cfg_class_code = {8'h00, CLASS_CODE};
    assign cfg_subsystem_id = {SUBSYSTEM_DEVICE_ID, SUBSYSTEM_VENDOR_ID};

    // BAR configuration
{%- for i in range(6) %}
    assign cfg_bar[{{ i }}] = BAR{{ i }}_APERTURE;
{%- endfor %}

endmodule
```

### Step 4: Create Advanced Templates

#### power_management.sv.j2
```systemverilog
// Advanced Power Management State Machine
typedef enum logic [2:0] {
    PM_D0_ACTIVE    = 3'b000,
    PM_D0_TO_D1     = 3'b001,
    PM_D1_STANDBY   = 3'b010,
    PM_D1_TO_D0     = 3'b011,
    PM_D0_TO_D3     = 3'b100,
    PM_D3_SUSPEND   = 3'b101,
    PM_D3_TO_D0     = 3'b110,
    PM_ERROR        = 3'b111
} power_state_t;

power_state_t pm_state = PM_D0_ACTIVE;
power_state_t pm_next_state;

// Power state transition logic
always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        pm_state <= PM_D0_ACTIVE;
        power_transition_timer <= 16'h0;
        power_state_changing <= 1'b0;
    end else begin
        pm_state <= pm_next_state;
        
        if (power_state_changing) begin
            power_transition_timer <= power_transition_timer + 1;
        end else begin
            power_transition_timer <= 16'h0;
        end
    end
end

// Power state combinational logic
always_comb begin
    pm_next_state = pm_state;
    power_state_changing = 1'b0;
    
    case (pm_state)
        PM_D0_ACTIVE: begin
            if (power_down_request) begin
                pm_next_state = PM_D0_TO_D1;
                power_state_changing = 1'b1;
            end
        end
        
        PM_D0_TO_D1: begin
            power_state_changing = 1'b1;
            if (power_transition_timer >= {{ power_management.transition_cycles.d0_to_d1 }}) begin
                pm_next_state = PM_D1_STANDBY;
            end
        end
        
        PM_D1_STANDBY: begin
            if (power_up_request) begin
                pm_next_state = PM_D1_TO_D0;
                power_state_changing = 1'b1;
            end
        end
        
        PM_D1_TO_D0: begin
            power_state_changing = 1'b1;
            if (power_transition_timer >= {{ power_management.transition_cycles.d1_to_d0 }}) begin
                pm_next_state = PM_D0_ACTIVE;
            end
        end
        
        // Additional states...
        default: pm_next_state = PM_ERROR;
    endcase
end
```

### Step 5: Refactor Generators

#### New systemverilog_generator.py Structure
```python
class SystemVerilogGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.renderer = TemplateRenderer()
    
    def generate_device_config_module(self, device_info: Dict[str, Any]) -> str:
        """Generate device configuration using template."""
        context = {
            'header': self._generate_header(device_info),
            'vendor_id': device_info['vendor_id'],
            'device_id': device_info['device_id'],
            'class_code': device_info['class_code'],
            'bars': device_info['bars']
        }
        return self.renderer.render_template('systemverilog/device_config.sv.j2', context)
    
    def generate_top_level_wrapper(self, device_info: Dict[str, Any]) -> str:
        """Generate top-level wrapper using template."""
        context = {
            'header': self._generate_header(device_info),
            'vendor_id': device_info['vendor_id'],
            'device_id': device_info['device_id'],
            'board': device_info.get('board', 'unknown')
        }
        return self.renderer.render_template('systemverilog/top_level_wrapper.sv.j2', context)
```

#### New advanced_sv_generator.py Structure
```python
class AdvancedSystemVerilogGenerator:
    def __init__(self, device_config, power_config, perf_config, error_config):
        self.device_config = device_config
        self.power_config = power_config
        self.perf_config = perf_config
        self.error_config = error_config
        self.renderer = TemplateRenderer()
    
    def generate_advanced_module(self, regs, variance_model=None):
        """Generate advanced SystemVerilog module using templates."""
        context = {
            'device_config': self.device_config,
            'power_management': self._build_power_context(),
            'performance_counters': self._build_perf_context(),
            'error_handling': self._build_error_context(),
            'registers': regs,
            'variance_model': variance_model
        }
        
        # Render main module with included sub-templates
        return self.renderer.render_template('systemverilog/advanced/main_module.sv.j2', context)
```

## Benefits of Migration

1. **Syntax Safety**: Eliminates all f-string syntax errors
2. **Maintainability**: Clear separation of logic and templates
3. **Modularity**: Reusable template components
4. **Validation**: Template-level syntax checking
5. **Documentation**: Templates serve as living documentation
6. **Testing**: Templates can be unit tested independently
7. **Flexibility**: Easy to modify SystemVerilog structure without code changes

## Testing Strategy

1. **Template Validation**: Ensure all templates render without errors
2. **Syntax Checking**: Validate generated SystemVerilog syntax
3. **Functional Testing**: Verify generated modules work correctly
4. **Regression Testing**: Compare output with original generators
5. **Performance Testing**: Measure template rendering performance

## Migration Timeline

1. **Day 1**: Create template structure and enhance renderer
2. **Day 2**: Create basic templates and refactor systemverilog_generator.py
3. **Day 3**: Create advanced templates and refactor advanced_sv_generator.py
4. **Day 4**: Testing, validation, and bug fixes
5. **Day 5**: Documentation and final integration

## Success Criteria

- [ ] All f-string syntax errors resolved
- [ ] All SystemVerilog generation uses templates
- [ ] Generated code is functionally equivalent
- [ ] Template system is well-documented
- [ ] Performance is acceptable (< 2x slower than original)
- [ ] Code is more maintainable and modular

## Next Steps

1. Switch to Code mode to implement the migration
2. Create template directory structure
3. Enhance template renderer with SystemVerilog filters
4. Create all SystemVerilog templates
5. Refactor both generator files
6. Test and validate the implementation