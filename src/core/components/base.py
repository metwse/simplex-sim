from typing import List
from collections import deque


class Wire:
    """Represents a physical connection carrying a voltage signal.
    It stores the instantaneous value and the history for plotting.
    """

    def __init__(self, name: str):
        self.name = name

        self.effects: List[Component] = []

        self.reset()

    def write_async(self, value: float, timestamp: float):
        """Updates the wire's voltage, without triggering update on components
        connected to it."""
        self.voltage = value

        # Record history for visualization - using deque for O(1) append
        self._history_deque.append(value)
        self._time_deque.append(timestamp)

    def write(self, value: float, timestamp: float):
        """Updates the wire's voltage."""
        self.write_async(value, timestamp)

        self.update = True

    def read(self) -> float:
        """Returns the current voltage on the wire."""
        return self.voltage

    @property
    def history(self) -> List[float]:
        """Convert deque to list only when accessed (lazy conversion)"""
        if self._history_cache is None:
            self._history_cache = list(self._history_deque)
        return self._history_cache

    @property
    def time_axis(self) -> List[float]:
        """Convert deque to list only when accessed (lazy conversion)"""
        if self._time_cache is None:
            self._time_cache = list(self._time_deque)
        return self._time_cache

    def reset(self):
        """Clears the history and wire state."""
        self.voltage: float = 0.0
        # Use deque for O(1) append operations
        self._history_deque = deque()
        self._time_deque = deque()
        # Cache for lazy conversion to list
        self._history_cache = None
        self._time_cache = None
        self.update = False


class Component:
    """Base class for all simulation modules (Generators, Encoders,
    Modulators).

    This acts like a Verilog module.
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire):
        self.input_wire = input_wire
        self.output_wire = output_wire

        input_wire.effects.append(self)

    def tick(self, time: float):
        """Equivalent to 'always @(posedge clk)'.

        Override this method in subclasses to implement logic.
        """
        _ = time
        pass

    def reset(self):
        pass
