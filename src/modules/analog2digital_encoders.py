from src.core.components import Component, Wire


class DeltaModulationEncoder(Component):
    """Delta Modulation Encoder.

    Encodes the difference between successive samples as a single bit:
    1 = signal increased, 0 = signal decreased.
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 sample_rate: float,
                 step_size: float = 0.1):
        super().__init__(input_wire, output_wire)
        self.sample_period = 1.0 / sample_rate
        self.step_size = step_size

        self.reset()

    def reset(self):
        self.approximation = 0.0
        self.last_sample_index = -1
        self.current_bit = 0.0

    def tick(self, time: float):
        sample_index = int(time / self.sample_period)

        if sample_index > self.last_sample_index:
            inp = self.input_wire.read()

            if inp > self.approximation:
                self.current_bit = 1.0
                self.approximation += self.step_size
            else:
                self.current_bit = 0.0
                self.approximation -= self.step_size

            self.last_sample_index = sample_index

        self.output_wire.write(self.current_bit, time)


class PCMEncoder(Component):
    """Pulse Code Modulation (PCM) Encoder.

    Quantizes analog input to discrete levels and outputs the binary
    representation bit-by-bit.
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 sample_rate: float,
                 n_bits: int = 4,
                 v_min: float = -1.0,
                 v_max: float = 1.0):
        super().__init__(input_wire, output_wire)
        self.sample_period = 1.0 / sample_rate
        self.n_bits = n_bits
        self.v_min = v_min
        self.v_max = v_max

        self.bit_period = self.sample_period / n_bits
        self.n_levels = 2 ** n_bits

        self.reset()

    def reset(self):
        self.current_code = 0
        self.last_sample_index = -1

    def tick(self, time: float):
        sample_index = int(time / self.sample_period)

        if sample_index > self.last_sample_index:
            inp = self.input_wire.read()

            clamped = max(self.v_min, min(self.v_max, inp))
            normalized = (clamped - self.v_min) / (self.v_max - self.v_min)

            self.current_code = int(normalized * (self.n_levels - 1))
            self.last_sample_index = sample_index

        time_in_sample = time % self.sample_period
        bit_index = int(time_in_sample / self.bit_period)
        bit_index = min(bit_index, self.n_bits - 1)

        bit_position = self.n_bits - 1 - bit_index
        bit_value = (self.current_code >> bit_position) & 1

        self.output_wire.write(float(bit_value), time)
