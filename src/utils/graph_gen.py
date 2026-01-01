from src.core.engine import Simulation

import graphviz


def generate_topology_graph(sim: Simulation) -> graphviz.Digraph:
    """Generates a graphviz of simulation state.
    """
    dot = graphviz.Digraph(comment='Simulation Topology', format='png')
    dot.attr(rankdir='LR')
    dot.attr('node', fontname='Arial')

    for wire in sim.wires:
        dot.node(str(id(wire)), wire.name, shape='plaintext', fontsize='10')

    for i, comp in enumerate(sim.components):
        comp_id = f"comp_{i}"
        comp_label = type(comp).__name__

        # component box
        dot.node(comp_id, comp_label, shape='box',
                 style='filled', fillcolor='lightgrey', height='0.6')

        # input wire -> component
        dot.edge(str(id(comp.input_wire)), comp_id)

        # component -> output wire
        dot.edge(comp_id, str(id(comp.output_wire)))

    return dot
