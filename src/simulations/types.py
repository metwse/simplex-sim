from typing import Callable, Generic, Type, TypeVar, TypedDict, Dict


T = TypeVar('T')


class ScenarioParamter(TypedDict, Generic[T]):
    type: Type[T]
    default: T


class Scenario(TypedDict):
    setup: Callable
    description: str
    parameters: Dict[str, ScenarioParamter]
