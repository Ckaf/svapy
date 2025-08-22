import pytest
import tempfile
import os
from svapy.parser import extract_module_ports
from pyverilog.vparser.ast import Input, Output


class TestParser:
    """Test cases for Verilog parser functionality."""
    
    def test_parse_counter_module(self):
        """Test parsing a simple counter module."""
        verilog_code = """
        module counter (
            input wire clk,
            input wire rst_n,
            output reg [7:0] count
        );
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n)
                    count <= 8'b0;
                else
                    count <= count + 1;
            end
        endmodule
        """
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(verilog_code)
            temp_file = f.name
        
        try:
            ports_info = extract_module_ports('counter', temp_file)
            
            assert 'clk' in ports_info
            assert 'rst_n' in ports_info
            assert 'count' in ports_info
            
            assert ports_info['clk']['direction'] == Input
            assert ports_info['clk']['width'] == 1
            
            assert ports_info['rst_n']['direction'] == Input
            assert ports_info['rst_n']['width'] == 1
            
            assert ports_info['count']['direction'] == Output
            assert ports_info['count']['width'] == 8
        finally:
            os.unlink(temp_file)
    
    def test_parse_multiplier_module(self):
        """Test parsing a multiplier module with different port types."""
        verilog_code = """
        module multiplier_pipe (
            input wire clk,
            input wire rst_n,
            input wire [7:0] a,
            input wire [7:0] b,
            output reg [15:0] result
        );
            // Implementation
        endmodule
        """
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(verilog_code)
            temp_file = f.name
        
        try:
            ports_info = extract_module_ports('multiplier_pipe', temp_file)
            
            assert len(ports_info) == 5
            
            assert ports_info['clk']['direction'] == Input
            assert ports_info['clk']['width'] == 1
            
            assert ports_info['a']['direction'] == Input
            assert ports_info['a']['width'] == 8
            
            assert ports_info['b']['direction'] == Input
            assert ports_info['b']['width'] == 8
            
            assert ports_info['result']['direction'] == Output
            assert ports_info['result']['width'] == 16
        finally:
            os.unlink(temp_file)
    
    def test_parse_invalid_module(self):
        """Test parsing invalid Verilog code."""
        invalid_code = "invalid verilog code"
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(invalid_code)
            temp_file = f.name
        
        try:
            with pytest.raises(Exception):
                extract_module_ports('invalid', temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_parse_empty_module(self):
        """Test parsing empty module."""
        empty_code = """
        module empty_module (
        );
        endmodule
        """
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(empty_code)
            temp_file = f.name
        
        try:
            ports_info = extract_module_ports('empty_module', temp_file)
            assert len(ports_info) == 0
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.xfail(reason="Parameter width resolution not implemented yet")
    def test_parse_module_with_parameters(self):
        """Test parsing module with parameters."""
        verilog_code = """
        module parameterized_module #(
            parameter WIDTH = 8
        ) (
            input wire clk,
            input wire [WIDTH-1:0] data,
            output wire [WIDTH-1:0] result
        );
            // Implementation
        endmodule
        """
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(verilog_code)
            temp_file = f.name
        
        try:
            ports_info = extract_module_ports('parameterized_module', temp_file)
            
            assert 'clk' in ports_info
            assert 'data' in ports_info
            assert 'result' in ports_info
            
            # Note: Parameter width resolution is not implemented yet
            # This test may need adjustment based on actual implementation
        finally:
            os.unlink(temp_file)
