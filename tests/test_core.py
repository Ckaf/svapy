import pytest
import tempfile
import os
from svapy.core import (
    generate_module_docstring,
    generate_module,
    generate_runner,
    get_template_environment
)
from pyverilog.vparser.ast import Input, Output


class TestCore:
    """Test cases for core code generation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.sample_ports_info = {
            'clk': {'direction': Input, 'width': 1},
            'rst_n': {'direction': Input, 'width': 1},
            'data': {'direction': Input, 'width': 8},
            'result': {'direction': Output, 'width': 8}
        }
    
    def test_get_template_environment(self):
        """Test template environment creation."""
        env = get_template_environment()
        assert env is not None
        assert hasattr(env, 'get_template')
    
    def test_generate_module_docstring(self):
        """Test module docstring generation."""
        docstring = generate_module_docstring('test_module', self.sample_ports_info)
        
        assert 'test_module' in docstring
        assert 'clk' in docstring
        assert 'rst_n' in docstring
        assert 'data' in docstring
        assert 'result' in docstring
        assert 'Input' in docstring
        assert 'Output' in docstring
        assert '1-bit' in docstring
        assert '8-bit' in docstring
    
    def test_generate_module_interface(self):
        """Test module interface generation."""
        interface_code = generate_module('test_module', self.sample_ports_info)
        
        assert 'def drive_test_module' in interface_code
        assert 'clk_seq' in interface_code
        assert 'rst_n_seq' in interface_code
        assert 'data_seq' in interface_code
        assert 'result_seq' in interface_code
        assert 'testbench' in interface_code
    
    def test_generate_runner(self):
        """Test test runner generation."""
        runner_code = generate_runner('test_module', self.sample_ports_info)
        
        assert '@given' in runner_code
        assert 'def test_test_module' in runner_code
        assert 'st.lists' in runner_code
        assert 'st.booleans' in runner_code
        assert 'st.integers' in runner_code
        assert 'hypothesis' in runner_code
    
    def test_generate_with_empty_ports(self):
        """Test generation with empty ports info."""
        empty_ports = {}
        
        docstring = generate_module_docstring('empty_module', empty_ports)
        assert 'empty_module' in docstring
        
        interface = generate_module('empty_module', empty_ports)
        assert 'def drive_empty_module' in interface
        
        runner = generate_runner('empty_module', empty_ports)
        assert 'def test_empty_module' in runner
    
    def test_generate_with_single_port(self):
        """Test generation with single port."""
        single_port = {'clk': {'direction': Input, 'width': 1}}
        
        docstring = generate_module_docstring('single_port', single_port)
        assert 'clk' in docstring
        
        interface = generate_module('single_port', single_port)
        assert 'clk_seq' in interface
        
        runner = generate_runner('single_port', single_port)
        assert 'clk_seq' in runner
    
    def test_generate_with_wide_bus(self):
        """Test generation with wide bus."""
        wide_bus = {'data': {'direction': Input, 'width': 64}}
        
        docstring = generate_module_docstring('wide_bus', wide_bus)
        assert '64-bit' in docstring
        
        interface = generate_module('wide_bus', wide_bus)
        assert 'data_seq' in interface
        
        runner = generate_runner('wide_bus', wide_bus)
        assert 'data_seq' in runner
        assert 'max_value=' in runner  # Should have max_value for wide bus
    
    def test_template_rendering_consistency(self):
        """Test that templates render consistently."""
        module_name = 'consistency_test'
        
        # Generate multiple times and compare
        docstring1 = generate_module_docstring(module_name, self.sample_ports_info)
        docstring2 = generate_module_docstring(module_name, self.sample_ports_info)
        assert docstring1 == docstring2
        
        interface1 = generate_module(module_name, self.sample_ports_info)
        interface2 = generate_module(module_name, self.sample_ports_info)
        assert interface1 == interface2
        
        runner1 = generate_runner(module_name, self.sample_ports_info)
        runner2 = generate_runner(module_name, self.sample_ports_info)
        assert runner1 == runner2
