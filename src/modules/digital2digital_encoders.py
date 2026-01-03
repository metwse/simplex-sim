from src.core.components import Component, Wire


class NRZLEncoder(Component):
    """Non-Return-to-Zero Level (NRZ-L).

    This is a level-based encoding, so it acts like a simple mapper.

    baud_rate argument at __init__ is only for unifying encoder constructor
    interface.
    """

    def __init__(self, input_wire: Wire, output_wire: Wire,
                 baud_rate: float = 0.0,
                 high_level: float = 1.0, low_level: float = -1.0):
        super().__init__(input_wire, output_wire)
        _ = baud_rate
        self.high = high_level
        self.low = low_level

    def tick(self, time: float):
        inp = self.input_wire.read()

        if inp > 0.5:
            self.output_wire.write(self.low, time)
        else:
            self.output_wire.write(self.high, time)


class NRZIEncoder(Component):
    """Non-Return-to-Zero Inverted (NRZI).

    0 = no transition at beginning of interval (keep current level)
    1 = transition at beginning of interval (flip level)
    """

    def __init__(self, input_wire: Wire, output_wire: Wire,
                 baud_rate: float, high_level: float = 1.0,
                 low_level: float = -1.0):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.high = high_level
        self.low = low_level

        self.reset()

    def reset(self):
        self.current_level = self.low
        self.last_bit_index = -1

    def tick(self, time: float):
        # Calculate which bit number we are currently processing
        current_bit_index = int(time / self.bit_duration)

        # Check if we have entered a new bit period
        if current_bit_index > self.last_bit_index:
            inp = self.input_wire.read()
            is_logic_1 = inp > 0.5

            if is_logic_1:
                # Logic 1: Transition (Flip the voltage)
                if self.current_level == self.low:
                    self.current_level = self.high
                else:
                    self.current_level = self.low
            else:
                # Logic 0: No transition (Keep the current voltage)
                pass

            # Update the index so we don't process this bit again
            self.last_bit_index = current_bit_index

        # Write the maintained level to the wire
        self.output_wire.write(self.current_level, time)


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


class BipolarAMIEncoder(Component):
    """Bipolar-AMI.

    0 = no line signal
    1 = positive or negative level, alternating for successive ones
    """

    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        # State tracking
        # Start assuming last was negative, so first 1 is positive
        self.last_polarity = -1.0
        self.current_voltage = 0.0
        self.last_bit_index = -1

    def tick(self, time: float):
        current_bit_index = int(time / self.bit_duration)

        if current_bit_index > self.last_bit_index:
            inp = self.input_wire.read()
            is_logic_1 = inp > 0.5

            if is_logic_1:
                # Flip polarity
                self.current_voltage = -self.last_polarity
                self.last_polarity = self.current_voltage
            else:
                # Logic 0: No signal
                self.current_voltage = 0.0

            self.last_bit_index = current_bit_index

        self.output_wire.write(self.current_voltage, time)


class PseudoternaryEncoder(Component):
    """Pseudoternary.

    0 = positive or negative level, alternating for successive zeros
    1 = no line signal
    """

    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        self.last_polarity = -1.0
        self.current_voltage = 0.0
        self.last_bit_index = -1

    def tick(self, time: float):
        current_bit_index = int(time / self.bit_duration)

        if current_bit_index > self.last_bit_index:
            inp = self.input_wire.read()
            is_logic_1 = inp > 0.5

            if not is_logic_1:  # Logic 0
                # Flip polarity
                self.current_voltage = -self.last_polarity
                self.last_polarity = self.current_voltage
            else:
                # Logic 1: No signal
                self.current_voltage = 0.0

            self.last_bit_index = current_bit_index

        self.output_wire.write(self.current_voltage, time)


class DifferentialManchesterEncoder(Component):
    """Differential Manchester.

    Always a transition in middle of interval.
    0 = transition at beginning of interval
    1 = no transition at beginning of interval
    """

    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.reset()

    def reset(self):
        self.previous_end_level = -1.0  # Assume previous bit ended low
        self.current_start_level = -1.0
        self.last_bit_index = -1

    def tick(self, time: float):
        current_bit_index = int(time / self.bit_duration)

        # Determine bit boundary
        if current_bit_index > self.last_bit_index:
            inp = self.input_wire.read()
            is_logic_1 = inp > 0.5

            # Logic 0: Transition at beginning -> flip from previous end
            # Logic 1: No transition at beginning -> keep previous end
            if is_logic_1:
                self.current_start_level = self.previous_end_level
            else:
                self.current_start_level = -self.previous_end_level

            self.last_bit_index = current_bit_index

        # Determine position within the bit (first half or second half)
        cycle_pos = time % self.bit_duration
        is_first_half = cycle_pos < (self.bit_duration / 2.0)

        if is_first_half:
            voltage = self.current_start_level
        else:
            # Always transition in the middle
            voltage = -self.current_start_level

        # Update state for next cycle
        self.previous_end_level = voltage

        self.output_wire.write(voltage, time)
