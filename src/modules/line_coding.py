from src.core.components import Component, Wire


class NRZLEncoder(Component):
    """Non-Return-to-Zero Level (NRZ-L).

    This is a level-based encoding, so it acts like a simple mapper.
    """

    def __init__(self, input_wire: Wire, output_wire: Wire,
                 high_level: float = 1.0, low_level: float = -1.0):
        super().__init__(input_wire, output_wire)
        self.high = high_level
        self.low = low_level

    def tick(self, time: float):
        inp = self.input_wire.read()

        if inp > 0.5:
            self.output_wire.write(self.high, time)
        else:
            self.output_wire.write(self.low, time)


class ManchesterEncoder(Component):
    """Manchester Encoding.

    Requires 'baud_rate' to calculate the bit period.
    """

    def __init__(self, input_wire: Wire, output_wire: Wire,
                 baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

    def tick(self, time: float):
        inp = self.input_wire.read()
        is_logic_1 = inp > 0.5

        cycle_pos = time % self.bit_duration
        is_first_half = cycle_pos < (self.bit_duration / 2.0)

        if is_logic_1:
            voltage = -1.0 if is_first_half else 1.0
        else:
            voltage = 1.0 if is_first_half else -1.0

        self.output_wire.write(voltage, time)
