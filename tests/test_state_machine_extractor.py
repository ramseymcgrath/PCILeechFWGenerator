#!/usr/bin/env python3
"""
Test suite for State Machine Extractor

This module tests the state machine extraction capabilities for analyzing
driver code patterns and generating SystemVerilog state machines.
"""

import re
from unittest.mock import patch

import pytest

from src.scripts.state_machine_extractor import (
    StateMachine,
    StateMachineExtractor,
    StateTransition,
    StateType,
    TransitionType,
)


class TestStateTransition:
    """Test the StateTransition class."""

    def test_state_transition_init(self):
        """Test StateTransition initialization with default values."""
        transition = StateTransition(
            from_state="IDLE", to_state="ACTIVE", trigger="start_trigger"
        )

        assert transition.from_state == "IDLE"
        assert transition.to_state == "ACTIVE"
        assert transition.trigger == "start_trigger"
        assert transition.condition is None
        assert transition.action is None
        assert transition.transition_type == TransitionType.CONDITION
        assert transition.delay_us is None
        assert transition.register_offset is None
        assert transition.register_value is None
        assert transition.confidence == 1.0

    def test_state_transition_init_with_custom_values(self):
        """Test StateTransition initialization with custom values."""
        transition = StateTransition(
            from_state="IDLE",
            to_state="ACTIVE",
            trigger="register_write",
            condition="value == 1",
            action="set_flag",
            transition_type=TransitionType.REGISTER_WRITE,
            delay_us=100,
            register_offset=0x1000,
            register_value=0x1,
            confidence=0.9,
        )

        assert transition.from_state == "IDLE"
        assert transition.to_state == "ACTIVE"
        assert transition.trigger == "register_write"
        assert transition.condition == "value == 1"
        assert transition.action == "set_flag"
        assert transition.transition_type == TransitionType.REGISTER_WRITE
        assert transition.delay_us == 100
        assert transition.register_offset == 0x1000
        assert transition.register_value == 0x1
        assert transition.confidence == 0.9

    def test_to_dict(self):
        """Test the to_dict method."""
        transition = StateTransition(
            from_state="IDLE",
            to_state="ACTIVE",
            trigger="register_write",
            condition="value == 1",
            action="set_flag",
            transition_type=TransitionType.REGISTER_WRITE,
            delay_us=100,
            register_offset=0x1000,
            register_value=0x1,
            confidence=0.9,
        )

        result = transition.to_dict()

        assert result["from_state"] == "IDLE"
        assert result["to_state"] == "ACTIVE"
        assert result["trigger"] == "register_write"
        assert result["condition"] == "value == 1"
        assert result["action"] == "set_flag"
        assert result["transition_type"] == "register_write"
        assert result["delay_us"] == 100
        assert result["register_offset"] == 0x1000
        assert result["register_value"] == 0x1
        assert result["confidence"] == 0.9


class TestStateMachine:
    """Test the StateMachine class."""

    def test_state_machine_init(self):
        """Test StateMachine initialization with default values."""
        sm = StateMachine(name="test_sm")

        assert sm.name == "test_sm"
        assert sm.states == set()
        assert sm.transitions == []
        assert sm.initial_state is None
        assert sm.final_states == set()
        assert sm.registers == set()
        assert sm.complexity_score == 0.0
        assert sm.context == {}

    def test_add_state(self):
        """Test adding states to the state machine."""
        sm = StateMachine(name="test_sm")

        # Add a regular state
        sm.add_state("ACTIVE")
        assert "ACTIVE" in sm.states
        assert sm.initial_state is None
        assert "ACTIVE" not in sm.final_states

        # Add an initial state
        sm.add_state("INIT", StateType.INIT)
        assert "INIT" in sm.states
        assert sm.initial_state == "INIT"

        # Add a final state
        sm.add_state("DONE", StateType.CLEANUP)
        assert "DONE" in sm.states
        assert "DONE" in sm.final_states

        # Add an error state
        sm.add_state("ERROR", StateType.ERROR)
        assert "ERROR" in sm.states
        assert "ERROR" in sm.final_states

    def test_add_transition(self):
        """Test adding transitions to the state machine."""
        sm = StateMachine(name="test_sm")

        transition = StateTransition(
            from_state="IDLE",
            to_state="ACTIVE",
            trigger="start",
            register_offset=0x1000,
        )

        sm.add_transition(transition)

        assert len(sm.transitions) == 1
        assert sm.transitions[0] == transition
        assert "IDLE" in sm.states
        assert "ACTIVE" in sm.states
        assert "reg_0x00001000" in sm.registers

    def test_calculate_complexity(self):
        """Test calculating complexity score."""
        sm = StateMachine(name="test_sm")

        # Add states and transitions
        sm.add_state("IDLE", StateType.INIT)
        sm.add_state("ACTIVE")
        sm.add_state("DONE", StateType.CLEANUP)

        sm.add_transition(
            StateTransition(
                from_state="IDLE",
                to_state="ACTIVE",
                trigger="start",
                register_offset=0x1000,
            )
        )

        sm.add_transition(
            StateTransition(
                from_state="ACTIVE",
                to_state="DONE",
                trigger="finish",
                condition="data_ready",
                transition_type=TransitionType.CONDITION,
            )
        )

        # Calculate complexity
        complexity = sm.calculate_complexity()

        # 3 states * 0.5 + 2 transitions * 0.3 + 1 register * 0.2 + 1 conditional * 0.1 = 2.2
        assert complexity == 2.2
        assert sm.complexity_score == 2.2

    def test_to_dict(self):
        """Test the to_dict method."""
        sm = StateMachine(name="test_sm")

        sm.add_state("IDLE", StateType.INIT)
        sm.add_state("ACTIVE")
        sm.add_state("DONE", StateType.CLEANUP)

        sm.add_transition(
            StateTransition(
                from_state="IDLE",
                to_state="ACTIVE",
                trigger="start",
                register_offset=0x1000,
            )
        )

        sm.calculate_complexity()

        result = sm.to_dict()

        assert result["name"] == "test_sm"
        assert set(result["states"]) == {"IDLE", "ACTIVE", "DONE"}
        assert len(result["transitions"]) == 1
        assert result["initial_state"] == "IDLE"
        assert set(result["final_states"]) == {"DONE"}
        assert set(result["registers"]) == {"reg_0x00001000"}
        assert result["complexity_score"] > 0

    def test_generate_systemverilog(self):
        """Test generating SystemVerilog code."""
        sm = StateMachine(name="test_sm")

        sm.add_state("IDLE", StateType.INIT)
        sm.add_state("ACTIVE")
        sm.add_state("DONE", StateType.CLEANUP)

        sm.add_transition(
            StateTransition(
                from_state="IDLE",
                to_state="ACTIVE",
                trigger="start",
                transition_type=TransitionType.REGISTER_WRITE,
                register_offset=0x1000,
            )
        )

        sm.add_transition(
            StateTransition(
                from_state="ACTIVE",
                to_state="DONE",
                trigger="finish",
                condition="data_ready",
                transition_type=TransitionType.CONDITION,
            )
        )

        sv_code = sm.generate_systemverilog()

        # Check for key elements in the generated code
        assert "typedef enum logic" in sv_code
        assert "IDLE" in sv_code
        assert "ACTIVE" in sv_code
        assert "DONE" in sv_code
        assert "test_sm_current_state" in sv_code
        assert "test_sm_next_state" in sv_code
        assert "always_ff @(posedge clk)" in sv_code
        assert "always_comb" in sv_code
        assert "case (test_sm_current_state)" in sv_code

    def test_generate_transition_condition(self):
        """Test generating transition conditions."""
        sm = StateMachine(name="test_sm")

        # Test register write condition
        transition1 = StateTransition(
            from_state="IDLE",
            to_state="ACTIVE",
            trigger="write_reg",
            transition_type=TransitionType.REGISTER_WRITE,
            register_offset=0x1000,
        )

        condition1 = sm._generate_transition_condition(transition1)
        assert condition1 == "bar_wr_en && bar_addr == 32'h00001000"

        # Test register read condition
        transition2 = StateTransition(
            from_state="ACTIVE",
            to_state="DONE",
            trigger="read_reg",
            transition_type=TransitionType.REGISTER_READ,
            register_offset=0x2000,
        )

        condition2 = sm._generate_transition_condition(transition2)
        assert condition2 == "bar_rd_en && bar_addr == 32'h00002000"

        # Test timeout condition
        transition3 = StateTransition(
            from_state="DONE",
            to_state="IDLE",
            trigger="timeout",
            transition_type=TransitionType.TIMEOUT,
        )

        condition3 = sm._generate_transition_condition(transition3)
        assert condition3 == "timeout_expired"

        # Test custom condition
        transition4 = StateTransition(
            from_state="IDLE",
            to_state="ERROR",
            trigger="error",
            condition="error_flag == 1",
            transition_type=TransitionType.CONDITION,
        )

        condition4 = sm._generate_transition_condition(transition4)
        assert condition4 == "error_flag == 1"

        # Test combined conditions
        transition5 = StateTransition(
            from_state="ACTIVE",
            to_state="ERROR",
            trigger="error_on_write",
            condition="error_flag == 1",
            transition_type=TransitionType.REGISTER_WRITE,
            register_offset=0x3000,
        )

        condition5 = sm._generate_transition_condition(transition5)
        assert condition5 == "bar_wr_en && bar_addr == 32'h00003000 && error_flag == 1"


class TestStateMachineExtractor:
    """Test the StateMachineExtractor class."""

    def test_init(self):
        """Test initialization of the extractor."""
        extractor = StateMachineExtractor()
        assert extractor.debug is False
        assert extractor.extracted_machines == []

        extractor_debug = StateMachineExtractor(debug=True)
        assert extractor_debug.debug is True

    def test_extract_functions(self):
        """Test extracting functions from C code."""
        extractor = StateMachineExtractor()

        c_code = """
        static int test_init(struct device *dev) {
            int ret = 0;
            return ret;
        }
        
        int test_probe(struct pci_dev *pdev) {
            int status;
            status = device_init(pdev);
            return status;
        }
        """

        functions = extractor._extract_functions(c_code)

        assert len(functions) == 2
        assert "test_init" in functions
        assert "test_probe" in functions
        assert "int ret = 0;" in functions["test_init"]
        assert "status = device_init(pdev);" in functions["test_probe"]

    def test_extract_explicit_state_machine_switch(self):
        """Test extracting explicit state machine from switch statement."""
        extractor = StateMachineExtractor()

        func_body = """
        {
            switch (dev_state) {
                case STATE_IDLE:
                    writel(0x1, dev->base + REG_CONTROL);
                    dev_state = STATE_ACTIVE;
                    break;
                case STATE_ACTIVE:
                    if (readl(dev->base + REG_STATUS) & 0x1) {
                        dev_state = STATE_DONE;
                    }
                    break;
                case STATE_DONE:
                    writel(0x0, dev->base + REG_CONTROL);
                    dev_state = STATE_IDLE;
                    break;
                default:
                    dev_state = STATE_IDLE;
                    break;
            }
        }
        """

        registers = {"REG_CONTROL": 0x1000, "REG_STATUS": 0x1004}

        sm = extractor._extract_explicit_state_machine(
            "test_func", func_body, registers
        )

        assert sm is not None
        assert sm.name == "test_func_dev_state_sm"
        assert "STATE_IDLE" in sm.states
        assert "STATE_ACTIVE" in sm.states
        assert "STATE_DONE" in sm.states
        assert len(sm.transitions) > 0

    def test_extract_explicit_state_machine_if_chain(self):
        """Test extracting explicit state machine from if-else chain."""
        extractor = StateMachineExtractor()

        func_body = """
        {
            if (dev_state == STATE_IDLE) {
                writel(0x1, dev->base + REG_CONTROL);
                dev_state = STATE_ACTIVE;
            } else if (dev_state == STATE_ACTIVE) {
                if (readl(dev->base + REG_STATUS) & 0x1) {
                    dev_state = STATE_DONE;
                }
            } else if (dev_state == STATE_DONE) {
                writel(0x0, dev->base + REG_CONTROL);
                dev_state = STATE_IDLE;
            } else {
                dev_state = STATE_IDLE;
            }
        }
        """

        registers = {"REG_CONTROL": 0x1000, "REG_STATUS": 0x1004}

        sm = extractor._extract_explicit_state_machine(
            "test_func", func_body, registers
        )

        assert sm is not None
        assert sm.name == "test_func_dev_state_sm"
        assert "STATE_IDLE" in sm.states
        assert "STATE_ACTIVE" in sm.states
        assert "STATE_DONE" in sm.states

    def test_extract_implicit_state_machine(self):
        """Test extracting implicit state machine from register access sequence."""
        extractor = StateMachineExtractor()

        func_body = """
        {
            writel(0x1, dev->base + REG_CONTROL);
            udelay(100);
            writel(0x2, dev->base + REG_CONFIG);
            
            status = readl(dev->base + REG_STATUS);
            if (status & 0x1) {
                writel(0x3, dev->base + REG_COMMAND);
            }
        }
        """

        registers = {
            "REG_CONTROL": 0x1000,
            "REG_CONFIG": 0x1004,
            "REG_STATUS": 0x1008,
            "REG_COMMAND": 0x100C,
        }

        sm = extractor._extract_implicit_state_machine(
            "test_func", func_body, registers
        )

        assert sm is not None
        assert sm.name == "test_func_sequence_sm"
        assert len(sm.states) >= 3
        assert len(sm.transitions) >= 2
        assert sm.context["function"] == "test_func"
        assert sm.context["type"] == "implicit_sequence"

    def test_extract_global_state_machine(self):
        """Test extracting global state machine from overall register access patterns."""
        extractor = StateMachineExtractor()

        c_code = """
        static int device_init(struct device *dev) {
            writel(0x1, dev->base + REG_CONTROL);
            return 0;
        }
        
        static int device_config(struct device *dev) {
            writel(0x2, dev->base + REG_CONFIG);
            return 0;
        }
        
        static int device_start(struct device *dev) {
            writel(0x3, dev->base + REG_COMMAND);
            return 0;
        }
        
        static void device_stop(struct device *dev) {
            writel(0x0, dev->base + REG_CONTROL);
        }
        """

        registers = {"REG_CONTROL": 0x1000, "REG_CONFIG": 0x1004, "REG_COMMAND": 0x1008}

        sm = extractor._extract_global_state_machine(c_code, registers)

        assert sm is not None
        assert sm.name == "device_global_sm"
        assert "init" in sm.states
        assert "config" in sm.states
        assert len(sm.transitions) > 0
        assert sm.context["type"] == "global_device"

    def test_extract_transitions_from_code(self):
        """Test extracting transitions from code block."""
        extractor = StateMachineExtractor()

        code_block = """
            writel(0x1, dev->base + REG_CONTROL);
            dev_state = STATE_ACTIVE;
            
            if (readl(dev->base + REG_STATUS) & 0x1) {
                dev_state = STATE_DONE;
            }
        """

        registers = {"REG_CONTROL": 0x1000, "REG_STATUS": 0x1004}

        transitions = extractor._extract_transitions_from_code(
            "STATE_IDLE", code_block, registers
        )

        assert len(transitions) > 0
        for transition in transitions:
            assert transition.from_state == "STATE_IDLE"
            assert transition.to_state in ["STATE_ACTIVE", "STATE_DONE"]

    def test_find_delay_between_positions(self):
        """Test finding delay calls between positions in code."""
        extractor = StateMachineExtractor()

        code = """
            writel(0x1, dev->base + REG_CONTROL);
            udelay(100);
            writel(0x2, dev->base + REG_CONFIG);
            
            mdelay(10);
            
            writel(0x3, dev->base + REG_COMMAND);
        """

        # Test finding udelay
        delay1 = extractor._find_delay_between_positions(code, 0, 100)
        assert delay1 == 100  # udelay(100)

        # Test finding mdelay (converted to microseconds)
        delay2 = extractor._find_delay_between_positions(code, 100, 200)
        assert delay2 == 10000  # mdelay(10) = 10000 microseconds

    def test_categorize_function(self):
        """Test categorizing function based on naming patterns."""
        extractor = StateMachineExtractor()

        assert extractor._categorize_function("device_init") == "init"
        assert extractor._categorize_function("probe_device") == "init"
        assert extractor._categorize_function("start_device") == "init"

        assert extractor._categorize_function("device_config") == "config"
        assert extractor._categorize_function("setup_device") == "config"

        assert extractor._categorize_function("device_irq_handler") == "interrupt"
        assert extractor._categorize_function("handle_interrupt") == "interrupt"

        assert extractor._categorize_function("device_exit") == "cleanup"
        assert extractor._categorize_function("remove_device") == "cleanup"

        assert extractor._categorize_function("handle_error") == "error"
        assert extractor._categorize_function("device_fault_handler") == "error"

        assert extractor._categorize_function("process_data") == "runtime"
        assert extractor._categorize_function("device_io") == "runtime"

    def test_get_state_type_for_category(self):
        """Test getting state type for function category."""
        extractor = StateMachineExtractor()

        assert extractor._get_state_type_for_category("init") == StateType.INIT
        assert extractor._get_state_type_for_category("config") == StateType.ACTIVE
        assert extractor._get_state_type_for_category("runtime") == StateType.ACTIVE
        assert extractor._get_state_type_for_category("interrupt") == StateType.ACTIVE
        assert extractor._get_state_type_for_category("cleanup") == StateType.CLEANUP
        assert extractor._get_state_type_for_category("error") == StateType.ERROR
        assert extractor._get_state_type_for_category("unknown") == StateType.ACTIVE

    def test_optimize_state_machines(self):
        """Test optimizing extracted state machines."""
        extractor = StateMachineExtractor()

        # Create some state machines
        sm1 = StateMachine(name="sm1")
        sm1.add_state("IDLE", StateType.INIT)
        sm1.add_state("ACTIVE")
        sm1.add_transition(
            StateTransition(from_state="IDLE", to_state="ACTIVE", trigger="start")
        )

        sm2 = StateMachine(name="sm2")
        sm2.add_state("STATE_A")
        sm2.add_state("STATE_B")
        # No transitions, should be removed

        sm3 = StateMachine(name="sm3")
        sm3.add_state("STATE_X", StateType.INIT)
        # Only one state, should be removed

        extractor.extracted_machines = [sm1, sm2, sm3]

        optimized = extractor.optimize_state_machines()

        assert len(optimized) == 1
        assert optimized[0].name == "sm1"

    def test_generate_analysis_report(self):
        """Test generating analysis report."""
        extractor = StateMachineExtractor()

        # Create some state machines
        sm1 = StateMachine(name="sm1")
        sm1.add_state("IDLE", StateType.INIT)
        sm1.add_state("ACTIVE")
        sm1.add_transition(
            StateTransition(from_state="IDLE", to_state="ACTIVE", trigger="start")
        )
        sm1.calculate_complexity()  # Should be simple

        sm2 = StateMachine(name="sm2")
        sm2.add_state("STATE_A", StateType.INIT)
        sm2.add_state("STATE_B")
        sm2.add_state("STATE_C")
        sm2.add_state("STATE_D")
        sm2.add_transition(
            StateTransition(from_state="STATE_A", to_state="STATE_B", trigger="t1")
        )
        sm2.add_transition(
            StateTransition(from_state="STATE_B", to_state="STATE_C", trigger="t2")
        )
        sm2.add_transition(
            StateTransition(from_state="STATE_C", to_state="STATE_D", trigger="t3")
        )
        sm2.calculate_complexity()  # Should be moderate

        extractor.extracted_machines = [sm1, sm2]

        report = extractor.generate_analysis_report()

        assert report["summary"]["total_state_machines"] == 2
        assert report["summary"]["total_states"] == 6
        assert report["summary"]["total_transitions"] == 4
        assert "avg_complexity" in report["summary"]
        assert len(report["state_machines"]) == 2
        assert "complexity_analysis" in report
        assert "simple" in report["complexity_analysis"]
        assert "moderate" in report["complexity_analysis"]
        assert "complex" in report["complexity_analysis"]

    def test_extract_state_machines_integration(self):
        """Integration test for extracting state machines from driver code."""
        extractor = StateMachineExtractor()

        c_code = """
        #define REG_CONTROL 0x1000
        #define REG_STATUS  0x1004
        #define REG_CONFIG  0x1008
        
        enum device_state {
            STATE_IDLE,
            STATE_ACTIVE,
            STATE_DONE,
            STATE_ERROR
        };
        
        static int device_init(struct device *dev) {
            dev->state = STATE_IDLE;
            writel(0x1, dev->base + REG_CONTROL);
            return 0;
        }
        
        static int device_process(struct device *dev) {
            switch (dev->state) {
                case STATE_IDLE:
                    writel(0x2, dev->base + REG_CONFIG);
                    dev->state = STATE_ACTIVE;
                    break;
                case STATE_ACTIVE:
                    if (readl(dev->base + REG_STATUS) & 0x1) {
                        dev->state = STATE_DONE;
                    }
                    break;
                case STATE_DONE:
                    writel(0x0, dev->base + REG_CONTROL);
                    dev->state = STATE_IDLE;
                    break;
                default:
                    dev->state = STATE_ERROR;
                    break;
            }
            return 0;
        }
        
        static void device_cleanup(struct device *dev) {
            writel(0x0, dev->base + REG_CONTROL);
            dev->state = STATE_IDLE;
        }
        """

        registers = {"REG_CONTROL": 0x1000, "REG_STATUS": 0x1004, "REG_CONFIG": 0x1008}

        state_machines = extractor.extract_state_machines(c_code, registers)

        assert len(state_machines) > 0

        # Should find at least the explicit state machine in device_process
        process_sm = None
        for sm in state_machines:
            if "device_process" in sm.name:
                process_sm = sm
                break

        assert process_sm is not None
        assert "STATE_IDLE" in process_sm.states
        assert "STATE_ACTIVE" in process_sm.states
        assert "STATE_DONE" in process_sm.states
        assert len(process_sm.transitions) >= 3

        # Should also find a global state machine
        global_sm = None
        for sm in state_machines:
            if sm.name == "device_global_sm":
                global_sm = sm
                break

        assert global_sm is not None
        assert "init" in global_sm.states
        assert "cleanup" in global_sm.states


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
