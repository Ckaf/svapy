import datetime
import sys
import os
from svapy.parser import extract_module_ports
from svapy.core import generate_module_docstring, generate_module, generate_runner

def main():
    if len(sys.argv) < 3:
        print("Usage: poetry run python main.py <module_name> <file_path.v>")
        sys.exit(1)
    
    module_name = sys.argv[1]
    file_path = sys.argv[2]
    
    try:
        ports = extract_module_ports(module_name, file_path)
        os.makedirs('gen', exist_ok=True)

        docstring = generate_module_docstring(module_name, ports)
        interface_path = os.path.join('gen', f"{module_name}_interface.py")
        interface_code = generate_module(module_name, ports)
        with open(interface_path, "w") as f:
            f.write("# Auto-generated interface\n")
            f.write(f"# Module: {module_name}\n")
            f.write(f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(interface_code)
        print(f"Interface generated: {interface_path}")
        # print (docstring)

        runner_code = generate_runner(module_name, ports)
        runner_path = os.path.join('gen', f"run_{module_name}.py")
        with open(runner_path, 'w') as f:
            f.write(runner_code)
        print(f"Runner generated: {runner_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    

if __name__ == "__main__":
    main()
