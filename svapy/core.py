import datetime
import os
from datetime import datetime

from pyverilog.vparser.ast import Input, Output, Inout

def generate_module_docstring(module_name, ports_info):
    """
    Generates a Python docstring describing a Verilog module
    
    :param module_name: Name of the Verilog module
    :param ports_info: Dictionary containing port information
    :return: Formatted docstring as a multi-line string
    """
    # Header section
    docstring = f'"""{module_name} Module\n\n'
    docstring += f"Hardware description for the {module_name} Verilog module.\n\n"
    
    # Ports table
    docstring += "Ports:\n"
    docstring += "| Port        | Direction   | Width  |\n"
    docstring += "|-------------|-------------|--------|\n"
    
    # Sort ports alphabetically for consistent output
    for port, info in sorted(ports_info.items()):
        # Get clean direction name
        direction = str(info['direction']).split('.')[-1].replace("'>", "")
        
        # Format width information
        width = info['width']
        width_str = f"{width}-bit" if width > 1 else "1-bit"
        
        docstring += f"| {port.ljust(12)}| {direction.ljust(12)}| {str(width_str).ljust(7)}|\n"
    
    # Footer section
    docstring += "\nFunctional Description:\n"
    docstring += "    [Add detailed description of module functionality here]\n\n"
    docstring += "Parameters:\n"
    docstring += "    [List any module parameters here]\n\n"
    docstring += "Timing Characteristics:\n"
    docstring += "    [Add timing requirements and characteristics]\n"
    docstring += '"""'
    
    return docstring

def generate_module(module_name, ports_info):
    """
    Generates Python code for a function drive_<module_name> with Verilog bit-level representation
    and adds output value assertions only when output sequence is not None.
    """
    input_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Input']
    output_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Output']
    all_ports = input_ports + output_ports

    # Add default None for output ports in function parameters
    func_params = []
    for p in input_ports:
        func_params.append(f"{p}_seq")
    for p in output_ports:
        func_params.append(f"{p}_seq=None")  # Default None for outputs

    lines = [
        "import os",
        "from datetime import datetime",
        "",
        f"def drive_{module_name}({', '.join(func_params)}):"
    ]
    
    # Add sequence length validation
    lines += [
        "    # Ensure sequences have equal length",
        "    non_none_seqs = []",
        "    # Collect all non-None sequences",
        f"    for seq in [{', '.join(f'{p}_seq' for p in input_ports)}]:",
        "        if seq is not None:",
        "            non_none_seqs.append(seq)",
        "    for seq in [" + ", ".join(f"{p}_seq" for p in output_ports) + "]:",
        "        if seq is not None:",
        "            non_none_seqs.append(seq)",
        "    ",
        "    if non_none_seqs:",
        "        num_cycles = min(len(seq) for seq in non_none_seqs)",
        "    else:",
        "        num_cycles = 0  # No sequences provided",
        "    ",
        "    # Trim sequences to min length",
        f"    for port in [{', '.join(f'\"{p}\"' for p in input_ports)}]:",
        "        if locals()[f'{port}_seq'] is not None:",
        "            locals()[f'{port}_seq'] = locals()[f'{port}_seq'][:num_cycles]",
        "    for port in [" + ", ".join(f'\"{p}\"' for p in output_ports) + "]:",
        "        if locals()[f'{port}_seq'] is not None:",
        "            locals()[f'{port}_seq'] = locals()[f'{port}_seq'][:num_cycles]",
        ""
    ]
    
    # Prepare testbench folder and filename
    lines += [
        "    # Prepare testbench folder and filename",
        "    tb_dir = os.path.join('gen', 'tests')",
        "    os.makedirs(tb_dir, exist_ok=True)",
        "    # Create dump directory for VCD files",
        "    dump_dir = os.path.join('gen', 'dump')",
        "    os.makedirs(dump_dir, exist_ok=True)",
        f"    base = '{module_name}_tb'",
        "    existing = os.listdir(tb_dir)",
        "    idx = 0",
        "    while f'{base}_{idx}.sv' in existing:",
        "        idx += 1",
        "    tb_name = f'{base}_{idx}.sv'",
        "    tb_path = os.path.join(tb_dir, tb_name)",
        "    # VCD file path",
        "    vcd_name = f'{base}_{idx}.vcd'",
        "    vcd_path = os.path.join(dump_dir, vcd_name)",
        "",
        "    # Write testbench file",
        "    with open(tb_path, 'w') as f:",
        f"        f.write('// Auto-generated testbench for {module_name} on ' + str(datetime.now().isoformat()) + '\\n')",
        "        f.write('`timescale 1ns/1ps\\n')",
        f"        f.write('module {module_name}_tb;\\n')",
    ]

    # Signal declarations
    for p in all_ports:
        width = ports_info[p]['width']
        decl = f"logic [{width-1}:0] {p};" if width > 1 else f"logic {p};"
        lines.append(f"        f.write('    {decl}\\n')")
    
    # Add cycle counter declaration
    lines.append("        f.write('    integer cycle;  // Test cycle counter\\n')")
    
    # Instantiate DUT
    conn = ", ".join(f".{p}({p})" for p in all_ports)
    lines += [
        "        f.write('\\n    // Instantiate DUT\\n')",
        f"        f.write('    {module_name} dut ({conn});\\n')",
        "",
        "        # Add VCD dumping",
        "        f.write('\\n    // VCD Dumping\\n')",
        "        f.write('    initial begin\\n')",
        f"        f.write('        $dumpfile(\\\"' + vcd_path + '\\\");\\n')",
        f"        f.write('        $dumpvars(0, {module_name}_tb);\\n')",
        "        f.write('    end\\n')",
        "",
        "        f.write('\\n    initial begin\\n')",
        "        f.write('        cycle = 0;  // Initialize counter\\n')",
        "",
        "        # Generate test vectors",
        "        for cycle in range(num_cycles):"
    ]

    # Input value assignments
    for p in input_ports:
        width = ports_info[p]['width']
        if width == 1:
            lines.append(f"            if {p}_seq is not None:")
            lines.append(f"                f.write('        {p} = 1\\\'b' + str({p}_seq[cycle]) + ';\\n')")
        else:
            lines.append(f"            if {p}_seq is not None:")
            lines.append(f"                f.write('        {p} = {width}\\'d' + str({p}_seq[cycle]) + ';\\n')")
    
    # Output value assertions only if sequence is not None
    for p in output_ports:
        width = ports_info[p]['width']
        lines.append(f"            # Check for {p} if sequence is provided")
        lines.append(f"            if {p}_seq is not None:")
        
        if width == 1:
            lines.append(f"                f.write('        if ({p} !== 1\\\'b' + str({p}_seq[cycle]) + ') begin\\n')")
            lines.append(f"                f.write('            $error(\\\"Cycle %0d: {p}: expected=%0d, actual=%0d\\\", cycle, 1\\\'b' + str({p}_seq[cycle]) + ', {p});\\n')")
            lines.append(f"                f.write('        end\\n')")
        else:
            lines.append(f"                f.write('        if ({p} !== {width}\\'d' + str({p}_seq[cycle]) + ') begin\\n')")
            lines.append(f"                f.write('            $error(\\\"Cycle %0d: {p}: expected=%0d, actual=%0d\\\", cycle, {width}\\'d' + str({p}_seq[cycle]) + ', {p});\\n')")
            lines.append(f"                f.write('        end\\n')")
    
    # Add delay for signal propagation
    lines.append("            f.write('        #1;  // Wait for signals to propagate\\n')")

    # Increment cycle counter
    lines.append("            f.write('        cycle = cycle + 1;  // Next test cycle\\n')")
    
    # Finish simulation
    lines += [
        "        f.write('        $finish;\\n')",
        "        f.write('    end\\nendmodule\\n')",
        "",
        "    print(f'Testbench generated: {tb_path}')",
        "    print(f'VCD dump file: {vcd_path}')"
    ]
    return '\n'.join(lines)

    
def generate_runner(module_name, ports_info):
    """
    Generates proper Hypothesis-based test runner with correct property-based testing approach.
    """
    input_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Input']
    output_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Output']
    all_ports = input_ports + output_ports

    lines = [
        f"# Auto-generated Hypothesis test for module {module_name}",
        "import os",
        "import pytest",
        "import hypothesis.strategies as st",
        "from hypothesis import given, settings, HealthCheck",
        f"from {module_name}_interface import drive_{module_name}",
        "",
        "# Hypothesis configuration",
        "@settings(",
        "    max_examples=20,",
        "    deadline=None,",
        "    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]",
        ")",
        "@given("
    ]
    
    # Generate strategies for input ports
    port_strategies = []
    for port in input_ports:
        width = ports_info[port]['width']
        if width == 1:
            port_strategies.append(f"    {port}_seq=st.lists(st.booleans(), min_size=10, max_size=100)")
        else:
            max_val = (1 << width) - 1
            port_strategies.append(f"    {port}_seq=st.lists(st.integers(min_value=0, max_value={max_val}), min_size=10, max_size=100)")
    
    # Add dummy strategies for outputs
    for port in output_ports:
        width = ports_info[port]['width']
        if width == 1:
            port_strategies.append(f"    {port}_seq=st.just([0]*100)")
        else:
            port_strategies.append(f"    {port}_seq=st.just([0]*100)")
    
    lines.append(",\n".join(port_strategies))
    lines.append(")")
    lines.append(f"def test_{module_name}(")
    lines.append(", ".join(f"{p}_seq" for p in all_ports))
    lines.append("):")
    
    # Convert boolean sequences to 0/1
    for port in input_ports:
        if ports_info[port]['width'] == 1:
            lines.append(f"    # Convert boolean to 0/1 for {port}")
            lines.append(f"    {port}_seq = [1 if x else 0 for x in {port}_seq]")
    
    # Ensure all sequences have same length
    lines.append("")
    lines.append("    # Ensure all sequences have same length")
    lines.append("    num_cycles = min(len(seq) for seq in [" + ", ".join(f"{p}_seq" for p in all_ports) + "])")
    for port in all_ports:
        lines.append(f"    {port}_seq = {port}_seq[:num_cycles]")
    
    # Function call
    lines.append("")
    lines.append("    # Generate testbench with sequences")
    args = ", ".join(f"{port}_seq" for port in all_ports)
    lines.append(f"    drive_{module_name}({args})")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    pytest.main([__file__])")

    return "\n".join(lines)
