from pyverilog.vparser.parser import parse
import os

def extract_module_ports(module_name, filepath):

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        ast, _ = parse([filepath])
        
        target_module = None
        for definition in ast.description.definitions:
            if definition.name == module_name:
                target_module = definition
                break
        
        if not target_module:
            raise ValueError(f"Module '{module_name}' not found in file")
        
        ports_info = {}
        ports = target_module.portlist.ports
        for p in ports:
            direction = type(p.first)
            width = 1
            if p.first.width is not None:
                width = (int(p.first.width.msb.value) - int(p.first.width.lsb.value)) + 1

            ports_info[p.first.name] = {
                'direction': direction,
                'width': width
            }
        
        return ports_info
    
    except Exception as e:
        raise RuntimeError(f"Parsing error: {str(e)}")
    
    
