
from src.core.components import Component
from src.core.vectorized import VectorizedWire
from src.core.numba_kernels import (
    ask_modulate, fsk_modulate, psk_modulate,
    am_modulate, fm_modulate, pm_modulate
)
import numpy as np

# Mixin or Subclassing
class VectorizedComponentMixin:
    def tick_batch(self, times: np.ndarray):
        pass

class VectorizedASKModulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, baud_rate):
        super().__init__(input_wire, output_wire)
        self.omega = 2 * np.pi * carrier_freq
        
    def tick_batch(self, times: np.ndarray):
        bits = self.input_wire.read_buffer() # Assuming this returns proper array
        result = ask_modulate(bits, times, self.omega)
        self.output_wire.write_buffer(result, times)

class VectorizedFSKModulator(Component):
    def __init__(self, input_wire, output_wire, freq_0, freq_1, baud_rate):
        super().__init__(input_wire, output_wire)
        self.omega0 = 2 * np.pi * freq_0
        self.omega1 = 2 * np.pi * freq_1
        
    def tick_batch(self, times: np.ndarray):
        bits = self.input_wire.read_buffer()
        result = fsk_modulate(bits, times, self.omega0, self.omega1)
        self.output_wire.write_buffer(result, times)

class VectorizedPSKModulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, baud_rate):
        super().__init__(input_wire, output_wire)
        self.omega = 2 * np.pi * carrier_freq
        
    def tick_batch(self, times: np.ndarray):
        bits = self.input_wire.read_buffer()
        result = psk_modulate(bits, times, self.omega)
        self.output_wire.write_buffer(result, times)

class VectorizedAMModulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, modulation_index=0.5):
        super().__init__(input_wire, output_wire)
        self.omega = 2 * np.pi * carrier_freq
        self.modulation_index = modulation_index
        
    def tick_batch(self, times: np.ndarray):
        msg = self.input_wire.read_buffer()
        result = am_modulate(msg, times, self.omega, self.modulation_index)
        self.output_wire.write_buffer(result, times)

class VectorizedPMModulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, phase_deviation=np.pi/2):
        super().__init__(input_wire, output_wire)
        self.omega = 2 * np.pi * carrier_freq
        self.phase_deviation = phase_deviation
        
    def tick_batch(self, times: np.ndarray):
        msg = self.input_wire.read_buffer()
        result = pm_modulate(msg, times, self.omega, self.phase_deviation)
        self.output_wire.write_buffer(result, times)

class VectorizedFMModulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, freq_deviation=10.0):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.freq_deviation = freq_deviation
        self.last_phase = 0.0
        self.last_time = 0.0
        
    def tick_batch(self, times: np.ndarray):
        msg = self.input_wire.read_buffer()
        # Numba kernel handles state update
        result, new_phase, new_time = fm_modulate(
            msg, times, self.carrier_freq, self.freq_deviation, 
            self.last_phase, self.last_time
        )
        self.last_phase = new_phase
        self.last_time = new_time
        self.output_wire.write_buffer(result, times)

# --- Demodulators ---

from src.core.numba_kernels import (
    am_demodulate_kernel, 
    ask_demodulate_kernel, 
    fm_demodulate_kernel
)

class VectorizedAMDemodulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, modulation_index=0.5):
        super().__init__(input_wire, output_wire)
        self.modulation_index = modulation_index
        self.envelope = 1.0
        self.alpha = 0.02
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        output, self.envelope = am_demodulate_kernel(
            sig, self.alpha, self.modulation_index, self.envelope
        )
        self.output_wire.write_buffer(output, times)

class VectorizedFMDemodulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, freq_deviation=5.0):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.freq_deviation = freq_deviation
        
        # State
        self.prev_val = 0.0
        self.last_crossing = 0.0
        self.smoothed_val = 0.0
        self.alpha = 0.05
        self.inst_freq = carrier_freq
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        
        output, self.prev_val, self.last_crossing, \
        self.smoothed_val, self.inst_freq = fm_demodulate_kernel(
            sig, times, self.carrier_freq, self.freq_deviation,
            self.prev_val, self.last_crossing, self.alpha, self.smoothed_val, self.inst_freq
        )
        self.output_wire.write_buffer(output, times)

class VectorizedASKDemodulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, baud_rate):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        
        # State
        self.last_bit_index = -1
        self.accumulator = 0.0
        self.sample_count = 0
        self.decoded_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        output, self.last_bit_index, self.accumulator, self.sample_count, self.decoded_val = ask_demodulate_kernel(
            sig, times, self.bit_duration, self.last_bit_index, self.accumulator, self.sample_count, self.decoded_val
        )
        self.output_wire.write_buffer(output, times)

# --- Digital Encoder Wrappers ---

from src.core.numba_kernels import (
    nrz_l_kernel, nrzi_kernel, manchester_kernel,
    ami_kernel, pseudoternary_kernel, diff_manchester_kernel
)

class VectorizedNRZLEncoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate=0, high_level=1.0, low_level=-1.0):
        super().__init__(input_wire, output_wire)
        self.high = high_level
        self.low = low_level
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res = nrz_l_kernel(sig, self.high, self.low)
        self.output_wire.write_buffer(res, times)

class VectorizedNRZIEncoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate, high_level=1.0, low_level=-1.0):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        self.high = high_level
        self.low = low_level
        
        # State
        self.current_level = low_level
        self.last_bit_index = -1
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.current_level, self.last_bit_index = nrzi_kernel(
            times, sig, self.rate, self.high, self.low, 
            self.current_level, self.last_bit_index
        )
        self.output_wire.write_buffer(res, times)

class VectorizedManchesterEncoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.half_duration = self.bit_duration / 2.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res = manchester_kernel(
            times, sig, self.bit_duration, self.half_duration
        )
        self.output_wire.write_buffer(res, times)

class VectorizedAMIEncoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        self.last_polarity = -1.0
        self.last_bit_index = -1
        self.current_holding_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_polarity, self.last_bit_index, self.current_holding_val = ami_kernel(
            times, sig, self.rate, self.last_polarity, self.last_bit_index, self.current_holding_val
        )
        self.output_wire.write_buffer(res, times)

class VectorizedPseudoternaryEncoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        self.last_polarity = -1.0
        self.last_bit_index = -1
        self.current_holding_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_polarity, self.last_bit_index, self.current_holding_val = pseudoternary_kernel(
            times, sig, self.rate, self.last_polarity, self.last_bit_index, self.current_holding_val
        )
        self.output_wire.write_buffer(res, times)

class VectorizedDifferentialManchesterEncoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        self.bit_duration = 1.0 / baud_rate
        self.half_duration = self.bit_duration / 2.0
        
        # State
        self.prev_end_level = -1.0
        self.last_bit_index = -1
        self.current_start_level = -1.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
# --- Digital Decoder Wrappers ---

from src.core.numba_kernels import (
    nrz_l_decode_kernel, nrzi_decode_kernel,
    manchester_decode_kernel, ami_decode_kernel,
    pseudoternary_decode_kernel
)

class VectorizedNRZLDecoder(Component):
    def __init__(self, input_wire, output_wire, high_level=1.0, low_level=-1.0):
        super().__init__(input_wire, output_wire)
        self.high = high_level
        self.low = low_level
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res = nrz_l_decode_kernel(times, sig, self.high, self.low)
        self.output_wire.write_buffer(res, times)

class VectorizedNRZIDecoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate, high_level=1.0, low_level=-1.0):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        self.high = high_level
        self.low = low_level
        
        # State
        self.last_level = -1 # Assuming start at low/0
        self.last_bit_index = -1
        self.current_decoded_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_level, self.last_bit_index, self.current_decoded_val = nrzi_decode_kernel(
            times, sig, self.rate, self.high, self.low,
            self.last_level, self.last_bit_index, self.current_decoded_val
        )
        self.output_wire.write_buffer(res, times)

class VectorizedManchesterDecoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.half_duration = self.bit_duration / 2.0
        
        # State
        self.last_bit_index = -1
        self.current_decoded_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_bit_index, self.current_decoded_val = manchester_decode_kernel(
            times, sig, self.bit_duration, self.half_duration,
            self.last_bit_index, self.current_decoded_val
        )
        self.output_wire.write_buffer(res, times)

class VectorizedAMIDecoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        
        # State
        self.last_bit_index = -1
        self.current_decoded_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_bit_index, self.current_decoded_val = ami_decode_kernel(
            times, sig, self.rate, self.last_bit_index, self.current_decoded_val
        )
        self.output_wire.write_buffer(res, times)

class VectorizedPseudoternaryDecoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.rate = baud_rate
        
        # State
        self.last_bit_index = -1
        self.current_decoded_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_bit_index, self.current_decoded_val = pseudoternary_decode_kernel(
            times, sig, self.rate, self.last_bit_index, self.current_decoded_val
        )
        self.output_wire.write_buffer(res, times)

class VectorizedDifferentialManchesterDecoder(Component):
    def __init__(self, input_wire, output_wire, baud_rate):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.quarter_duration = self.bit_duration / 4.0
        
        # State
        self.last_bit_index = -1
        self.last_end_level = -1.0 # Assume previous bit ended Low
        self.current_decoded_val = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        # Import kernel here if not at top? It is at top.
        from src.core.numba_kernels import diff_manchester_decode_kernel
        
        res, self.last_bit_index, self.last_end_level, self.current_decoded_val = diff_manchester_decode_kernel(
            times, sig, self.bit_duration, self.quarter_duration,
            self.last_bit_index, self.last_end_level, self.current_decoded_val
        )
        self.output_wire.write_buffer(res, times)

# --- Analog-Digital Wrappers ---

from src.core.numba_kernels import (
    pcm_encode_kernel, pcm_decode_kernel,
    delta_encode_kernel, delta_decode_kernel
)

class VectorizedPCMEncoder(Component):
    def __init__(self, input_wire, output_wire, sample_rate, n_bits=4, v_min=-1.0, v_max=1.0):
        super().__init__(input_wire, output_wire)
        self.sample_rate = sample_rate
        self.bit_rate = sample_rate * n_bits
        self.n_bits = n_bits
        self.v_min = v_min
        self.v_range_inv = 1.0 / (v_max - v_min)
        self.n_levels_m1 = (2 ** n_bits) - 1
        
        # State
        self.last_sample_index = -1
        self.current_code = 0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_sample_index, self.current_code = pcm_encode_kernel(
            times, sig, self.sample_rate, self.bit_rate,
            self.n_bits, self.v_min, self.v_range_inv, self.n_levels_m1,
            self.last_sample_index, self.current_code
        )
        self.output_wire.write_buffer(res, times)

class VectorizedPCMDecoder(Component):
    def __init__(self, input_wire, output_wire, sample_rate, n_bits=4, v_min=-1.0, v_max=1.0):
        super().__init__(input_wire, output_wire)
        self.bit_rate = sample_rate * n_bits
        self.n_bits = n_bits
        self.v_min = v_min
        self.step_size = (v_max - v_min) / ((2 ** n_bits) - 1)
        
        # State
        self.last_bit_index = -1
        self.assembly_reg = 0
        self.bits_collected = 0
        self.current_output = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_bit_index, self.assembly_reg, \
        self.bits_collected, self.current_output = pcm_decode_kernel(
            times, sig, self.bit_rate, self.n_bits,
            self.v_min, self.step_size,
            self.last_bit_index, self.assembly_reg, 
            self.bits_collected, self.current_output
        )
        self.output_wire.write_buffer(res, times)

class VectorizedDeltaEncoder(Component):
    def __init__(self, input_wire, output_wire, sample_rate, step_size=0.1):
        super().__init__(input_wire, output_wire)
        self.sample_rate = sample_rate
        self.step_size = step_size
        
        # State
        self.last_sample_index = -1
        self.approximation = 0.0
        self.current_bit = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_sample_index, self.approximation, self.current_bit = delta_encode_kernel(
            times, sig, self.sample_rate, self.step_size,
            self.last_sample_index, self.approximation, self.current_bit
        )
        self.output_wire.write_buffer(res, times)

class VectorizedDeltaDecoder(Component):
    def __init__(self, input_wire, output_wire, sample_rate, step_size=0.1):
        super().__init__(input_wire, output_wire)
        self.sample_rate = sample_rate
        self.step_size = step_size
        
        # State
        self.last_sample_index = -1
        self.approximation = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_sample_index, self.approximation = delta_decode_kernel(
            times, sig, self.sample_rate, self.step_size,
            self.last_sample_index, self.approximation
        )
        self.output_wire.write_buffer(res, times)

# --- Other Demodulators ---

from src.core.numba_kernels import (
    fsk_demodulate_kernel, psk_demodulate_kernel
)

class VectorizedFSKDemodulator(Component):
    def __init__(self, input_wire, output_wire, freq_0, freq_1, baud_rate):
        super().__init__(input_wire, output_wire)
        self.bit_duration = 1.0 / baud_rate
        self.threshold = (freq_0 + freq_1) / 2.0
        
        # State
        self.last_bit_index = -1
        self.last_val = 0.0
        self.zero_crossings = 0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_bit_index, self.last_val, self.zero_crossings, _ = fsk_demodulate_kernel(
            times, sig, self.bit_duration, self.threshold,
            self.last_bit_index, self.last_val, self.zero_crossings
        )
        self.output_wire.write_buffer(res, times)

class VectorizedPSKDemodulator(Component):
    def __init__(self, input_wire, output_wire, carrier_freq, baud_rate):
        super().__init__(input_wire, output_wire)
        self.carrier_freq = carrier_freq
        self.bit_duration = 1.0 / baud_rate
        
        # State
        self.last_bit_index = -1
        self.accumulator = 0.0
        self.sample_count = 0
        self.decoded_bit = 0.0
        
    def tick_batch(self, times: np.ndarray):
        sig = self.input_wire.read_buffer()
        res, self.last_bit_index, self.accumulator, self.sample_count, self.decoded_bit = psk_demodulate_kernel(
            times, sig, self.bit_duration, self.carrier_freq,
            self.last_bit_index, self.accumulator, self.sample_count, self.decoded_bit
        )
        self.output_wire.write_buffer(res, times)
