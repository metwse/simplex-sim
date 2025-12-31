from src.core.components import Wire

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure

from typing import List


class PlotPanel(ttk.Frame):
    """Right-side panel containing the Matplotlib canvas.
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Figure Setup
        self.fig = Figure(figsize=(5, 4), dpi=100)

        # Canvas Setup
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,
                                         expand=True)

        # Toolbar Setup
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,
                                         expand=True)

    def plot_wires(self, wires: List[Wire]):
        """Clears the canvas and plots the history of the provided wires.
        """
        self.fig.clear()

        if not wires:
            self.canvas.draw()
            return

        num_wires = len(wires)
        axes = self.fig.subplots(num_wires, 1, sharex=True)

        if num_wires == 1:
            axes = [axes]

        for i, wire in enumerate(wires):
            ax = axes[i]
            ax.plot(wire.time_axis, wire.history, label=wire.name,
                    linewidth=1.5)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='upper right', fontsize='small')

            if i == num_wires - 1:
                ax.set_xlabel("time (s)")

        self.fig.tight_layout()
        self.canvas.draw()
