from .components import Wire, Component
from .types import SignalGenerator

from typing import List


class Simulation:
    """The main engine that drives the clock."""

    def __init__(self,
                 input_wire: Wire,
                 input_function: SignalGenerator,
                 dt: float = 0.01):
        self.dt = dt
        self.current_time: float = 0.0

        self.wires: List[Wire] = []
        self.components: List[Component] = []

        self.input_wire = input_wire

        self.input_function = input_function

    def add_component(self, component: Component):
        """Registers a component and automatically registers its connected
        wires.
        """

        if component in self.components:
            return

        self.components.append(component)

        self.add_wire(component.input_wire)
        self.add_wire(component.output_wire)

    def add_wire(self, wire: Wire):
        if wire not in self.wires:
            self.wires.append(wire)

    def advance(self):
        """Executes one time-step of the simulation.

        Algorithm:
        1. Write new value to the System Input (Source).
        2. Advance the clock.
        3. Propagation Loop:
           - Find all components connected to updated wires.
           - Run their logic.
           - If they write to their output wires, those wires get flagged
             `update=True`.
           - Repeat until the signal stabilizes (no more updates).
        """

        self.input_wire.write_async(self.input_function(self.current_time),
                                    self.current_time)

        updates = set(self.input_wire.effects)
        while len(updates) > 0:
            to_update = list(updates)
            updates = set()

            for component in to_update:
                component.tick(self.current_time)

            for wire in self.wires:
                if wire.update:
                    wire.update = False
                    updates.update(wire.effects)

        self.current_time += self.dt

    def reset(self):
        self.current_time = 0.0
        for wire in self.wires:
            wire.reset()
        for component in self.components:
            component.reset()
