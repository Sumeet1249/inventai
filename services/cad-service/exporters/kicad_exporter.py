from schemas.circuit_schemas import CircuitGraph, Net, Component
from typing import Dict

class KiCadExporter:
    """
    Exports a CircuitGraph to a KiCad PCB (.kicad_pcb) s-expression format.
    """
    
    @staticmethod
    def export(graph: CircuitGraph) -> str:
        lines = []
        
        # Header
        lines.append("(kicad_pcb (version 20211014) (generator inventai_kicad_exporter)")
        lines.append('  (general')
        lines.append('    (thickness 1.6)')
        lines.append('  )')
        lines.append('  (paper "A4")')
        
        # Default empty net
        lines.append('  (net 0 "")')
        
        # Nets
        # Map node (comp_id, pin_id) to net_id to easily add to pads later
        pad_to_net: Dict[tuple[str, str], tuple[int, str]] = {}
        
        for net in graph.nets:
            lines.append(f'  (net {net.id} "{net.name}")')
            for node in net.nodes:
                pad_to_net[(node.component_id, node.pin_id)] = (net.id, net.name)
        
        # Components as Footprints
        for comp in graph.components:
            lines.append(f'  (footprint "{comp.footprint}" (layer "F.Cu")')
            lines.append(f'    (at {comp.x} {comp.y} {comp.rotation})')
            lines.append(f'    (fp_text reference "{comp.id}" (at 0 -2) (layer "F.SilkS")')
            lines.append('      (effects (font (size 1 1) (thickness 0.15)))')
            lines.append('    )')
            lines.append(f'    (fp_text value "{comp.value}" (at 0 2) (layer "F.Fab")')
            lines.append('      (effects (font (size 1 1) (thickness 0.15)))')
            lines.append('    )')
            
            # Pads/Pins
            for pin in comp.pins:
                net_info = pad_to_net.get((comp.id, pin.id))
                net_expr = f'\n      (net {net_info[0]} "{net_info[1]}")' if net_info else ''
                
                # Using a generic SMD pad shape as foundation. 
                # Real footprint pads would have accurate sizes/shapes.
                lines.append(f'    (pad "{pin.id}" smd rect (at {pin.x} {pin.y} {comp.rotation}) (size 1.5 1.5) (layers "F.Cu" "F.Paste" "F.Mask"){net_expr}')
                lines.append('    )')
            
            lines.append('  )') # End footprint
        
        lines.append(")") # End kicad_pcb
        
        return "\n".join(lines)
