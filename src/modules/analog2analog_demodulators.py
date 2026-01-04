from src.core.components import Component, Wire

import math


class AMDemodulator(Component):
    """AM Demodulator using envelope detection with low-pass filter."""

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
        self.envelope = 1.0
        self.alpha = 0.02

    def tick(self, time: float):
        inp = abs(self.input_wire.read())

        self.envelope = self.alpha * inp + (1 - self.alpha) * self.envelope

        message = (self.envelope - 1.0) / self.modulation_index
        self.output_wire.write(message, time)


class FMDemodulator(Component):
    """FM Demodulator using zero-crossing detection with smoothing."""

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 freq_deviation: float = 5.0):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.freq_deviation = freq_deviation

        self.reset()

    def reset(self):
        self.prev_value = 0.0
        self.prev_time = 0.0
        self.last_crossing_time = 0.0
        self.inst_freq = self.carrier_freq
        self.smoothed_output = 0.0
        self.alpha = 0.05

    def tick(self, time: float):
        current = self.input_wire.read()

        if self.prev_value <= 0 < current:
            if self.last_crossing_time > 0:
                period = time - self.last_crossing_time
                if period > 0:
                    self.inst_freq = 1.0 / period
            self.last_crossing_time = time

        freq_offset = self.inst_freq - self.carrier_freq
        normalized = freq_offset / self.freq_deviation

        self.smoothed_output = (self.alpha * normalized +
                                (1 - self.alpha) * self.smoothed_output)

        self.prev_value = current
        self.prev_time = time
        self.output_wire.write(self.smoothed_output, time)


class PMDemodulator(Component):
    """PM Demodulator using coherent detection."""

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

        i_component = inp * ref_cos
        q_component = inp * ref_sin

        phase = math.atan2(q_component, i_component)

        message = phase / self.phase_deviation
        self.output_wire.write(message, time)
