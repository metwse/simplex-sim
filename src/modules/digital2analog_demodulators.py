from src.core.components import Component, Wire

import math


class ASKDemodulator(Component):
    """ASK Demodulator using envelope detection."""

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        self.accumulator = 0.0
        self.sample_count = 0
        self.last_bit_index = -1
        self.decoded_bit = 0.0

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)

        if bit_index > self.last_bit_index:
            if self.sample_count > 0:
                avg = self.accumulator / self.sample_count
                self.decoded_bit = 1.0 if avg > 0.3 else 0.0

            self.accumulator = 0.0
            self.sample_count = 0
            self.last_bit_index = bit_index

        self.accumulator += abs(self.input_wire.read())
        self.sample_count += 1

        self.output_wire.write(self.decoded_bit, time)


class FSKDemodulator(Component):
    """FSK Demodulator using zero-crossing detection."""

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
        self.threshold = (freq_0 + freq_1) / 2.0

        self.reset()

    def reset(self):
        self.last_value = 0.0
        self.zero_crossings = 0
        self.last_bit_index = -1
        self.decoded_bit = 0.0

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)
        current = self.input_wire.read()

        if bit_index > self.last_bit_index:
            if self.last_bit_index >= 0:
                estimated_freq = self.zero_crossings / (2.0 * self.bit_duration)
                self.decoded_bit = 1.0 if estimated_freq > self.threshold else 0.0

            self.zero_crossings = 0
            self.last_bit_index = bit_index

        if self.last_value * current < 0:
            self.zero_crossings += 1

        self.last_value = current
        self.output_wire.write(self.decoded_bit, time)


class PSKDemodulator(Component):
    """PSK Demodulator using coherent detection."""

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 carrier_freq: float,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        self.accumulator = 0.0
        self.sample_count = 0
        self.last_bit_index = -1
        self.decoded_bit = 0.0

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)

        if bit_index > self.last_bit_index:
            if self.sample_count > 0:
                corr = self.accumulator / self.sample_count
                self.decoded_bit = 1.0 if corr > 0 else 0.0

            self.accumulator = 0.0
            self.sample_count = 0
            self.last_bit_index = bit_index

        ref = math.sin(2 * math.pi * self.carrier_freq * time)
        self.accumulator += self.input_wire.read() * ref
        self.sample_count += 1

        self.output_wire.write(self.decoded_bit, time)
