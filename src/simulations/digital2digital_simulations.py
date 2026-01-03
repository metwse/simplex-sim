from .types import Scenario

from src.core.components.base import Wire
from src.core.engine import Simulation
from src.modules.generators import create_digital_signal
from src.modules.digital2digital_encoders import ManchesterEncoder, \
    NRZIEncoder, NRZLEncoder, BipolarAMIEncoder, \
    DifferentialManchesterEncoder, PseudoternaryEncoder
from src.modules.digital2digital_decoders import ManchesterDecoder, \
    NRZIDecoder, NRZLDecoder, BipolarAMIDecoder, \
    DifferentialManchesterDecoder, PseudoternaryDecoder

from typing import Dict
from functools import partial


def generic_codec_setup(baud_rate: float, bitstream: str, Encoder, Decoder):
    w_input = Wire("Raw Input")
    w_encoded = Wire(Encoder.__name__.replace("Encoder", " Encoded"))
    w_decoded = Wire(Decoder.__name__.replace("Decoder", " Decoded"))

    input_func = create_digital_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(Encoder(w_input, w_encoded,
                              baud_rate=baud_rate))
    sim.add_component(Decoder(w_encoded, w_decoded,
                              baud_rate=baud_rate))

    return sim


CODEC_PAIRS = [
    [ManchesterEncoder, ManchesterDecoder],
    [NRZIEncoder, NRZIDecoder],
    [NRZLEncoder, NRZLDecoder],
    [BipolarAMIEncoder, BipolarAMIDecoder],
    [DifferentialManchesterEncoder, DifferentialManchesterDecoder],
    [PseudoternaryEncoder, PseudoternaryDecoder],
]


CODEC_SCENARIOS: Dict[str, Scenario] = {
    f"Digital to Digital: {enc.__name__.replace("Encoder", "")} Codec": {
        'setup': partial(generic_codec_setup, Encoder=enc, Decoder=dec),
        'description': (f"Demonstrates {enc.__name__.replace('Encoder', '')} "
                        f"encoding and decoding logic."),
        'parameters': {
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': '01001100011'}
        }
    }
    for enc, dec in CODEC_PAIRS
}
