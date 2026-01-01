import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List


class ControlPanel(ttk.Frame):
    """Left-side panel containing simulation controls (Start, Stop, Settings).
    """

    def __init__(self,
                 parent,
                 scenario_list: List[str],
                 on_scenario_change: Callable[[str], None],
                 on_start: Callable[[float], None],
                 on_stop: Callable[[], None],
                 on_visualize: Callable,
                 on_wire_toggle: Callable[[List[str]], None]):
        super().__init__(parent, padding="10")

        self.scenario_list = scenario_list

        self.on_scenario_change = on_scenario_change
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_visualize = on_visualize
        self.on_wire_toggle = on_wire_toggle

        # State storage for wire checkboxes {wire_name: BooleanVar}
        self.wire_vars: Dict[str, tk.BooleanVar] = {}

        self._init_widgets()

    def _init_widgets(self):
        # Header
        ttk.Label(self, text="Control Panel", font=("Arial", 14, "bold")) \
            .pack(pady=(0, 20))

        # Scenario Selection
        lf_scenario = ttk.LabelFrame(self, text="Simulation Setup", padding=10)
        lf_scenario.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(lf_scenario, text="Select Scenario:").pack(anchor=tk.W)

        self.combo_scenario = ttk.Combobox(lf_scenario,
                                           values=self.scenario_list,
                                           state="readonly")
        if self.scenario_list:
            self.combo_scenario.current(0)  # Select first by default

        self.combo_scenario.pack(fill=tk.X, pady=(5, 0))
        self.combo_scenario.bind("<<ComboboxSelected>>",
                                 self._handle_scenario_change)

        # Duration Input
        ttk.Label(self, text="Duration (sec):").pack(anchor=tk.W)
        self.entry_duration = ttk.Entry(self)
        self.entry_duration.insert(0, "1.0")
        self.entry_duration.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        self.btn_start = ttk.Button(self, text="Start",
                                    command=self._handle_start)
        self.btn_start.pack(fill=tk.X, pady=5)

        self.btn_stop = ttk.Button(self, text="Stop", command=self.on_stop,
                                   state=tk.DISABLED)
        self.btn_stop.pack(fill=tk.X, pady=5)

        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=20)

        # Status and Progress
        self.lbl_status = ttk.Label(self, text="Status: Ready",
                                    foreground="blue")
        self.lbl_status.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL,
                                            mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=10)

        # Visualization Button
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=10)

        self.btn_viz = ttk.Button(self, text="Show Topology Graph",
                                  command=self.on_visualize)
        self.btn_viz.pack(fill=tk.X, pady=5)

        # Wire Visibility
        lf_wires = ttk.LabelFrame(self, text="Visible Wires", padding=5)
        lf_wires.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        self.canvas = tk.Canvas(lf_wires, highlightthickness=0)
        scrollbar = ttk.Scrollbar(lf_wires, orient="vertical",
                                  command=self.canvas.yview)

        self.wire_list_frame = ttk.Frame(self.canvas)

        self.wire_list_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.wire_list_frame,
                                  anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_wire_list(self, wire_names: List[str]):
        """Dynamically creates checkboxes for each wire in the simulation."""
        # 1. Clear existing checkboxes
        for widget in self.wire_list_frame.winfo_children():
            widget.destroy()
        self.wire_vars.clear()

        # 2. Create new checkboxes
        for name in wire_names:
            var = tk.BooleanVar(value=True)  # Checked by default
            self.wire_vars[name] = var

            chk = ttk.Checkbutton(
                self.wire_list_frame,
                text=name,
                variable=var,
                command=self._handle_wire_toggle  # Trigger update on click
            )
            chk.pack(anchor=tk.W, padx=5, pady=2)

    def _handle_scenario_change(self, _):
        """Triggered when combobox changes."""
        selected_scenario = self.combo_scenario.get()
        self.on_scenario_change(selected_scenario)

    def _handle_wire_toggle(self):
        """Triggered when any wire checkbox is clicked."""
        # Collect list of currently checked wires
        active_wires = [name for name, var in self.wire_vars.items() if var.get()]
        self.on_wire_toggle(active_wires)

    def _handle_start(self):
        """Validates input and triggers the start callback."""
        try:
            duration = float(self.entry_duration.get())
            self.on_start(duration)
        except ValueError:
            messagebox.showerror("Error",
                                 "Please enter a valid number for duration.")

    def set_state_running(self):
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_status.config(text="Running...", foreground="green")
        self.progress_bar['value'] = 0

    def set_state_stopped(self):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="Stopped / Finished", foreground="black")
        self.progress_bar['value'] = 100

    def update_progress(self, value: float):
        self.progress_bar['value'] = value
