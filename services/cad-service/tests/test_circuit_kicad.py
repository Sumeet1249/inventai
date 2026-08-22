import pytest
from services.cad_service.schemas.circuit_schemas import CircuitGraph, Component, Pin, Net, NetNode
from services.cad_service.exporters.kicad_exporter import KiCadExporter

def test_circuit_graph_kicad_export():
    # 1. Define Pins
    r_pin_1 = Pin(id="1", name="~", x=-1.0, y=0.0)
    r_pin_2 = Pin(id="2", name="~", x=1.0, y=0.0)
    
    led_pin_1 = Pin(id="1", name="A", x=-1.2, y=0.0)
    led_pin_2 = Pin(id="2", name="K", x=1.2, y=0.0)
    
    # 2. Define Components
    r1 = Component(
        id="R1",
        value="1K",
        footprint="Resistor_SMD:R_0805_2012Metric",
        x=10.0, y=10.0, rotation=90,
        pins=[r_pin_1, r_pin_2]
    )
    
    d1 = Component(
        id="D1",
        value="LED_Red",
        footprint="LED_SMD:LED_0805_2012Metric",
        x=10.0, y=20.0, rotation=90,
        pins=[led_pin_1, led_pin_2]
    )
    
    # 3. Define Nets
    net1 = Net(
        id=1,
        name="Net-(D1-Pad1)",
        nodes=[
            NetNode(component_id="R1", pin_id="2"),
            NetNode(component_id="D1", pin_id="1")
        ]
    )
    
    # 4. Create Graph
    graph = CircuitGraph(
        components=[r1, d1],
        nets=[net1]
    )
    
    # 5. Export to KiCad PCB
    kicad_output = KiCadExporter.export(graph)
    
    # 6. Verify contents
    assert "(kicad_pcb (version 20211014)" in kicad_output
    assert '(net 1 "Net-(D1-Pad1)")' in kicad_output
    assert 'footprint "Resistor_SMD:R_0805_2012Metric"' in kicad_output
    assert 'fp_text reference "R1"' in kicad_output
    assert '(net 1 "Net-(D1-Pad1)")' in kicad_output
    assert 'pad "2" smd rect' in kicad_output
    assert '(size 1.5 1.5)' in kicad_output
    
    print("\n--- Generated KiCad PCB ---")
    print(kicad_output)
    print("---------------------------\n")

