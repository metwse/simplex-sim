from .workers import SimulationThread
from .panels.controls import ControlPanel
from .panels.plotting import PlotPanel

from src.simulations import SCENARIOS
from src.utils.graph_gen import generate_topology_graph

import tkinter as tk
from tkinter import ttk
import io
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("simplexsim")
        self.geometry("1200x800")

        # Initialize Layout
        self._init_layout()

        self.load_scenario(list(SCENARIOS.keys())[0])

    def load_scenario(self, scenario_name):
        self.scenario = SCENARIOS[scenario_name]

        defaults = {
            k: v.get('default')
            for k, v in self.scenario.get('parameters', {}).items()
        }

        self.rebuild_simulation(defaults, False)

        # Update UI components that depend on the topology
        wire_names = [w.name for w in self.wires]
        self.controls.populate_wire_list(wire_names)
        self.controls.generate_param_fields(self.scenario['parameters'])
        self.controls.set_scenario_description(self.scenario['description'])

    def rebuild_simulation(self, parameters: dict,
                           preserve_wires_to_plot: bool = True):
        """Builds the SimulationEngine using the provided parameters."""

        wires_to_plot = [w.name for w in self.wires_to_plot] \
            if preserve_wires_to_plot else None

        self.sim_engine = self.scenario['setup'](**parameters)
        self.wires = self.sim_engine.wires

        if wires_to_plot is not None:
            self.wires_to_plot = [*filter(lambda w: w.name in wires_to_plot,
                                          self.wires)]
        else:
            self.wires_to_plot = self.wires

        # Reset plot
        self.plotting.plot_wires([])

    def update_plot_visibility(self, visible_wire_names):
        """Filter self.wires based on names and re-plot."""
        self.wires_to_plot = [
            w for w in self.wires if w.name in visible_wire_names
        ]

        self.plotting.plot_wires(self.wires_to_plot)

    def visualize_simulation(self):
        dot = generate_topology_graph(self.sim_engine)

        img = Image.open(io.BytesIO(dot.pipe()))

        top = tk.Toplevel(self)
        top.title("Simulation Topology")

        tk_img = ImageTk.PhotoImage(img)

        lbl = ttk.Label(top, image=tk_img)
        lbl.pack(padx=10, pady=10)

        lbl.image = tk_img  # type: ignore

    def start_simulation(self, duration: float):
        """Called by ControlPanel when Start is clicked."""
        params = self.controls.get_param_values()
        self.rebuild_simulation(params)

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
            # update progress bar
            self.controls.update_progress(self.sim_thread.progress)

            if self.sim_thread.is_alive():
                # re-schedule check
                self.after(100, self.monitor_simulation)
            else:
                # finished
                self.controls.set_state_stopped()
                self.plotting.plot_wires(self.wires_to_plot)
        else:
            self.after(100, self.monitor_simulation)

    def _init_layout(self):
        self.controls = \
            ControlPanel(self,
                         scenario_list=list(SCENARIOS.keys()),
                         on_scenario_change=self.load_scenario,
                         on_start=self.start_simulation,
                         on_stop=self.stop_simulation,
                         on_visualize=self.visualize_simulation,
                         on_wire_toggle=self.update_plot_visibility)
        self.controls.pack(side=tk.LEFT, fill=tk.Y)

        self.plotting = PlotPanel(self)
        self.plotting.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
