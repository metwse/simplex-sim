import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable


class ControlPanel(ttk.Frame):
    """Left-side panel containing simulation controls (Start, Stop, Settings).
    """

    def __init__(self,
                 parent,
                 on_start: Callable[[float], None],
                 on_stop: Callable[[], None]):
        super().__init__(parent, padding="10")

        self.on_start = on_start
        self.on_stop = on_stop

        self._init_widgets()

    def _init_widgets(self):
        # Header
        ttk.Label(self, text="Control Panel", font=("Arial", 14, "bold")) \
            .pack(pady=(0, 20))

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
