from src.core.components.base import Wire
from src.core.engine import Simulation
from src.modules.generators import create_digital_signal
from src.modules.line_coding import ManchesterEncoder, NRZIEncoder, \
    NRZLEncoder, BipolarAMIEncoder, DifferentialManchesterEncoder, \
    PseudoternaryEncoder


def line_coding():
    w_input = Wire("Raw Input")
    w_nrzl_encoded = Wire("NRZL Encoded")
    w_nrzi_encoded = Wire("NRZI Encoded")
    w_manchester_encoded = Wire("Manchester Encoded")
    w_bipolar_ami_encoded = Wire("Bipolar AMI Encoded")
    w_differential_manchester_encoded = Wire("Differential Manchester Encoded")
    w_pseudoternary_encoded = Wire("Pseudoternary Encoded")

    baud_rate = 5.0
    input_func = create_digital_signal("0110101111010001001110110",
                                       baud_rate=baud_rate)

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
