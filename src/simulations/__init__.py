from .line_coding import line_coding

from typing import Callable, Dict, Generic, Type, TypeVar, TypedDict


T = TypeVar('T')


class ScenarioParamter(TypedDict, Generic[T]):
    type: Type[T]
    default: T


class Scenario(TypedDict):
    setup: Callable
    description: str
    parameters: Dict[str, ScenarioParamter]


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
}
