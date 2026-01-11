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
        self.omega = 2 * math.pi * carrier_freq
        self.modulation_index = modulation_index

    def tick(self, time: float):
        message = self.input_wire.voltage
        carrier = math.cos(self.omega * time)

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
        self.omega_factor = 2 * math.pi * carrier_freq
        self.dev_factor = 2 * math.pi * freq_deviation

        self.reset()

    def reset(self):
        self.phase_integral = 0.0
        self.last_time = 0.0

    def tick(self, time: float):
        message = self.input_wire.voltage
        dt = time - self.last_time

        if dt > 0:
            inst_omega = self.omega_factor + self.dev_factor * message
            self.phase_integral += inst_omega * dt

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
        self.omega = 2 * math.pi * carrier_freq
        self.phase_deviation = phase_deviation

    def tick(self, time: float):
        message = self.input_wire.voltage
        phase = self.omega * time
        phase += self.phase_deviation * message

        self.output_wire.write(math.cos(phase), time)
