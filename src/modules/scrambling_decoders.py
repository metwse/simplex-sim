from src.core.components import Component, Wire


class B8ZSDecoder(Component):
    """B8ZS Decoder.

    Detects violation patterns and restores original zeros.
    Patterns: 000+-0-+ or 000-+0+-
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        self.buffer = [0.0] * 8
        self.last_bit_index = -1
        self.last_output = 0.0

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)

        if bit_index > self.last_bit_index:
            current = self.input_wire.read()

            self.buffer.pop(0)
            self.buffer.append(current)

            if self._is_b8zs_pattern():
                self.last_output = 0.0
            else:
                oldest = self.buffer[0]
                if abs(oldest) > 0.5:
                    self.last_output = 1.0
                else:
                    self.last_output = 0.0

            self.last_bit_index = bit_index

        self.output_wire.write(self.last_output, time)

    def _is_b8zs_pattern(self) -> bool:
        b = self.buffer
        pattern1 = (abs(b[0]) < 0.5 and abs(b[1]) < 0.5 and abs(b[2]) < 0.5 and
                    b[3] > 0.5 and b[4] < -0.5 and abs(b[5]) < 0.5 and
                    b[6] < -0.5 and b[7] > 0.5)
        pattern2 = (abs(b[0]) < 0.5 and abs(b[1]) < 0.5 and abs(b[2]) < 0.5 and
                    b[3] < -0.5 and b[4] > 0.5 and abs(b[5]) < 0.5 and
                    b[6] > 0.5 and b[7] < -0.5)
        return pattern1 or pattern2


class HDB3Decoder(Component):
    """HDB3 Decoder.

    Detects B00V and 000V patterns and restores original zeros.
    """

    def __init__(self,
                 input_wire: Wire,
                 output_wire: Wire,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        self.buffer = [0.0] * 4
        self.last_bit_index = -1
        self.last_output = 0.0
        self.last_polarity = 1.0

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)

        if bit_index > self.last_bit_index:
            current = self.input_wire.read()

            self.buffer.pop(0)
            self.buffer.append(current)

            if self._is_hdb3_pattern():
                self.last_output = 0.0
            else:
                oldest = self.buffer[0]
                if abs(oldest) > 0.5:
                    self.last_output = 1.0
                    self.last_polarity = oldest
                else:
                    self.last_output = 0.0

            self.last_bit_index = bit_index

        self.output_wire.write(self.last_output, time)

    def _is_hdb3_pattern(self) -> bool:
        b = self.buffer

        pattern_000v = (abs(b[0]) < 0.5 and abs(b[1]) < 0.5 and
                        abs(b[2]) < 0.5 and abs(b[3]) > 0.5)

        pattern_b00v = (abs(b[0]) > 0.5 and abs(b[1]) < 0.5 and
                        abs(b[2]) < 0.5 and abs(b[3]) > 0.5 and
                        (b[0] > 0) == (b[3] > 0))

        return pattern_000v or pattern_b00v
