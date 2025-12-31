from .workers import SimulationThread
from .panels.controls import ControlPanel
from .panels.plotting import PlotPanel

from src.core.engine import Simulation, Wire
from src.modules.generators import create_digital_signal
from src.modules.line_coding import ManchesterEncoder, NRZLEncoder

import tkinter as tk


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("simplexsim")
        self.geometry("1200x800")

        # Initialize Layout
        self._init_layout()

        # Load Default Simulation Scenario
        self._setup_default_simulation()

    def _init_layout(self):
        self.controls = ControlPanel(self, on_start=self.start_simulation,
                                     on_stop=self.stop_simulation)
        self.controls.pack(side=tk.LEFT, fill=tk.Y)

        self.plotting = PlotPanel(self)
        self.plotting.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _setup_default_simulation(self):
        self.w_input = Wire("Raw Input")
        self.w_encoded = Wire("NRZL Encoded")
        self.w_encoded2 = Wire("Manchester Encoded")
        self.wires = [self.w_input, self.w_encoded, self.w_encoded2]

        baud_rate = 5.0
        input_func = create_digital_signal("1011010111", baud_rate=baud_rate)

        self.sim_engine = Simulation(
            input_wire=self.w_input,
            input_function=input_func,
            dt=0.001
        )

        self.sim_engine.add_component(
            ManchesterEncoder(self.w_input, self.w_encoded,
                              baud_rate=baud_rate))
        self.sim_engine.add_component(
            NRZLEncoder(self.w_input, self.w_encoded2))

    def start_simulation(self, duration: float):
        """Called by ControlPanel when Start is clicked."""
        self.sim_engine.reset()

        self.controls.set_state_running()

        self.sim_thread = SimulationThread(self.sim_engine, duration)
        self.sim_thread.start()

        self.after(100, self.monitor_simulation)

    def stop_simulation(self):
        """Called by ControlPanel when Stop is clicked."""
        if self.sim_thread and self.sim_thread.is_alive():
            self.sim_thread.stop()

    def monitor_simulation(self):
        """Polls the thread for progress."""
        if self.sim_thread:
            # Update Progress Bar
            self.controls.update_progress(self.sim_thread.progress)

            if self.sim_thread.is_alive():
                # Re-schedule check
                self.after(100, self.monitor_simulation)
            else:
                # Finished
                self.controls.set_state_stopped()
                self.plotting.plot_wires(self.wires)
        else:
            self.after(100, self.monitor_simulation)
