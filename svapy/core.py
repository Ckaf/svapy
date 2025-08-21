import datetime
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

from pyverilog.vparser.ast import Input, Output, Inout

def get_template_environment():
    """
    Creates and returns a Jinja2 template environment
    
    :return: Jinja2 Environment instance
    """
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    return env

def generate_module_docstring(module_name, ports_info):
    """
    Generates a Python docstring describing a Verilog module using Jinja2 template
    
    :param module_name: Name of the Verilog module
    :param ports_info: Dictionary containing port information
    :return: Formatted docstring as a multi-line string
    """
    env = get_template_environment()
    template = env.get_template('module_docstring.j2')
    
    # Prepare template context
    context = {
        'module_name': module_name,
        'ports_info': ports_info
    }
    
    return template.render(context)

def generate_module(module_name, ports_info):
    """
    Generates Python code for a function drive_<module_name> with Verilog bit-level representation
    and adds output value assertions only when output sequence is not None.
    Uses Jinja2 template for code generation.
    """
    input_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Input']
    output_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Output']
    all_ports = input_ports + output_ports

    env = get_template_environment()
    template = env.get_template('module_interface.j2')
    
    # Prepare template context
    context = {
        'module_name': module_name,
        'ports_info': ports_info,
        'input_ports': input_ports,
        'output_ports': output_ports,
        'all_ports': all_ports
    }
    
    return template.render(context)

def generate_runner(module_name, ports_info):
    """
    Generates proper Hypothesis-based test runner with correct property-based testing approach.
    Uses Jinja2 template for code generation.
    """
    input_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Input']
    output_ports = [p for p, info in ports_info.items() if info['direction'].__name__ == 'Output']
    all_ports = input_ports + output_ports

    # Calculate maximum values for each port
    port_max_values = {}
    for port, info in ports_info.items():
        if info['width'] > 1:
            port_max_values[port] = (1 << info['width']) - 1

    env = get_template_environment()
    template = env.get_template('test_runner.j2')
    
    # Prepare template context
    context = {
        'module_name': module_name,
        'ports_info': ports_info,
        'input_ports': input_ports,
        'output_ports': output_ports,
        'all_ports': all_ports,
        'port_max_values': port_max_values
    }
    
    return template.render(context)
