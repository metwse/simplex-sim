
from .types import Scenario
from src.core.vectorized import VectorizedSimulation, VectorizedWire
from src.modules.vectorized_modules import (
    VectorizedAMModulator, VectorizedFMModulator, 
    VectorizedASKModulator, VectorizedFSKModulator,
    VectorizedAMDemodulator, VectorizedFMDemodulator,
    VectorizedASKDemodulator
)
import numpy as np

def create_raw_signal_generator(freq=1.0):
    omega = 2 * np.pi * freq
    def gene(times):
        return np.sin(omega * times)
    return gene

def create_digital_generator(bitstream, baud_rate):
    bit_duration = 1.0 / baud_rate
    bits = np.array([float(b) for b in bitstream], dtype=np.float64)
    n_bits = len(bits)
    
    def gene(times):
        indices = (times * baud_rate).astype(np.int64) % n_bits
        return bits[indices]
    return gene

def setup_am_vectorized(carrier_freq=10.0):
    w_in = VectorizedWire("Input Signal")
    w_mod = VectorizedWire("AM Modulated")
    w_out = VectorizedWire("Demodulated Output")
    
    gen = create_raw_signal_generator(1.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    mod = VectorizedAMModulator(w_in, w_mod, carrier_freq=carrier_freq)
    demod = VectorizedAMDemodulator(w_mod, w_out, carrier_freq=carrier_freq)
    
    sim.add_component(mod)
    sim.add_component(demod)
    return sim

def setup_fm_vectorized(carrier_freq=10.0, freq_deviation=5.0):
    w_in = VectorizedWire("Input Signal")
    w_mod = VectorizedWire("FM Modulated")
    w_out = VectorizedWire("Demodulated Output")
    
    gen = create_raw_signal_generator(1.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    mod = VectorizedFMModulator(w_in, w_mod, carrier_freq=carrier_freq, freq_deviation=freq_deviation)
    demod = VectorizedFMDemodulator(w_mod, w_out, carrier_freq=carrier_freq, freq_deviation=freq_deviation)
    
    sim.add_component(mod)
    sim.add_component(demod)
    return sim

def setup_ask_vectorized(baud_rate=5.0, carrier_freq=20.0):
    w_in = VectorizedWire("Digital Input")
    w_mod = VectorizedWire("ASK Modulated")
    w_out = VectorizedWire("Demodulated Output")
    
    gen = create_digital_generator("10110", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    mod = VectorizedASKModulator(w_in, w_mod, carrier_freq=carrier_freq, baud_rate=baud_rate)
    demod = VectorizedASKDemodulator(w_mod, w_out, carrier_freq=carrier_freq, baud_rate=baud_rate)
    
    sim.add_component(mod)
    sim.add_component(demod)
    return sim

# --- Digital Coding Scenarios ---

from src.modules.vectorized_modules import (
    VectorizedNRZLEncoder, VectorizedNRZIEncoder,
    VectorizedManchesterEncoder, VectorizedAMIEncoder,
    VectorizedPseudoternaryEncoder, VectorizedDifferentialManchesterEncoder,
    VectorizedNRZLDecoder, VectorizedNRZIDecoder,
    VectorizedManchesterDecoder, VectorizedAMIDecoder,
    VectorizedPseudoternaryDecoder, VectorizedDifferentialManchesterDecoder
)

def setup_nrz_l_vectorized(baud_rate=5.0):
    w_in = VectorizedWire("Digital Input")
    w_enc = VectorizedWire("NRZ-L Encoded")
    w_out = VectorizedWire("Decoded Output")
    
    gen = create_digital_generator("101101001", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedNRZLEncoder(w_in, w_enc, baud_rate=baud_rate)
    dec = VectorizedNRZLDecoder(w_enc, w_out)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

def setup_nrzi_vectorized(baud_rate=5.0):
    w_in = VectorizedWire("Digital Input")
    w_enc = VectorizedWire("NRZI Encoded")
    w_out = VectorizedWire("Decoded Output")
    
    gen = create_digital_generator("101101001", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedNRZIEncoder(w_in, w_enc, baud_rate=baud_rate)
    dec = VectorizedNRZIDecoder(w_enc, w_out, baud_rate=baud_rate)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

def setup_manchester_vectorized(baud_rate=5.0):
    w_in = VectorizedWire("Digital Input")
    w_enc = VectorizedWire("Manchester Encoded")
    w_out = VectorizedWire("Decoded Output")
    
    gen = create_digital_generator("101101001", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedManchesterEncoder(w_in, w_enc, baud_rate=baud_rate)
    dec = VectorizedManchesterDecoder(w_enc, w_out, baud_rate=baud_rate)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

def setup_ami_vectorized(baud_rate=5.0):
    w_in = VectorizedWire("Digital Input")
    w_enc = VectorizedWire("AMI Encoded")
    w_out = VectorizedWire("Decoded Output")
    
    gen = create_digital_generator("101101001", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedAMIEncoder(w_in, w_enc, baud_rate=baud_rate)
    dec = VectorizedAMIDecoder(w_enc, w_out, baud_rate=baud_rate)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

def setup_pseudoternary_vectorized(baud_rate=5.0):
    w_in = VectorizedWire("Digital Input")
    w_enc = VectorizedWire("Pseudoternary Encoded")
    w_out = VectorizedWire("Decoded Output")
    
    gen = create_digital_generator("101101001", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedPseudoternaryEncoder(w_in, w_enc, baud_rate=baud_rate)
    dec = VectorizedPseudoternaryDecoder(w_enc, w_out, baud_rate=baud_rate)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

def setup_diff_manchester_vectorized(baud_rate=5.0):
    w_in = VectorizedWire("Digital Input")
    w_enc = VectorizedWire("Diff. Manchester Encoded")
    w_out = VectorizedWire("Decoded Output")
    
    gen = create_digital_generator("101101001", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedDifferentialManchesterEncoder(w_in, w_enc, baud_rate=baud_rate)
    dec = VectorizedDifferentialManchesterDecoder(w_enc, w_out, baud_rate=baud_rate)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

# --- Digital-Analog Scenarios (FSK/PSK) ---

from src.modules.vectorized_modules import (
    VectorizedFSKModulator, VectorizedPSKModulator,
    VectorizedFSKDemodulator, VectorizedPSKDemodulator
)

def setup_fsk_vectorized(baud_rate=5.0, freq_0=10.0, freq_1=20.0):
    w_in = VectorizedWire("Digital Input")
    w_mod = VectorizedWire("FSK Modulated")
    w_out = VectorizedWire("Demodulated Output")
    
    gen = create_digital_generator("10110", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    mod = VectorizedFSKModulator(w_in, w_mod, freq_0=freq_0, freq_1=freq_1, baud_rate=baud_rate)
    demod = VectorizedFSKDemodulator(w_mod, w_out, freq_0=freq_0, freq_1=freq_1, baud_rate=baud_rate)
    
    sim.add_component(mod)
    sim.add_component(demod)
    return sim

def setup_psk_vectorized(baud_rate=5.0, carrier_freq=20.0):
    w_in = VectorizedWire("Digital Input")
    w_mod = VectorizedWire("PSK Modulated")
    w_out = VectorizedWire("Demodulated Output")
    
    gen = create_digital_generator("10110", baud_rate=baud_rate)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    mod = VectorizedPSKModulator(w_in, w_mod, carrier_freq=carrier_freq, baud_rate=baud_rate)
    demod = VectorizedPSKDemodulator(w_mod, w_out, carrier_freq=carrier_freq, baud_rate=baud_rate)
    
    sim.add_component(mod)
    sim.add_component(demod)
    return sim

# --- A2D Scenarios ---

from src.modules.vectorized_modules import (
    VectorizedPCMEncoder, VectorizedPCMDecoder,
    VectorizedDeltaEncoder, VectorizedDeltaDecoder
)

def setup_pcm_vectorized(sample_rate=20.0, n_bits=4):
    w_in = VectorizedWire("Analog Input")
    w_digital = VectorizedWire("PCM Digital Stream")
    w_out = VectorizedWire("Reconstructed Output")
    
    gen = create_raw_signal_generator(1.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedPCMEncoder(w_in, w_digital, sample_rate, n_bits=int(n_bits))
    dec = VectorizedPCMDecoder(w_digital, w_out, sample_rate, n_bits=int(n_bits))
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

def setup_delta_vectorized(sample_rate=50.0, step_size=0.1):
    w_in = VectorizedWire("Analog Input")
    w_digital = VectorizedWire("Delta Bitstream")
    w_out = VectorizedWire("Reconstructed Output")
    
    gen = create_raw_signal_generator(1.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.001, batch_size=1000)
    
    enc = VectorizedDeltaEncoder(w_in, w_digital, sample_rate, step_size)
    dec = VectorizedDeltaDecoder(w_digital, w_out, sample_rate, step_size)
    
    sim.add_component(enc)
    sim.add_component(dec)
    return sim

VECTORIZED_SCENARIOS = {
    "Vectorized: AM Modulation": {
        'setup': setup_am_vectorized,
        'description': "High-performance Vectorized AM Modulation (Numpy/Numba)",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 10.0}
        }
    },
    "Vectorized: FM Modulation": {
        'setup': setup_fm_vectorized,
        'description': "High-performance Vectorized FM Modulation (Numpy/Numba)",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 10.0},
            'freq_deviation': {'type': float, 'default': 5.0}
        }
    },
    "Vectorized: ASK Modulation": {
        'setup': setup_ask_vectorized,
        'description': "High-performance Vectorized ASK Modulation (Numpy/Numba)",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'baud_rate': {'type': float, 'default': 5.0}
        }
    },
    "Vectorized: NRZ-L": {
        'setup': setup_nrz_l_vectorized,
        'description': "Vectorized NRZ-L Encoding",
        'parameters': {'baud_rate': {'default': 5.0, 'type': float}}
    },
    "Vectorized: NRZI": {
        'setup': setup_nrzi_vectorized,
        'description': "Vectorized NRZI Encoding",
        'parameters': {'baud_rate': {'default': 5.0, 'type': float}}
    },
    "Vectorized: Manchester": {
        'setup': setup_manchester_vectorized,
        'description': "Vectorized Manchester Encoding",
        'parameters': {'baud_rate': {'default': 5.0, 'type': float}}
    },
    "Vectorized: Bipolar AMI": {
        'setup': setup_ami_vectorized,
        'description': "Vectorized Bipolar AMI Encoding",
        'parameters': {'baud_rate': {'default': 5.0, 'type': float}}
    },
    "Vectorized: Pseudoternary": {
        'setup': setup_pseudoternary_vectorized,
        'description': "Vectorized Pseudoternary Encoding",
        'parameters': {'baud_rate': {'default': 5.0, 'type': float}}
    },
    "Vectorized: Delta Modulation": {
        'setup': setup_delta_vectorized,
        'description': "Vectorized Delta Modulation",
        'parameters': {
            'sample_rate': {'default': 50.0, 'type': float},
            'step_size': {'default': 0.1, 'type': float}
        }
    }, 
    "Vectorized: FSK Modulation": {
        'setup': setup_fsk_vectorized,
        'description': "Vectorized Frequency Shift Keying",
        'parameters': {
            'baud_rate': {'default': 5.0, 'type': float},
            'freq_0': {'default': 10.0, 'type': float},
            'freq_1': {'default': 20.0, 'type': float}
        }
    },
    "Vectorized: PSK Modulation": {
        'setup': setup_psk_vectorized,
        'description': "Vectorized Phase Shift Keying",
        'parameters': {
            'baud_rate': {'default': 5.0, 'type': float},
            'carrier_freq': {'default': 20.0, 'type': float},
        }
    },
}
