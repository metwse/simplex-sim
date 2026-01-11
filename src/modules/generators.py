from src.core.types import SignalGenerator

from typing import List


def create_digital_signal(bitstream: str,
                          baud_rate: float,
                          voltage_levels: tuple = (0.0, 1.0)) \
                            -> SignalGenerator:
    """Simple digital signal generator.

    Input `bitstream` is a string of ones and zeros.
    """

    low, high = voltage_levels
    bit_duration = 1.0 / baud_rate
    
    # Pre-calculate voltage sequence to avoid string parsing in loop
    levels = tuple(high if bit == '1' else low for bit in bitstream)
    total_bits = len(levels)

    def signal_func(time: float) -> float:
        if time < 0:
            return low

        bit_index = int(time * baud_rate) % total_bits
        return levels[bit_index]

    return signal_func


def _encode_b8zs(bitstream: str) -> List[float]:
    """Encode bitstream using B8ZS (Bipolar with 8-Zero Substitution).

    Replaces 8 consecutive zeros with a violation pattern:
    - Last pulse +: 000+-0-+
    - Last pulse -: 000-+0+-
    """

    result: List[float] = []
    last_polarity = 1.0
    i = 0
    length = len(bitstream)

    while i < length:
        if (i + 8 <= length and
                bitstream.startswith('00000000', i)):
            if last_polarity > 0:
                result.extend([0, 0, 0, 1, -1, 0, -1, 1])
            else:
                result.extend([0, 0, 0, -1, 1, 0, 1, -1])
            last_polarity = result[-1]
            i += 8
        elif bitstream[i] == '1':
            last_polarity = -last_polarity
            result.append(last_polarity)
            i += 1
        else:
            result.append(0.0)
            i += 1

    return result


def create_b8zs_signal(bitstream: str, baud_rate: float) -> SignalGenerator:
    """B8ZS encoded signal generator."""

    encoded = _encode_b8zs(bitstream)
    bit_duration = 1.0 / baud_rate
    total_bits = len(encoded)

    def signal_func(time: float) -> float:
        if time < 0:
            return 0.0

        bit_index = int(time / bit_duration) % total_bits
        return encoded[bit_index]

    return signal_func


def _encode_hdb3(bitstream: str) -> List[float]:
    """Encode bitstream using HDB3 (High Density Bipolar 3).

    Replaces 4 consecutive zeros with a violation pattern:
    - Odd 1s since last substitution: 000V
    - Even 1s since last substitution: B00V
    Where V = violation (same polarity), B = balancing pulse
    """

    result: List[float] = []
    last_polarity = 1.0
    ones_since_sub = 0
    i = 0
    length = len(bitstream)

    while i < length:
        if (i + 4 <= length and
                bitstream.startswith('0000', i)):
            if ones_since_sub % 2 == 1:
                violation = last_polarity
                result.extend([0, 0, 0, violation])
            else:
                balance = -last_polarity
                violation = balance
                result.extend([balance, 0, 0, violation])
                last_polarity = balance

            ones_since_sub = 0
            i += 4
        elif bitstream[i] == '1':
            last_polarity = -last_polarity
            result.append(last_polarity)
            ones_since_sub += 1
            i += 1
        else:
            result.append(0.0)
            i += 1

    return result


def create_hdb3_signal(bitstream: str, baud_rate: float) -> SignalGenerator:
    """HDB3 encoded signal generator."""

    encoded = _encode_hdb3(bitstream)
    bit_duration = 1.0 / baud_rate
    total_bits = len(encoded)

    def signal_func(time: float) -> float:
        if time < 0:
            return 0.0

        bit_index = int(time / bit_duration) % total_bits
        return encoded[bit_index]

    return signal_func
