from .types import Scenario

from src.core.components.base import Wire
from src.core.engine import Simulation
from src.modules.analog2analog_modulators import \
    AMModulator, FMModulator, PMModulator
from src.modules.analog2analog_demodulators import \
    AMDemodulator, FMDemodulator, PMDemodulator

from typing import Dict, Callable
import math


DEFAULT_SIGNAL = 'lambda t: math.sin(2 * math.pi * t)'


def parse_signal_func(func_str: str) -> Callable[[float], float]:
    """Parses a lambda string into a callable function."""
    return eval(func_str, {'math': math, '__builtins__': {}})


def analog_to_analog(carrier_freq: float = 20.0,
                     modulation_index: float = 0.5,
                     freq_deviation: float = 5.0,
                     signal_func: str = DEFAULT_SIGNAL):
    """Showcase: displays AM, FM, and PM side by side."""

    w_input = Wire("Analog Input")
    w_am = Wire("AM Modulated")
    w_fm = Wire("FM Modulated")
    w_pm = Wire("PM Modulated")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.00001
    )

    sim.add_component(AMModulator(w_input, w_am,
                                  carrier_freq=carrier_freq,
                                  modulation_index=modulation_index))
    sim.add_component(FMModulator(w_input, w_fm,
                                  carrier_freq=carrier_freq,
                                  freq_deviation=freq_deviation))
    sim.add_component(PMModulator(w_input, w_pm,
                                  carrier_freq=carrier_freq))

    return sim


def am_modem(carrier_freq: float = 20.0,
             modulation_index: float = 0.5,
             signal_func: str = DEFAULT_SIGNAL):
    """AM modulator + demodulator chain."""

    w_input = Wire("Analog Input")
    w_modulated = Wire("AM Modulated")
    w_demodulated = Wire("AM Demodulated")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.0001
    )

    sim.add_component(AMModulator(w_input, w_modulated,
                                  carrier_freq=carrier_freq,
                                  modulation_index=modulation_index))
    sim.add_component(AMDemodulator(w_modulated, w_demodulated,
                                    carrier_freq=carrier_freq,
                                    modulation_index=modulation_index))

    return sim


def fm_modem(carrier_freq: float = 20.0,
             freq_deviation: float = 5.0,
             signal_func: str = DEFAULT_SIGNAL):
    """FM modulator + demodulator chain."""

    w_input = Wire("Analog Input")
    w_modulated = Wire("FM Modulated")
    w_demodulated = Wire("FM Demodulated")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.00001
    )

    sim.add_component(FMModulator(w_input, w_modulated,
                                  carrier_freq=carrier_freq,
                                  freq_deviation=freq_deviation))
    sim.add_component(FMDemodulator(w_modulated, w_demodulated,
                                    carrier_freq=carrier_freq,
                                    freq_deviation=freq_deviation))

    return sim


def pm_modem(carrier_freq: float = 20.0,
             phase_deviation: float = 1.57,
             signal_func: str = DEFAULT_SIGNAL):
    """PM modulator + demodulator chain."""

    w_input = Wire("Analog Input")
    w_modulated = Wire("PM Modulated")
    w_demodulated = Wire("PM Demodulated")

    input_func = parse_signal_func(signal_func)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.00001
    )

    sim.add_component(PMModulator(w_input, w_modulated,
                                  carrier_freq=carrier_freq,
                                  phase_deviation=phase_deviation))
    sim.add_component(PMDemodulator(w_modulated, w_demodulated,
                                    carrier_freq=carrier_freq,
                                    phase_deviation=phase_deviation))

    return sim


A2A_SCENARIOS: Dict[str, Scenario] = {
    "Analog to Analog Modulation": {
        'setup': analog_to_analog,
        'description': "Showcases AM, FM, and PM modulation.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'modulation_index': {'type': float, 'default': 0.5},
            'freq_deviation': {'type': float, 'default': 5.0},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    },
    "Analog to Analog: AM Modem": {
        'setup': am_modem,
        'description': "AM modulation and demodulation chain.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'modulation_index': {'type': float, 'default': 0.5},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    },
    "Analog to Analog: FM Modem": {
        'setup': fm_modem,
        'description': "FM modulation and demodulation chain.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'freq_deviation': {'type': float, 'default': 5.0},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    },
    "Analog to Analog: PM Modem": {
        'setup': pm_modem,
        'description': "PM modulation and demodulation chain.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'phase_deviation': {'type': float, 'default': 1.57},
            'signal_func': {'type': str, 'default': DEFAULT_SIGNAL}
        }
    }
}
