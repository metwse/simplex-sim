from src.core.types import SignalGenerator

import math


def create_digital_signal(bitstream: str,
                          baud_rate: float,
                          voltage_levels: tuple = (0.0, 1.0)) \
                            -> SignalGenerator:
    """Simple digital signal generator.

    Input `bitstream` is a string of ones and zeros.
    """

    low, high = voltage_levels
    bit_duration = 1.0 / baud_rate
    total_bits = len(bitstream)

    def signal_func(time: float) -> float:
        if time < 0:
            return low

        bit_index = int(time / bit_duration) % total_bits

        return high if bitstream[bit_index] == '1' else low

    return signal_func


def create_sine_wave(frequency: float,
                     amplitude: float = 1.0,
                     phase: float = 0.0) -> SignalGenerator:
    """Sinusoidal wave generator."""

    def signal_func(time: float) -> float:
        return amplitude * math.sin(2 * math.pi * frequency * time + phase)

    return signal_func


def create_silence() -> SignalGenerator:
    """0-generating empty signal."""

    return lambda _: 0.0
