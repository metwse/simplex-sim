from .digital2digital_simulations import D2D_SCENARIOS
from .analog2digital_simulations import A2D_SCENARIOS
from .digital2analog_simulations import D2A_SCENARIOS
from .analog2analog_simulations import A2A_SCENARIOS
from .types import Scenario

from typing import Dict


SCENARIOS: Dict[str, Scenario] = {
    **D2D_SCENARIOS,
    **A2D_SCENARIOS,
    **D2A_SCENARIOS,
    **A2A_SCENARIOS
}
