import threading
from src.core.engine import Simulation


class SimulationThread(threading.Thread):
    """Runs the blocking simulation in a separate thread."""

    def __init__(self, sim: Simulation, duration: float):
        super().__init__()
        self.sim = sim
        self.duration = duration
        self.stop_requested = False
        self.progress = 0.0

    def run(self):
        self.stop_requested = False

        total_steps = int(self.duration / self.sim.dt)
        current_step = 0

        while current_step < total_steps and not self.stop_requested:
            self.sim.advance()
            current_step += 1

            self.progress = (current_step / total_steps) * 100

    def stop(self):
        self.stop_requested = True
