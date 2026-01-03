from src.core.components import Component, Wire


class NRZLDecoder(Component):
    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.last_decoded_bit = 0.0

    def tick(self, time: float):
        # Sample in the middle of the bit period for stability
        cycle_pos = time % self.bit_duration

        if cycle_pos >= (self.bit_duration * 0.5) and \
           cycle_pos < (self.bit_duration * 0.6):
            inp = self.input_wire.read()

            if inp > 0.0:
                self.last_decoded_bit = 0.0
            else:
                self.last_decoded_bit = 1.0

        self.output_wire.write(self.last_decoded_bit, time)


class NRZIDecoder(Component):
    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate

        self.previous_level = -1.0  # Default start level of Encoder
        self.last_decoded_bit = 0.0
        self.current_bit_index = -1

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)
        cycle_pos = time % self.bit_duration

        # Sample at 50%
        if bit_index > self.current_bit_index and cycle_pos >= \
           (self.bit_duration * 0.5):
            current_level = self.input_wire.read()

            # Use a threshold to determine High/Low clearly
            current_level = 1.0 if current_level > 0 else -1.0

            if current_level != self.previous_level:
                self.last_decoded_bit = 1.0  # Transition detected
            else:
                self.last_decoded_bit = 0.0  # No transition

            self.previous_level = current_level
            self.current_bit_index = bit_index

        self.output_wire.write(self.last_decoded_bit, time)


class BipolarAMIDecoder(Component):
    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.last_decoded_bit = 0.0

    def tick(self, time: float):
        cycle_pos = time % self.bit_duration

        # Sample at 50%
        if cycle_pos >= (self.bit_duration * 0.5) and \
           cycle_pos < (self.bit_duration * 0.6):
            inp = self.input_wire.read()

            # Check magnitude
            if abs(inp) > 0.5:
                self.last_decoded_bit = 1.0
            else:
                self.last_decoded_bit = 0.0

        self.output_wire.write(self.last_decoded_bit, time)


class PseudoternaryDecoder(Component):
    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.last_decoded_bit = 0.0

    def tick(self, time: float):
        cycle_pos = time % self.bit_duration

        # Sample at 50%
        if cycle_pos >= (self.bit_duration * 0.5) and \
           cycle_pos < (self.bit_duration * 0.6):
            inp = self.input_wire.read()

            if abs(inp) > 0.5:
                self.last_decoded_bit = 0.0
            else:
                self.last_decoded_bit = 1.0

        self.output_wire.write(self.last_decoded_bit, time)


class ManchesterDecoder(Component):
    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.last_decoded_bit = 0.0

        self.sample_1 = 0.0
        self.current_bit_index = -1
        self.sampled_first_half = False

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)
        cycle_pos = time % self.bit_duration

        if bit_index > self.current_bit_index:
            self.current_bit_index = bit_index
            self.sampled_first_half = False

        # Sample 1: First Half (at 25%)
        if not self.sampled_first_half and \
           cycle_pos >= (self.bit_duration * 0.25):
            self.sample_1 = self.input_wire.read()
            self.sampled_first_half = True

        # Sample 2: Second Half (at ~75%) -> Make Decision
        if cycle_pos >= (self.bit_duration * 0.75) \
           and cycle_pos < (self.bit_duration * 0.85):
            sample_2 = self.input_wire.read()

            if self.sample_1 < 0 and sample_2 > 0:
                self.last_decoded_bit = 1.0
            elif self.sample_1 > 0 and sample_2 < 0:
                self.last_decoded_bit = 0.0
            # Else: Error or noise, keep previous

        self.output_wire.write(self.last_decoded_bit, time)


class DifferentialManchesterDecoder(Component):
    def __init__(self, input_wire: Wire, output_wire: Wire, baud_rate: float):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.last_decoded_bit = 0.0

        # Start assuming previous bit ended Low (matches Encoder reset)
        self.prev_second_half = -1.0
        self.current_bit_index = -1

    def tick(self, time: float):
        bit_index = int(time / self.bit_duration)
        cycle_pos = time % self.bit_duration

        # Logic runs at ~25%
        if bit_index > self.current_bit_index and \
           cycle_pos >= (self.bit_duration * 0.25):
            current_first_half = self.input_wire.read()

            # Normalize to +/- 1.0 for comparison
            curr_val = 1.0 if current_first_half > 0 else -1.0
            prev_val = 1.0 if self.prev_second_half > 0 else -1.0

            if curr_val == prev_val:
                # Levels matched -> No transition at start -> Logic 1
                self.last_decoded_bit = 1.0
            else:
                # Levels different -> Transition at start -> Logic 0
                self.last_decoded_bit = 0.0

            self.current_bit_index = bit_index

        # At ~75%, we record the "second half" value for the NEXT bit to use
        if cycle_pos >= (self.bit_duration * 0.75) and \
           cycle_pos < (self.bit_duration * 0.85):
            self.prev_second_half = self.input_wire.read()

        self.output_wire.write(self.last_decoded_bit, time)
