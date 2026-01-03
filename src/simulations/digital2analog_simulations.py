from .types import Scenario

from src.core.components.base import Wire
from src.core.engine import Simulation
from src.modules.generators import create_digital_signal
from src.modules.digital2analog_modulators import \
    ASKModulator, FSKModulator, PSKModulator
from src.modules.digital2analog_demodulators import \
    ASKDemodulator, FSKDemodulator, PSKDemodulator

from typing import Dict


def digital_to_analog(carrier_freq: float = 20.0,
                      baud_rate: float = 5.0,
                      bitstream: str = '10110010',
                      freq_0: float = 10.0,
                      freq_1: float = 25.0):
    """Showcase: displays ASK, FSK, and PSK side by side."""

    w_input = Wire("Digital Input")
    w_ask = Wire("ASK Modulated")
    w_fsk = Wire("FSK Modulated")
    w_psk = Wire("PSK Modulated")

    input_func = create_digital_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(ASKModulator(w_input, w_ask,
                                   carrier_freq=carrier_freq,
                                   baud_rate=baud_rate))
    sim.add_component(FSKModulator(w_input, w_fsk,
                                   freq_0=freq_0,
                                   freq_1=freq_1,
                                   baud_rate=baud_rate))
    sim.add_component(PSKModulator(w_input, w_psk,
                                   carrier_freq=carrier_freq,
                                   baud_rate=baud_rate))

    return sim


def ask_modem(carrier_freq: float = 20.0,
              baud_rate: float = 5.0,
              bitstream: str = '10110010'):
    """ASK modulator + demodulator chain."""

    w_input = Wire("Digital Input")
    w_modulated = Wire("ASK Modulated")
    w_demodulated = Wire("ASK Demodulated")

    input_func = create_digital_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(ASKModulator(w_input, w_modulated,
                                   carrier_freq=carrier_freq,
                                   baud_rate=baud_rate))
    sim.add_component(ASKDemodulator(w_modulated, w_demodulated,
                                     carrier_freq=carrier_freq,
                                     baud_rate=baud_rate))

    return sim


def fsk_modem(freq_0: float = 10.0,
              freq_1: float = 25.0,
              baud_rate: float = 5.0,
              bitstream: str = '10110010'):
    """FSK modulator + demodulator chain."""

    w_input = Wire("Digital Input")
    w_modulated = Wire("FSK Modulated")
    w_demodulated = Wire("FSK Demodulated")

    input_func = create_digital_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(FSKModulator(w_input, w_modulated,
                                   freq_0=freq_0,
                                   freq_1=freq_1,
                                   baud_rate=baud_rate))
    sim.add_component(FSKDemodulator(w_modulated, w_demodulated,
                                     freq_0=freq_0,
                                     freq_1=freq_1,
                                     baud_rate=baud_rate))

    return sim


def psk_modem(carrier_freq: float = 20.0,
              baud_rate: float = 5.0,
              bitstream: str = '10110010'):
    """PSK modulator + demodulator chain."""

    w_input = Wire("Digital Input")
    w_modulated = Wire("PSK Modulated")
    w_demodulated = Wire("PSK Demodulated")

    input_func = create_digital_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(PSKModulator(w_input, w_modulated,
                                   carrier_freq=carrier_freq,
                                   baud_rate=baud_rate))
    sim.add_component(PSKDemodulator(w_modulated, w_demodulated,
                                     carrier_freq=carrier_freq,
                                     baud_rate=baud_rate))

    return sim


D2A_SCENARIOS: Dict[str, Scenario] = {
    "Digital to Analog Modulation": {
        'setup': digital_to_analog,
        'description': "Showcases ASK, FSK, and PSK modulation.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': '10110010'},
            'freq_0': {'type': float, 'default': 10.0},
            'freq_1': {'type': float, 'default': 25.0}
        }
    },
    "Digital to Analog: ASK Modem": {
        'setup': ask_modem,
        'description': "ASK modulation and demodulation chain.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': '10110010'}
        }
    },
    "Digital to Analog: FSK Modem": {
        'setup': fsk_modem,
        'description': "FSK modulation and demodulation chain.",
        'parameters': {
            'freq_0': {'type': float, 'default': 10.0},
            'freq_1': {'type': float, 'default': 25.0},
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': '10110010'}
        }
    },
    "Digital to Analog: PSK Modem": {
        'setup': psk_modem,
        'description': "PSK modulation and demodulation chain.",
        'parameters': {
            'carrier_freq': {'type': float, 'default': 20.0},
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': '10110010'}
        }
    }
}
