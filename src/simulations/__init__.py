from .digital2digital_simulations import CODEC_SCENARIOS
from .line_coding import line_coding
from .types import Scenario

from typing import Dict


SCENARIOS: Dict[str, Scenario] = {
    "Line Coding": {
        'setup': line_coding,
        'description': "Showcases digital encoding formats that does not "
                       "require lookaheading",
        'parameters': {
            'baud_rate': {'type': float, 'default': 5.0},
            'bitstream': {'type': str, 'default': "01001100011011101010"}
        }
    },
    **CODEC_SCENARIOS
}
