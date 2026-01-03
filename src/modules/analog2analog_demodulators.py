from src.core.components import Component, Wire

import math


class AMDemodulator(Component):
    """AM Demodulator using envelope detection."""

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 modulation_index: float = 0.5):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.modulation_index = modulation_index

        self.reset()

    def reset(self):
        self.envelope = 0.0
        self.alpha = 0.1

    def tick(self, time: float):
        inp = abs(self.input_wire.read())

        self.envelope = self.alpha * inp + (1 - self.alpha) * self.envelope

        message = (self.envelope - 1.0) / self.modulation_index
        self.output_wire.write(message, time)


class FMDemodulator(Component):
    """FM Demodulator using differentiation."""

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 freq_deviation: float = 10.0):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.freq_deviation = freq_deviation

        self.reset()

    def reset(self):
        self.last_value = 0.0
        self.last_time = 0.0
        self.output = 0.0

    def tick(self, time: float):
        current = self.input_wire.read()
        dt = time - self.last_time

        if dt > 0:
            derivative = (current - self.last_value) / dt
            self.output = derivative / (2 * math.pi * self.freq_deviation)

        self.last_value = current
        self.last_time = time
        self.output_wire.write(self.output, time)


class PMDemodulator(Component):
    """PM Demodulator using phase comparison."""

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 phase_deviation: float = math.pi / 2):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.phase_deviation = phase_deviation

    def tick(self, time: float):
        inp = self.input_wire.read()

        ref_cos = math.cos(2 * math.pi * self.carrier_freq * time)
        ref_sin = math.sin(2 * math.pi * self.carrier_freq * time)

        phase = math.atan2(-inp * ref_sin, inp * ref_cos)
        message = phase / self.phase_deviation

        self.output_wire.write(message, time)
