# Svapy

**Status**: Early prototype

Svapy is a framework for **Property-Based Testing of Hardware Designs**. It generates the testing infrastructure and test vectors, while you define the properties that your hardware design must satisfy. This enables systematic verification through automated test generation and simulation.

## What Svapy Does

Svapy creates the foundation for property-based testing of your Verilog modules:

- **🔍 Analyzes Verilog Modules**: Automatically parses your Verilog code and extracts port information
- **🧪 Generates Test Infrastructure**: Creates Hypothesis-based test runners with test vector generation
- **⚡ Produces Testbenches**: Generates SystemVerilog testbenches with VCD waveform dumping
- **📝 Creates Documentation**: Automatically generates module documentation and interface files
- **🔄 Enables Continuous Testing**: Provides a foundation for automated hardware verification workflows

## Key Features

- **Test Infrastructure Generation**: Svapy analyzes your module and generates the testing framework - you focus on defining properties
- **Property-Based Testing Foundation**: Uses Hypothesis to generate thousands of test vectors, while you specify what properties to verify
- **Waveform Analysis**: Generates VCD files for detailed signal analysis and debugging
- **Multiple Test Strategies**: Supports different input generation strategies (random, constrained, etc.)
- **Extensible Architecture**: Easy to add custom test patterns and verification strategies

## Quick Start

### Installation

```bash
# Install dependencies
poetry install
```

### Basic Usage

```bash
# Generate tests for your Verilog module
poetry run python main.py counter example/counter.v
```

This single command generates:
- **Python Interface**: `gen/counter_interface.py` - Functions to drive your module
- **Test Runner**: `gen/run_counter.py` - Property-based test suite
- **Testbenches**: `gen/tests/counter_tb_*.sv` - SystemVerilog testbenches
- **Waveforms**: `gen/dump/counter_tb_*.vcd` - VCD files for waveform analysis

### Running Your Tests

```bash
# Execute the generated test suite
poetry run python gen/run_counter.py
```

## Example: Testing a Counter Module

Given this Verilog counter:

```verilog
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
```

Svapy automatically generates:

### 1. Python Interface
```python
def drive_counter(clk_seq, rst_n_seq, count_seq=None):
    """
    Drives the counter module with test sequences.
    Generates SystemVerilog testbench and VCD waveforms.
    """
    # Automatically generates testbench with your sequences
```

### 2. Property-Based Test Suite
```python
@given(
    clk_seq=st.lists(st.booleans(), min_size=10, max_size=100),
    rst_n_seq=st.lists(st.booleans(), min_size=10, max_size=100),
    count_seq=st.just([0]*100)
)
def test_counter(clk_seq, rst_n_seq, count_seq):
    """
    Property-based test framework - you define the properties to verify.
    For example:
    - Counter should increment on each clock cycle when not reset
    - Counter should reset to zero when rst_n is low
    - Counter should not overflow beyond 8 bits
    """
    # TODO: Add your property assertions here
    # Example properties:
    # assert counter_increments_correctly(clk_seq, rst_n_seq, count_seq)
    # assert counter_resets_properly(clk_seq, rst_n_seq, count_seq)
```

### 3. SystemVerilog Testbench
```systemverilog
module counter_tb;
    reg clk, rst_n;
    wire [7:0] count;
    
    counter dut(clk, rst_n, count);
    
    initial begin
        $dumpfile("counter_tb.vcd");
        $dumpvars(0, counter_tb);
        
        // Test vectors automatically generated from Python
        // VCD waveforms for analysis
    end
endmodule
```

## Use Cases

### Hardware Verification
- **RTL Verification**: Comprehensive testing of Register Transfer Level designs with custom properties
- **Protocol Testing**: Verify communication protocols and interfaces with specific behavioral requirements
- **Corner Case Discovery**: Find edge cases and timing issues through extensive test vector generation
- **Regression Testing**: Maintain test suites as designs evolve while preserving property definitions

### Design Validation
- **Functional Verification**: Ensure modules satisfy your specific functional requirements
- **Performance Analysis**: Test across different input patterns and frequencies with custom metrics
- **Integration Testing**: Verify module interactions and system-level behavior with defined constraints

### Development Workflow
- **Continuous Integration**: Automate testing in CI/CD pipelines with property-based verification
- **Design Reviews**: Generate test reports for design review processes with clear property coverage
- **Documentation**: Auto-generate module documentation and test reports with property specifications

## Dependencies

- **pyverilog** - Verilog parsing and AST manipulation
- **hypothesis** - Property-based testing framework
- **pytest** - Test execution and reporting
- **vcdvcd** - VCD file parsing and analysis

## Development

### Adding Custom Test Patterns

Svapy is designed to be extensible. You can:
- Add custom Hypothesis strategies for specific input patterns
- Create specialized test templates for different module types
- Implement custom verification functions for domain-specific requirements
- Define your own property assertions and verification logic

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
