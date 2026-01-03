from .types import Scenario

from src.core.components.base import Wire
from src.core.engine import Simulation
from src.modules.analog2digital_encoders import \
    DeltaModulationEncoder, PCMEncoder
from src.modules.analog2digital_decoders import \
    DeltaModulationDecoder, PCMDecoder

from typing import Dict, Callable
import math


DEFAULT_SIGNAL = 'lambda t: math.sin(2 * math.pi * t)'


def parse_signal_func(func_str: str) -> Callable[[float], float]:
    """Parses a lambda string into a callable function."""
    return eval(func_str, {'math': math, '__builtins__': {}})


def analog_to_digital(sample_rate: float = 20.0,
                      n_bits: int = 4,
                      step_size: float = 0.1,
                      signal_func: str = DEFAULT_SIGNAL):
    """Showcase scenario: displays Delta Modulation and PCM side by side."""

    w_input = Wire("Analog Input")
    w_dm = Wire("Delta Modulation Encoded")
    w_pcm = Wire("PCM Encoded")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(DeltaModulationEncoder(w_input, w_dm,
                                             sample_rate=sample_rate,
                                             step_size=step_size))
    sim.add_component(PCMEncoder(w_input, w_pcm,
                                 sample_rate=sample_rate,
                                 n_bits=n_bits))

    return sim


def dm_codec(sample_rate: float = 20.0,
             step_size: float = 0.1,
             signal_func: str = DEFAULT_SIGNAL):
    """Delta Modulation encoder + decoder chain."""

    w_input = Wire("Analog Input")
    w_encoded = Wire("DM Encoded")
    w_decoded = Wire("DM Decoded")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(DeltaModulationEncoder(w_input, w_encoded,
                                             sample_rate=sample_rate,
                                             step_size=step_size))
    sim.add_component(DeltaModulationDecoder(w_encoded, w_decoded,
                                             sample_rate=sample_rate,
                                             step_size=step_size))

    return sim


def pcm_codec(sample_rate: float = 20.0,
              n_bits: int = 4,
              signal_func: str = DEFAULT_SIGNAL):
    """PCM encoder + decoder chain."""

    w_input = Wire("Analog Input")
    w_encoded = Wire("PCM Encoded")
    w_decoded = Wire("PCM Decoded")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(PCMEncoder(w_input, w_encoded,
                                 sample_rate=sample_rate,
                                 n_bits=n_bits))
    sim.add_component(PCMDecoder(w_encoded, w_decoded,
                                 sample_rate=sample_rate,
                                 n_bits=n_bits))

    return sim


A2D_SCENARIOS: Dict[str, Scenario] = {
    "Analog to Digital Encoding": {
        'setup': analog_to_digital,
        'description': "Showcases Delta Modulation and PCM encoding.",
        'parameters': {
            'sample_rate': {'type': float, 'default': 20.0},
            'n_bits': {'type': int, 'default': 4},
            'step_size': {'type': float, 'default': 0.1},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    },
    "Analog to Digital: Delta Modulation Codec": {
        'setup': dm_codec,
        'description': "Delta Modulation encoding and decoding chain.",
        'parameters': {
            'sample_rate': {'type': float, 'default': 20.0},
            'step_size': {'type': float, 'default': 0.1},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    },
    "Analog to Digital: PCM Codec": {
        'setup': pcm_codec,
        'description': "PCM encoding and decoding chain.",
        'parameters': {
            'sample_rate': {'type': float, 'default': 20.0},
            'n_bits': {'type': int, 'default': 4},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    }
}
