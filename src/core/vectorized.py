
import numpy as np
from typing import List, Set
from .components import Wire, Component
import time

class VectorizedWire(Wire):
    """A Wire that can handle NumPy arrays for batch processing."""
    
    __slots__ = ['buffer', 'history_buffer', 'time_buffer']

    def __init__(self, name: str):
        super().__init__(name)
        self.buffer = np.array([], dtype=np.float64)
        
        # We will use these lists of arrays for history to avoid reallocating huge arrays constantly
        self.history_buffer: List[np.ndarray] = [] 
        self.time_buffer: List[np.ndarray] = []

    def write_buffer(self, values: np.ndarray, times: np.ndarray):
        """Write a batch of values."""
        self.buffer = values
        self.history_buffer.append(values)
        self.time_buffer.append(times)
        
    def read_buffer(self) -> np.ndarray:
        return self.buffer

    def reset(self):
        # Do not call super().reset() because it tries to assign to self.history/time_axis
        # which are now properties without setters.
        self.voltage = 0.0
        self.update = False
        
        self.buffer = np.array([], dtype=np.float64)
        self.history_buffer = []
        self.time_buffer = []
        
    @property
    def history(self):
        if not self.history_buffer:
            return np.array([])
        return np.concatenate(self.history_buffer)
        
    @property
    def time_axis(self):
        if not self.time_buffer:
            return np.array([])
        return np.concatenate(self.time_buffer)

class VectorizedSimulation:
    """Engine that processes simulation in batches using NumPy."""
    
    def __init__(self, 
                 input_wire: VectorizedWire,
                 input_generator_func, # Function that accepts time array and returns value array
                 dt: float = 0.01,
                 batch_size: int = 1000):
        self.input_wire = input_wire
        self.input_generator = input_generator_func
        self.dt = dt
        self.batch_size = batch_size
        self.current_time = 0.0
        
        self.components: List[Component] = []
        self.wires: List[VectorizedWire] = []

        self.add_wire(input_wire)
        
    def add_wire(self, wire: VectorizedWire):
        if wire not in self.wires:
            self.wires.append(wire)

    def add_component(self, component: Component):
        if component not in self.components:
            self.components.append(component)
            # Ensure wires are upgraded/compatible if possible, otherwise we assume they are injected as VectorizedWire
            if not isinstance(component.input_wire, VectorizedWire) or not isinstance(component.output_wire, VectorizedWire):
                raise TypeError("All wires in VectorizedSimulation must be VectorizedWire")
            
            self.add_wire(component.input_wire)
            self.add_wire(component.output_wire)

    def advance_batch(self):
        """Run one batch of simulation."""
        # 1. Generate Time Batch
        start_time = self.current_time
        times = np.arange(self.batch_size, dtype=np.float64) * self.dt + start_time
        self.current_time = times[-1] + self.dt
        
        # 2. Input Signal Generation
        # We assume input_generator can accept a numpy array
        input_values = self.input_generator(times)
        self.input_wire.write_buffer(input_values, times)
        
        # 3. Propagate
        # In a generic feedback-free system, strict ordering is cleaner, 
        # but for compatibility with the existing "settling" logic, we can try topological sort or simple passes.
        # Since most our scenarios are linear chains, iterating components in order of addition is usually fine,
        # but the original engine handled loops.
        # For this optimization, we will assume a feed-forward path which covers 99% of the use cases here.
        
        for component in self.components:
            if hasattr(component, 'tick_batch'):
                component.tick_batch(times)
            else:
                # Fallback (slow!)
                raise NotImplementedError(f"Component {type(component)} does not support batch processing")

