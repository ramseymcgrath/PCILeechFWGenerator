#!/usr/bin/env python3
"""
driver_scrape.py  <vendor_id_hex> <device_id_hex>
Example:
    python3 driver_scrape.py 8086 1533
Outputs JSON list:
[
  {"offset": 0x400, "name": "reg_ctrl", "value": "0x0", "rw": "rw",
   "context": {"function": "init_device", "dependencies": ["reg_status"],
   "timing": "early", "access_pattern": "write_then_read"}},
  ...
]
"""
import ast
import json
import os
import pathlib
import platform
import re
import subprocess
import sys
import tarfile
import tempfile


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system().lower() == "linux"


def check_linux_requirement(operation: str) -> None:
    """Check if operation requires Linux and raise error if not available."""
    if not is_linux():
        raise RuntimeError(
            f"{operation} requires Linux. "
            f"Current platform: {platform.system()}. "
            f"This functionality is only available on Linux systems."
        )


# Import state machine extractor
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now import the state machine extractor
from src.scripts.state_machine_extractor import StateMachineExtractor

# Module-level variables will be set in main()
VENDOR = None
DEVICE = None


# ------------------------------------------------------------------ helpers
def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)


def ensure_kernel_source():
    """Extract /usr/src/linux-source-*.tar.* if not untarred yet."""
    # Find the source package
    src_path = pathlib.Path("/usr/src")

    # In real execution, this will be an iterator
    # In tests, this is mocked to return a list directly
    glob_result = src_path.glob("linux-source-*.tar*")

    # Get the first source package
    # This approach works with both real iterators and mocked lists
    src_pkg = None
    for pkg in glob_result:
        src_pkg = pkg
        break

    if not src_pkg:
        print("Warning: linux-source package not found inside container.")
        # Return empty data instead of exiting
        return None

    untar_dir = src_pkg.with_suffix("").with_suffix("")  # strip .tar.xz
    if not (untar_dir / "drivers").exists():
        print("[driver_scrape] Extracting kernel source…")
        with tarfile.open(src_pkg) as t:
            # Security: validate tar members before extraction
            def is_safe_path(path):
                return not (path.startswith("/") or ".." in path)

            safe_members = [m for m in t.getmembers() if is_safe_path(m.name)]
            t.extractall("/usr/src", members=safe_members)
    return untar_dir


def ko_name_from_alias():
    check_linux_requirement("Driver module resolution")
    alias_line = run(
        f"modprobe --resolve-alias pci:v0000{VENDOR}d0000{DEVICE}*"
    ).splitlines()
    if not alias_line:
        sys.exit("No driver module found for that VID:DID in modules.alias")
    return alias_line[-1].strip()  # e.g. snd_hda_intel


def analyze_function_context(file_content, reg_name):
    """Analyze the function context where a register is used."""
    context = {
        "function": None,
        "dependencies": [],
        "timing": "unknown",
        "access_pattern": "unknown",
    }

    # Find function containing the register usage
    func_pattern = re.compile(
        r"(\w+)\s*\([^)]*\)\s*\{[^}]*" + re.escape(reg_name) + r"[^}]*\}", re.DOTALL
    )
    func_match = func_pattern.search(file_content)

    if func_match:
        context["function"] = func_match.group(1)
        func_body = func_match.group(0)

        # Analyze dependencies - other registers used in same function
        dep_pattern = re.compile(r"\b(REG_[A-Z0-9_]+)\b")
        deps = set(dep_pattern.findall(func_body))
        deps.discard(reg_name)  # Remove self
        context["dependencies"] = list(deps)[:5]  # Limit to 5 most relevant

        # Determine timing based on function name patterns
        if any(
            keyword in context["function"].lower()
            for keyword in ["init", "probe", "start"]
        ):
            context["timing"] = "early"
        elif any(
            keyword in context["function"].lower()
            for keyword in ["exit", "remove", "stop"]
        ):
            context["timing"] = "late"
        elif any(
            keyword in context["function"].lower()
            for keyword in ["irq", "interrupt", "handler"]
        ):
            context["timing"] = "interrupt"
        else:
            context["timing"] = "runtime"

        # Analyze access patterns
        write_count = len(
            re.findall(r"write[blwq]?\s*\([^)]*" + re.escape(reg_name), func_body)
        )
        read_count = len(
            re.findall(r"read[blwq]?\s*\([^)]*" + re.escape(reg_name), func_body)
        )

        # Check for specific patterns based on read/write counts
        if write_count > 0 and read_count > 0:
            # Check for write-then-read pattern (exactly one write followed by one read)
            if write_count == 1 and read_count == 1:
                write_pos = re.search(
                    r"write[blwq]?\s*\([^)]*" + re.escape(reg_name), func_body
                ).start()
                read_pos = re.search(
                    r"read[blwq]?\s*\([^)]*" + re.escape(reg_name), func_body
                ).start()
                if write_pos < read_pos:
                    context["access_pattern"] = "write_then_read"
                else:
                    context["access_pattern"] = "balanced"
            # Check if significantly more writes than reads
            elif write_count > read_count * 1.5:
                context["access_pattern"] = "write_heavy"
            # Check if significantly more reads than writes
            elif read_count > write_count * 1.5:
                context["access_pattern"] = "read_heavy"
            # Otherwise it's balanced
            else:
                context["access_pattern"] = "balanced"
        elif write_count > 0:
            context["access_pattern"] = "write_heavy"
        elif read_count > 0:
            context["access_pattern"] = "read_heavy"
        else:
            context["access_pattern"] = "unknown"

    return context


def analyze_access_sequences(file_content, reg_name=None):
    """Analyze register access sequences for a specific register.

    Args:
        file_content: The source code content to analyze
        reg_name: Optional specific register name to focus on

    Returns:
        List of access sequences with function context and position information
    """
    sequences = []

    # Find functions in the file
    func_pattern = re.compile(r"(\w+)\s*\([^)]*\)\s*\{([^}]*)\}", re.DOTALL)

    for func_match in func_pattern.finditer(file_content):
        func_name = func_match.group(1)
        func_body = func_match.group(2)

        # Find all register accesses in order
        access_pattern = re.compile(
            r"(write|read)[blwq]?\s*\([^)]*\b(REG_[A-Z0-9_]+)\b"
        )
        accesses = []

        for access_match in access_pattern.finditer(func_body):
            operation = access_match.group(1)
            register = access_match.group(2)

            # If specific register requested, filter for it
            if reg_name and register != reg_name:
                continue

            accesses.append((operation, register, access_match.start()))

        # Only process functions with register accesses
        if len(accesses) > 0:
            for i, (op, reg, pos) in enumerate(accesses):
                sequence = {
                    "function": func_name,
                    "position": i,
                    "total_ops": len(accesses),
                    "operation": op,
                    "register": reg,
                }

                # Add preceding and following operations for context
                if i > 0:
                    sequence["preceded_by"] = accesses[i - 1][1]  # Register name
                    sequence["preceded_by_op"] = accesses[i - 1][0]  # Operation
                if i < len(accesses) - 1:
                    sequence["followed_by"] = accesses[i + 1][1]  # Register name
                    sequence["followed_by_op"] = accesses[i + 1][0]  # Operation

                sequences.append(sequence)

    return sequences


def analyze_register_sequences(file_content, registers):
    """Analyze register access sequences, timing dependencies, and state patterns."""
    sequences = {}
    state_patterns = {}

    # Find sequences of register accesses within functions
    func_pattern = re.compile(r"(\w+)\s*\([^)]*\)\s*\{([^}]*)\}", re.DOTALL)

    for func_match in func_pattern.finditer(file_content):
        func_name = func_match.group(1)
        func_body = func_match.group(2)

        # Find all register accesses in order
        access_pattern = re.compile(
            r"(write|read)[blwq]?\s*\([^)]*\b(REG_[A-Z0-9_]+)\b"
        )
        accesses = []

        for access_match in access_pattern.finditer(func_body):
            operation = access_match.group(1)
            reg_name = access_match.group(2)
            if reg_name in registers:
                accesses.append((operation, reg_name, access_match.start()))

        if len(accesses) > 1:
            sequences[func_name] = accesses

            # Analyze for state machine patterns
            state_info = analyze_state_patterns(func_body, accesses, registers)
            if state_info:
                state_patterns[func_name] = state_info

    return sequences, state_patterns


def analyze_state_patterns(func_body, accesses, registers):
    """Analyze function body for state machine patterns."""
    state_info = {
        "has_state_variable": False,
        "has_conditional_logic": False,
        "has_loops": False,
        "state_transitions": [],
        "complexity_indicators": [],
    }

    # Look for state variables
    state_var_pattern = re.compile(
        r"\b(\w*state\w*|\w*mode\w*|\w*status\w*)\s*=", re.IGNORECASE
    )
    if state_var_pattern.search(func_body):
        state_info["has_state_variable"] = True
        state_info["complexity_indicators"].append("explicit_state_variable")

    # Look for switch statements (strong indicator of state machine)
    switch_pattern = re.compile(r"switch\s*\([^)]+\)\s*\{", re.IGNORECASE)
    if switch_pattern.search(func_body):
        state_info["has_conditional_logic"] = True
        state_info["complexity_indicators"].append("switch_statement")

    # Look for if-else chains
    if_else_pattern = re.compile(r"if\s*\([^)]+\)[^}]*else\s+if", re.IGNORECASE)
    if if_else_pattern.search(func_body):
        state_info["has_conditional_logic"] = True
        state_info["complexity_indicators"].append("if_else_chain")

    # Look for loops
    loop_pattern = re.compile(r"\b(for|while|do)\s*\(", re.IGNORECASE)
    if loop_pattern.search(func_body):
        state_info["has_loops"] = True
        state_info["complexity_indicators"].append("loops")

    # Analyze register access patterns for state transitions
    if len(accesses) >= 2:
        for i in range(len(accesses) - 1):
            current_access = accesses[i]
            next_access = accesses[i + 1]

            # Look for delays between accesses (indicates state transition timing)
            section = func_body[current_access[2] : next_access[2]]
            delay_pattern = re.compile(
                r"(udelay|mdelay|msleep|usleep_range)\s*\(\s*(\d+)", re.IGNORECASE
            )
            delay_match = delay_pattern.search(section)

            transition = {
                "from_register": current_access[1],
                "to_register": next_access[1],
                "from_operation": current_access[0],
                "to_operation": next_access[0],
                "has_delay": bool(delay_match),
                "delay_us": None,
            }

            if delay_match:
                delay_type = delay_match.group(1).lower()
                delay_value = int(delay_match.group(2))

                # Convert to microseconds
                if delay_type in ["mdelay", "msleep"]:
                    transition["delay_us"] = delay_value * 1000
                elif delay_type == "udelay":
                    transition["delay_us"] = delay_value
                else:  # usleep_range
                    transition["delay_us"] = delay_value

            state_info["state_transitions"].append(transition)

    # Calculate complexity score
    complexity_score = 0
    if state_info["has_state_variable"]:
        complexity_score += 2
    if state_info["has_conditional_logic"]:
        complexity_score += 3
    if state_info["has_loops"]:
        complexity_score += 1
    complexity_score += len(state_info["state_transitions"]) * 0.5

    state_info["complexity_score"] = complexity_score

    # Only return if there are meaningful state patterns
    return state_info if complexity_score > 1.0 else None


def analyze_timing_constraints(file_content, reg_name=None):
    """Analyze timing constraints and delays related to register accesses.

    Args:
        file_content: The source code content to analyze
        reg_name: Optional specific register name to focus on

    Returns:
        List of timing constraints with delay values in microseconds
    """
    constraints = []

    # Look for delay patterns
    delay_pattern = re.compile(
        r"(udelay|mdelay|msleep|usleep_range)\s*\(\s*(\d+)", re.IGNORECASE
    )

    for delay_match in delay_pattern.finditer(file_content):
        delay_type = delay_match.group(1).lower()
        delay_value = int(delay_match.group(2))

        # Convert to microseconds for consistency
        if delay_type in ["mdelay", "msleep"]:
            delay_us = delay_value * 1000
        elif delay_type == "udelay":
            delay_us = delay_value
        else:  # usleep_range
            delay_us = delay_value

        # Find nearby register accesses
        context_start = max(0, delay_match.start() - 200)
        context_end = min(len(file_content), delay_match.end() + 200)
        context = file_content[context_start:context_end]

        reg_pattern = re.compile(r"\b(REG_[A-Z0-9_]+)\b")
        nearby_regs = reg_pattern.findall(context)

        # Filter for specific register if provided
        if reg_name and reg_name not in nearby_regs:
            continue

        if nearby_regs:
            constraint = {
                "delay_us": delay_us,
                "registers": list(set(nearby_regs)),
                "context": "register_access",
            }

            # Determine if this is a post-write or pre-read delay
            pre_context = file_content[context_start : delay_match.start()]
            post_context = file_content[delay_match.end() : context_end]

            if re.search(r"write[blwq]?\s*\([^)]*", pre_context):
                constraint["type"] = "post_write_delay"
            elif re.search(r"read[blwq]?\s*\([^)]*", post_context):
                constraint["type"] = "pre_read_delay"
            else:
                constraint["type"] = "general_delay"

            constraints.append(constraint)

    return constraints


def extract_timing_constraints(file_content):
    """Extract timing constraints and delays from driver code."""
    timing_info = {}

    # Look for delay patterns
    delay_pattern = re.compile(
        r"(udelay|mdelay|msleep|usleep_range)\s*\(\s*(\d+)", re.IGNORECASE
    )

    for delay_match in delay_pattern.finditer(file_content):
        delay_type = delay_match.group(1).lower()
        delay_value = int(delay_match.group(2))

        # Convert to microseconds for consistency
        if delay_type in ["mdelay", "msleep"]:
            delay_us = delay_value * 1000
        elif delay_type == "udelay":
            delay_us = delay_value
        else:  # usleep_range
            delay_us = delay_value

        # Find nearby register accesses
        context_start = max(0, delay_match.start() - 200)
        context_end = min(len(file_content), delay_match.end() + 200)
        context = file_content[context_start:context_end]

        reg_pattern = re.compile(r"\b(REG_[A-Z0-9_]+)\b")
        nearby_regs = reg_pattern.findall(context)

        if nearby_regs:
            timing_info[delay_match.start()] = {
                "delay_us": delay_us,
                "registers": list(set(nearby_regs)),
            }

    return timing_info


# ------------------------------------------------------------------ main
def main():
    """Main function to scrape driver registers."""
    global VENDOR, DEVICE

    if len(sys.argv) != 3:
        sys.exit("Usage: driver_scrape.py <vendor_id hex> <device_id hex>")

    VENDOR = sys.argv[1].lower()
    DEVICE = sys.argv[2].lower()

    ksrc = ensure_kernel_source()

    # If kernel source not found, return empty data with state machine analysis
    if ksrc is None:
        empty_output = {
            "registers": [],
            "state_machine_analysis": {
                "extracted_state_machines": 0,
                "optimized_state_machines": 0,
                "functions_with_state_patterns": 0,
                "state_machines": [],
                "analysis_report": "Linux source package not found. Unable to perform analysis.",
            },
        }
        print(json.dumps(empty_output, indent=2))
        return

    try:
        driver = ko_name_from_alias()
        print(f"[driver_scrape] Driver module: {driver}")

        # find .c/.h files containing driver name
        src_files = list(ksrc.rglob(f"{driver}*.c")) + list(ksrc.rglob(f"{driver}*.h"))
        if not src_files:
            # heuristic: fallback to any file inside drivers/ with module name inside it
            src_files = [
                p for p in ksrc.rglob("*.c") if driver in p.read_text(errors="ignore")
            ][:20]

        if not src_files:
            # Return empty data with state machine analysis
            empty_output = {
                "registers": [],
                "state_machine_analysis": {
                    "extracted_state_machines": 0,
                    "optimized_state_machines": 0,
                    "functions_with_state_patterns": 0,
                    "state_machines": [],
                    "analysis_report": "No driver source files found for the specified device.",
                },
            }
            print(json.dumps(empty_output, indent=2))
            return
    except Exception as e:
        # Handle any errors in driver resolution
        error_output = {
            "registers": [],
            "state_machine_analysis": {
                "extracted_state_machines": 0,
                "optimized_state_machines": 0,
                "functions_with_state_patterns": 0,
                "state_machines": [],
                "analysis_report": f"Error during driver analysis: {str(e)}",
            },
        }
        print(json.dumps(error_output, indent=2))
        return

    REG = re.compile(r"#define\s+(REG_[A-Z0-9_]+)\s+0x([0-9A-Fa-f]+)")
    WR = re.compile(r"write[blwq]?\s*\(.*?\b(REG_[A-Z0-9_]+)\b")
    RD = re.compile(r"read[blwq]?\s*\(.*?\b(REG_[A-Z0-9_]+)\b")

    regs, writes, reads = {}, set(), set()
    all_content = ""

    # Enhanced analysis: collect all file content and register information
    for path in src_files:
        txt = path.read_text(errors="ignore")
        all_content += txt + "\n"

        for m in REG.finditer(txt):
            regs[m.group(1)] = int(m.group(2), 16)
        for w in WR.finditer(txt):
            writes.add(w.group(1))
            if len(writes) > 64:
                break
        for r in RD.finditer(txt):
            reads.add(r.group(1))
            if len(reads) > 64:
                break

    # Analyze register sequences, state patterns, and timing
    sequences, state_patterns = analyze_register_sequences(all_content, regs.keys())
    timing_info = extract_timing_constraints(all_content)

    # Extract state machines using the new state machine extractor
    state_machine_extractor = StateMachineExtractor(debug=False)
    extracted_state_machines = state_machine_extractor.extract_state_machines(
        all_content, regs
    )
    optimized_state_machines = state_machine_extractor.optimize_state_machines()

    items = []
    for sym, off in regs.items():
        # Determine read/write capability
        rw_capability = "ro"  # default
        if sym in writes and sym in reads:
            rw_capability = "rw"
        elif sym in writes:
            rw_capability = "wo"
        elif sym in reads:
            rw_capability = "ro"

        # Analyze context for this register
        context = analyze_function_context(all_content, sym)

        # Add timing information if available
        relevant_timing = []
        for timing_pos, timing_data in timing_info.items():
            if sym in timing_data["registers"]:
                relevant_timing.append(
                    {"delay_us": timing_data["delay_us"], "context": "register_access"}
                )

        if relevant_timing:
            context["timing_constraints"] = relevant_timing[
                :3
            ]  # Limit to 3 most relevant

        # Add sequence information
        context["sequences"] = []
        for func_name, func_sequences in sequences.items():
            for i, (op, reg_name, pos) in enumerate(func_sequences):
                if reg_name == sym:
                    # Add context about surrounding operations
                    sequence_context = {
                        "function": func_name,
                        "position": i,
                        "total_ops": len(func_sequences),
                        "operation": op,
                    }

                    # Add preceding and following operations
                    if i > 0:
                        sequence_context["preceded_by"] = func_sequences[i - 1][1]
                    if i < len(func_sequences) - 1:
                        sequence_context["followed_by"] = func_sequences[i + 1][1]

                    context["sequences"].append(sequence_context)

        # Add state pattern information
        context["state_patterns"] = {}
        for func_name, pattern_info in state_patterns.items():
            # Check if this register is involved in state patterns
            register_involved = False
            for transition in pattern_info.get("state_transitions", []):
                if (
                    transition["from_register"] == sym
                    or transition["to_register"] == sym
                ):
                    register_involved = True
                    break

            if register_involved:
                context["state_patterns"][func_name] = {
                    "complexity_score": pattern_info["complexity_score"],
                    "complexity_indicators": pattern_info["complexity_indicators"],
                    "has_state_variable": pattern_info["has_state_variable"],
                    "has_conditional_logic": pattern_info["has_conditional_logic"],
                    "transitions_count": len(pattern_info["state_transitions"]),
                }

        # Add state machine information
        context["state_machines"] = []
        for sm in optimized_state_machines:
            if (
                sym.lower() in [reg.lower() for reg in sm.registers]
                or f"reg_0x{off:08x}" in sm.registers
            ):
                sm_info = {
                    "name": sm.name,
                    "states_count": len(sm.states),
                    "transitions_count": len(sm.transitions),
                    "complexity_score": sm.complexity_score,
                    "type": sm.context.get("type", "unknown"),
                    "initial_state": sm.initial_state,
                    "final_states": list(sm.final_states),
                }
                context["state_machines"].append(sm_info)

        items.append(
            dict(
                offset=off,
                name=sym.lower(),
                value="0x0",
                rw=rw_capability,
                context=context,
            )
        )

    # Create comprehensive output with state machine metadata
    output = {
        "registers": items,
        "state_machine_analysis": {
            "extracted_state_machines": len(extracted_state_machines),
            "optimized_state_machines": len(optimized_state_machines),
            "functions_with_state_patterns": len(state_patterns),
            "state_machines": [sm.to_dict() for sm in optimized_state_machines],
            "analysis_report": state_machine_extractor.generate_analysis_report(),
        },
    }

    print(json.dumps(output, indent=2))


def extract_registers_from_file(file_path):
    """Extract register definitions from a header or source file.

    Args:
        file_path: Path to the file to analyze

    Returns:
        List of register dictionaries with name, offset, and other properties
    """
    registers = []

    try:
        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

        # Find register definitions (#define REG_XXX 0xYYYY)
        reg_pattern = re.compile(r"#define\s+(REG_[A-Z0-9_]+)\s+0x([0-9A-Fa-f]+)")

        for match in reg_pattern.finditer(content):
            reg_name = match.group(1)
            reg_offset = int(match.group(2), 16)

            # Default to read-write until we analyze access patterns
            registers.append(
                {
                    "name": reg_name,
                    "offset": reg_offset,
                    "value": "0x0",
                    "rw": "rw",  # Default to read-write
                }
            )

    except Exception as e:
        print(f"Error extracting registers from {file_path}: {e}")

    return registers


def enhance_registers_with_context(registers, file_path):
    """Enhance register information with context from source files.

    Args:
        registers: List of register dictionaries to enhance
        file_path: Path to the source file to analyze

    Returns:
        Enhanced list of register dictionaries with context information
    """
    enhanced_registers = []

    try:
        with open(file_path, "r", errors="ignore") as f:
            content = f.read()

        for reg in registers:
            reg_name = reg["name"]

            # Create a copy of the register with enhanced context
            enhanced_reg = reg.copy()

            # Analyze function context
            context = analyze_function_context(content, reg_name)

            # Analyze timing constraints
            timing_constraints = analyze_timing_constraints(content, reg_name)
            if timing_constraints:
                context["timing_constraints"] = timing_constraints[
                    :3
                ]  # Limit to 3 most relevant

            # Analyze access sequences
            sequences = analyze_access_sequences(content, reg_name)
            if sequences:
                context["sequences"] = sequences

            # Add the enhanced context to the register
            enhanced_reg["context"] = context
            enhanced_registers.append(enhanced_reg)

    except Exception as e:
        print(f"Error enhancing registers from {file_path}: {e}")
        # Return original registers if enhancement fails
        return registers

    return enhanced_registers


def find_driver_sources(kernel_source_dir, driver_name):
    """Find source files for a specific driver in the kernel source tree.

    Args:
        kernel_source_dir: Path to the kernel source directory
        driver_name: Name of the driver module to find

    Returns:
        List of paths to source files related to the driver
    """
    # Convert to Path object if it's a string
    if isinstance(kernel_source_dir, str):
        kernel_source_dir = pathlib.Path(kernel_source_dir)

    # First, try to find files directly matching the driver name
    src_files = list(kernel_source_dir.rglob(f"{driver_name}*.c")) + list(
        kernel_source_dir.rglob(f"{driver_name}*.h")
    )

    # If no direct matches, try to find files containing the driver name in their content
    if not src_files:
        # Look in drivers directory first as it's most likely location
        drivers_dir = kernel_source_dir / "drivers"
        if drivers_dir.exists():
            candidates = []
            for ext in [".c", ".h"]:
                for file_path in drivers_dir.rglob(f"*{ext}"):
                    try:
                        content = file_path.read_text(errors="ignore")
                        if driver_name in content:
                            candidates.append(file_path)
                            # Limit to prevent excessive searching
                            if len(candidates) >= 20:
                                break
                    except Exception:
                        continue
            src_files = candidates

    return src_files


def extract_and_analyze_registers(source_files, all_content=None):
    """Extract and analyze registers from source files.

    This function combines the extraction of register definitions with context analysis
    to provide comprehensive information about registers found in driver source code.

    Args:
        source_files: List of source file paths to analyze
        all_content: Optional pre-loaded content of all files combined

    Returns:
        List of register dictionaries with enhanced context information
    """
    if all_content is None:
        all_content = ""
        for path in source_files:
            try:
                with open(path, "r", errors="ignore") as f:
                    all_content += f.read() + "\n"
            except Exception as e:
                print(f"Error reading {path}: {e}")

    # Extract register definitions
    REG = re.compile(r"#define\s+(REG_[A-Z0-9_]+)\s+0x([0-9A-Fa-f]+)")
    WR = re.compile(r"write[blwq]?\s*\(.*?\b(REG_[A-Z0-9_]+)\b")
    RD = re.compile(r"read[blwq]?\s*\(.*?\b(REG_[A-Z0-9_]+)\b")

    regs, writes, reads = {}, set(), set()

    for m in REG.finditer(all_content):
        regs[m.group(1)] = int(m.group(2), 16)
    for w in WR.finditer(all_content):
        writes.add(w.group(1))
    for r in RD.finditer(all_content):
        reads.add(r.group(1))

    # Create register objects with context
    items = []
    for sym, off in regs.items():
        # Determine read/write capability
        rw_capability = "ro"  # default
        if sym in writes and sym in reads:
            rw_capability = "rw"
        elif sym in writes:
            rw_capability = "wo"
        elif sym in reads:
            rw_capability = "ro"

        # Analyze context for this register
        context = analyze_function_context(all_content, sym)

        # Add timing constraints
        timing_constraints = analyze_timing_constraints(all_content, sym)
        if timing_constraints:
            context["timing_constraints"] = timing_constraints[
                :3
            ]  # Limit to 3 most relevant

        # Add access sequences
        sequences = analyze_access_sequences(all_content, sym)
        if sequences:
            context["sequences"] = sequences[:5]  # Limit to 5 most relevant

        items.append(
            dict(
                offset=off,
                name=sym,
                value="0x0",
                rw=rw_capability,
                context=context,
            )
        )

    return items


if __name__ == "__main__":
    main()
