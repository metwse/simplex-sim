from .types import Scenario

from src.core.components import Wire
from src.core.engine import Simulation
from src.modules.generators import create_digital_signal, \
    create_b8zs_signal, create_hdb3_signal
from src.modules.digital2digital_encoders import ManchesterEncoder, \
    NRZIEncoder, NRZLEncoder, BipolarAMIEncoder, \
    DifferentialManchesterEncoder, PseudoternaryEncoder
from src.modules.digital2digital_decoders import ManchesterDecoder, \
    NRZIDecoder, NRZLDecoder, BipolarAMIDecoder, \
    DifferentialManchesterDecoder, PseudoternaryDecoder
from src.modules.scrambling_decoders import B8ZSDecoder, HDB3Decoder

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


def b8zs_codec(baud_rate: float = 5.0,
               bitstream: str = "10000000001"):
    """B8ZS scrambler + descrambler chain."""

    w_scrambled = Wire("B8ZS Scrambled")
    w_decoded = Wire("B8ZS Decoded")

    input_func = create_b8zs_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_scrambled,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(B8ZSDecoder(w_scrambled, w_decoded,
                                  baud_rate=baud_rate))

    return sim


def hdb3_codec(baud_rate: float = 5.0,
               bitstream: str = "10000100001"):
    """HDB3 scrambler + descrambler chain."""

    w_scrambled = Wire("HDB3 Scrambled")
    w_decoded = Wire("HDB3 Decoded")

    input_func = create_hdb3_signal(bitstream, baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_scrambled,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(HDB3Decoder(w_scrambled, w_decoded,
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
    },
    "Digital to Digital: B8ZS Codec": {
        'setup': b8zs_codec,
        'description': "B8ZS scrambling and descrambling (8-zero substitution)",
        'parameters': {
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': "10000000001"}
        }
    },
    "Digital to Digital: HDB3 Codec": {
        'setup': hdb3_codec,
        'description': "HDB3 scrambling and descrambling (4-zero substitution)",
        'parameters': {
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': "10000100001"}
        }
    },
    **{
        f"Digital to Digital: {enc.__name__.replace('Encoder', '')} Codec": {
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

