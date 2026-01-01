from src.core.components.base import Wire
from src.core.engine import Simulation
from src.modules.generators import create_digital_signal
from src.modules.line_coding import ManchesterEncoder, NRZLEncoder


def line_coding():
    w_input = Wire("Raw Input")
    w_nrzl_encoded = Wire("NRZL Encoded")
    w_manchester_encoded = Wire("Manchester Encoded")

    baud_rate = 5.0
    input_func = create_digital_signal("1011010111", baud_rate=baud_rate)

    sim = Simulation(
        input_wire=w_input,
        input_function=input_func,
        dt=0.001
    )

    sim.add_component(ManchesterEncoder(w_input,
                                        w_nrzl_encoded,
                                        baud_rate=baud_rate))
    sim.add_component(NRZLEncoder(w_input,
                                  w_manchester_encoded))

    return sim
