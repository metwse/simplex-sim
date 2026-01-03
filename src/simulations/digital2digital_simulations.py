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


def line_coding(baud_rate: float = 5.0,
                bitstream: str = "01001100011011101010"):
    w_input = Wire("Raw Input")
    w_nrzl_encoded = Wire("NRZL Encoded")
    w_nrzi_encoded = Wire("NRZI Encoded")
    w_manchester_encoded = Wire("Manchester Encoded")
    w_bipolar_ami_encoded = Wire("Bipolar AMI Encoded")
    w_differential_manchester_encoded = Wire("Differential Manchester Encoded")
    w_pseudoternary_encoded = Wire("Pseudoternary Encoded")

    input_func = create_digital_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(NRZLEncoder(w_input,
                                  w_nrzl_encoded))
    sim.add_component(NRZIEncoder(w_input,
                                  w_nrzi_encoded,
                                  baud_rate=baud_rate))
    sim.add_component(ManchesterEncoder(w_input,
                                        w_manchester_encoded,
                                        baud_rate=baud_rate))
    sim.add_component(
        DifferentialManchesterEncoder(w_input,
                                      w_differential_manchester_encoded,
                                      baud_rate=baud_rate))
    sim.add_component(
        BipolarAMIEncoder(w_input,
                          w_bipolar_ami_encoded,
                          baud_rate=baud_rate))
    sim.add_component(PseudoternaryEncoder(w_input,
                                           w_pseudoternary_encoded,
                                           baud_rate=baud_rate))

    return sim


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


D2D_SCENARIOS: Dict[str, Scenario] = {
    "Digital to Digital Encoding": {
        'setup': line_coding,
        'description': "Showcases digital encoding formats that does not "
                       "require lookaheading",
        'parameters': {
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': "01001100011011101010"}
        }
    }, **{
        f"Digital to Digital: {enc.__name__.replace("Encoder", "")} Codec": {
            'setup': partial(generic_codec_setup, Encoder=enc, Decoder=dec),
            'description': ("Demonstrates "
                            f"{enc.__name__.replace('Encoder', '')} "
                            "encoding and decoding logic."),
            'parameters': {
                'baud_rate': {'type': float, 'default': 5.0},
                'bitstream': {'type': str, 'default': '01001100011'}
            }
        }
        for enc, dec in CODEC_PAIRS
    }
}
