from src.core.components import Component, Wire

import math


class AMModulator(Component):
    """Amplitude Modulation (AM).

    Carrier amplitude varies with the message signal.
    Output: (1 + m * message(t)) * cos(2*pi*fc*t)
    where m is the modulation index.
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 modulation_index: float = 0.5):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.modulation_index = modulation_index

    def tick(self, time: float):
        message = self.input_wire.read()
        carrier = math.cos(2 * math.pi * self.carrier_freq * time)

        envelope = 1.0 + self.modulation_index * message
        self.output_wire.write(envelope * carrier, time)


class FMModulator(Component):
    """Frequency Modulation (FM).

    Carrier frequency varies with the message signal.
    Instantaneous frequency: fc + kf * message(t)
    """

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
        self.phase_integral = 0.0
        self.last_time = 0.0

    def tick(self, time: float):
        message = self.input_wire.read()
        dt = time - self.last_time

        if dt > 0:
            inst_freq = self.carrier_freq + self.freq_deviation * message
            self.phase_integral += 2 * math.pi * inst_freq * dt

        signal = math.cos(self.phase_integral)
        self.output_wire.write(signal, time)
        self.last_time = time


class PMModulator(Component):
    """Phase Modulation (PM).

    Carrier phase varies with the message signal.
    Output: cos(2*pi*fc*t + kp * message(t))
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 phase_deviation: float = math.pi / 2):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.phase_deviation = phase_deviation

    def tick(self, time: float):
        message = self.input_wire.read()
        phase = 2 * math.pi * self.carrier_freq * time
        phase += self.phase_deviation * message

        self.output_wire.write(math.cos(phase), time)
