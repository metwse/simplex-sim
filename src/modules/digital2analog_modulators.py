from src.core.components import Component, Wire

import math


class ASKModulator(Component):
    """Amplitude Shift Keying (ASK) Modulator.

    Binary 1 = carrier at full amplitude
    Binary 0 = carrier at zero (or low) amplitude
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.bit_duration = 1.0 / baud_rate

    def tick(self, time: float):
        bit = self.input_wire.read()
        amplitude = 1.0 if bit > 0.5 else 0.0

        carrier = math.sin(2 * math.pi * self.carrier_freq * time)
        self.output_wire.write(amplitude * carrier, time)


class FSKModulator(Component):
    """Frequency Shift Keying (FSK) Modulator.

    Binary 1 = carrier at frequency f1
    Binary 0 = carrier at frequency f0
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 freq_0: float,
                 freq_1: float,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.freq_0 = freq_0
        self.freq_1 = freq_1
        self.bit_duration = 1.0 / baud_rate

    def tick(self, time: float):
        bit = self.input_wire.read()
        freq = self.freq_1 if bit > 0.5 else self.freq_0

        signal = math.sin(2 * math.pi * freq * time)
        self.output_wire.write(signal, time)


class PSKModulator(Component):
    """Phase Shift Keying (PSK) Modulator.

    Binary 1 = carrier with 0 phase
    Binary 0 = carrier with 180 degree phase shift
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.bit_duration = 1.0 / baud_rate

    def tick(self, time: float):
        bit = self.input_wire.read()
        phase = 0.0 if bit > 0.5 else math.pi

        signal = math.sin(2 * math.pi * self.carrier_freq * time + phase)
        self.output_wire.write(signal, time)
