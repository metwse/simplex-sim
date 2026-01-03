from src.core.components import Component, Wire


class DeltaModulationDecoder(Component):
    """Delta Modulation Decoder.

    Reconstructs the signal by integrating the delta bits:
    1 = step up, 0 = step down.
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
        self.reconstructed = 0.0
        self.last_sample_index = -1

    def tick(self, time: float):
        sample_index = int(time / self.sample_period)

        if sample_index > self.last_sample_index:
            bit = self.input_wire.read()

            if bit > 0.5:
                self.reconstructed += self.step_size
            else:
                self.reconstructed -= self.step_size

            self.last_sample_index = sample_index

        self.output_wire.write(self.reconstructed, time)


class PCMDecoder(Component):
    """PCM Decoder.

    Collects bits over a sample period and reconstructs the quantized
    analog value.
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
        self.accumulated_code = 0
        self.bits_received = 0
        self.last_bit_index = -1
        self.output_value = 0.0

    def tick(self, time: float):
        global_bit_index = int(time / self.bit_period)

        if global_bit_index > self.last_bit_index:
            bit = 1 if self.input_wire.read() > 0.5 else 0

            self.accumulated_code = (self.accumulated_code << 1) | bit
            self.bits_received += 1

            if self.bits_received >= self.n_bits:
                normalized = self.accumulated_code / (self.n_levels - 1)
                self.output_value = \
                    self.v_min + normalized * (self.v_max - self.v_min)

                self.accumulated_code = 0
                self.bits_received = 0

            self.last_bit_index = global_bit_index

        self.output_wire.write(self.output_value, time)
