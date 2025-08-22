import pytest
import tempfile
import os
import subprocess
import sys
from pathlib import Path


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Copy main.py to test directory
        import shutil
        main_py_path = os.path.join(self.original_cwd, 'main.py')
        if os.path.exists(main_py_path):
            shutil.copy(main_py_path, self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        os.chdir(self.original_cwd)
        # Cleanup temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow_counter(self):
        """Test complete workflow with counter module."""
        # Create a simple counter module
        counter_v = """
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
        
        with open('counter.v', 'w') as f:
            f.write(counter_v)
        
        # Run the main script
        result = subprocess.run([
            sys.executable, 'main.py', 'counter', 'counter.v'
        ], capture_output=True, text=True)
        
        # Check that files were generated
        assert os.path.exists('gen/counter_interface.py')
        assert os.path.exists('gen/run_counter.py')
        # Note: gen/tests/ directory is created only when testbench is generated
        
        # Check that test files contain expected content
        with open('gen/counter_interface.py', 'r') as f:
            interface_content = f.read()
            assert 'def drive_counter(' in interface_content
        
        with open('gen/run_counter.py', 'r') as f:
            runner_content = f.read()
            assert '@given(' in runner_content
            assert 'def test_counter(' in runner_content
    
    def test_full_workflow_multiplier(self):
        """Test complete workflow with multiplier module."""
        # Create a simple multiplier module
        multiplier_v = """
        module multiplier (
            input wire clk,
            input wire [7:0] a,
            input wire [7:0] b,
            output reg [15:0] result
        );
            always @(posedge clk) begin
                result <= a * b;
            end
        endmodule
        """
        
        with open('multiplier.v', 'w') as f:
            f.write(multiplier_v)
        
        # Run the main script
        result = subprocess.run([
            sys.executable, 'main.py', 'multiplier', 'multiplier.v'
        ], capture_output=True, text=True)
        
        # Check that files were generated
        assert os.path.exists('gen/multiplier_interface.py')
        assert os.path.exists('gen/run_multiplier.py')
        
        # Check that test files contain expected content
        with open('gen/multiplier_interface.py', 'r') as f:
            interface_content = f.read()
            assert 'def drive_multiplier(' in interface_content
            assert 'a_seq' in interface_content
            assert 'b_seq' in interface_content
        
        with open('gen/run_multiplier.py', 'r') as f:
            runner_content = f.read()
            assert '@given(' in runner_content
            assert 'def test_multiplier(' in runner_content
    
    def test_makefile_workflow(self):
        """Test Makefile workflow."""
        # Create a simple module
        test_module_v = """
        module test_module (
            input wire clk,
            input wire [3:0] data,
            output reg [3:0] result
        );
            always @(posedge clk) begin
                result <= data;
            end
        endmodule
        """
        
        with open('test_module.v', 'w') as f:
            f.write(test_module_v)
        
        # Create a simple Makefile
        makefile_content = """
DESIGN = test_module.v
MODULE_NAME = test_module

# Copy the main Makefile content here for testing
TEST_DIR = gen/tests
TB_FILES := $(wildcard $(TEST_DIR)/*.sv)

BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin
ifeq ($(wildcard $(BUILD_DIR)),)
  $(shell mkdir -p $(BIN_DIR))
endif

.PHONY: all clean sim generate test python-test help

# Generate test files
generate:
	@echo "Generating test files for $(MODULE_NAME) from $(DESIGN)..."
	python main.py $(MODULE_NAME) $(DESIGN)
	@echo "== Test generation complete"
        """
        
        with open('Makefile', 'w') as f:
            f.write(makefile_content)
        
        # Test generate target
        result = subprocess.run(['make', 'generate'], capture_output=True, text=True)
        assert result.returncode == 0
        
        # Check that files were generated
        assert os.path.exists('gen/test_module_interface.py')
        assert os.path.exists('gen/run_test_module.py')
    
    def test_error_handling_invalid_module(self):
        """Test error handling with invalid module."""
        # Create invalid Verilog
        invalid_v = "invalid verilog code"
        
        with open('invalid.v', 'w') as f:
            f.write(invalid_v)
        
        # Run the main script - should handle errors gracefully
        result = subprocess.run([
            sys.executable, 'main.py', 'invalid', 'invalid.v'
        ], capture_output=True, text=True)
        
        # Should not crash, but may return error
        # The exact behavior depends on error handling implementation
    
    def test_template_consistency(self):
        """Test that generated templates are consistent."""
        # Create a simple module
        simple_v = """
        module simple (
            input wire clk,
            output reg [7:0] out
        );
            always @(posedge clk) begin
                out <= 8'hAA;
            end
        endmodule
        """
        
        with open('simple.v', 'w') as f:
            f.write(simple_v)
        
        # Generate multiple times
        for i in range(3):
            result = subprocess.run([
                sys.executable, 'main.py', 'simple', 'simple.v'
            ], capture_output=True, text=True)
            assert result.returncode == 0
        
        # Read generated files
        with open('gen/simple_interface.py', 'r') as f:
            interface_content = f.read()
        
        with open('gen/run_simple.py', 'r') as f:
            runner_content = f.read()
        
        # Check that content is reasonable
        assert 'def drive_simple(' in interface_content
        assert 'def test_simple(' in runner_content
        assert 'clk_seq' in interface_content
        assert 'out_seq' in interface_content
