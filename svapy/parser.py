from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import ModuleDef, Port
from typing import Dict, Any, Tuple, Optional
import os

def extract_module_ports(module_name: str, filepath: str) -> Dict[str, Dict[str, Any]]:

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        ast, _ = parse([filepath])
        
        target_module: Optional[ModuleDef] = None
        for definition in ast.description.definitions:
            if hasattr(definition, 'name') and definition.name == module_name:
                target_module = definition
                break
        
        if not target_module:
            raise ValueError(f"Module '{module_name}' not found in file")
        
        ports_info: Dict[str, Dict[str, Any]] = {}
        if not (hasattr(target_module, 'portlist') and target_module.portlist and hasattr(target_module.portlist, 'ports')):
            return ports_info
            
        ports = target_module.portlist.ports
        for p in ports:
            if not (hasattr(p, 'first') and p.first):
                continue
                
            direction = type(p.first)
            width = 1
            
            # Calculate width if available
            if (hasattr(p.first, 'width') and p.first.width is not None
                    and hasattr(p.first.width, 'msb') and hasattr(p.first.width, 'lsb')
                    and hasattr(p.first.width.msb, 'value') and hasattr(p.first.width.lsb, 'value')):
                width = (int(p.first.width.msb.value) - int(p.first.width.lsb.value)) + 1

            ports_info[p.first.name] = {
                'direction': direction,
                'width': width
            }
        
        return ports_info
    
    except Exception as e:
        raise RuntimeError(f"Parsing error: {str(e)}")
    
    
