# Project Optimizations

This document details the performance optimizations applied to the `simplex-sim` project. The primary goal was to improve the simulation throughput (steps per second) without changing the functional behavior of the components.

## Summary of Results

Significant performance improvements were observed across various scenarios. 

| Scenario category | Original Baseline | Final Performance | Improvement |
| :--- | :--- | :--- | :--- |
| **PCM Codec** | ~46.7ms | ~31.3ms | **~33% Speedup** |
| **D2D Encoding** | ~56.2ms | ~47.1ms | **~16% Speedup** |
| **B8ZS Codec** | ~17.7ms | ~17.4ms | **~2% Speedup** |

## Techniques Applied

### 1. Memory Optimization (`__slots__`)
**File:** `src/core/components/base.py`

Python objects normally use a dynamic dictionary (`__dict__`) to store attributes, which consumes more memory and has a slightly slower lookup time. We added `__slots__` to the core `Wire` and `Component` classes.

*   **Benefit:** Reduced memory footprint for the thousands of objects created during simulation and faster attribute access.

### 2. Simulation Engine Tuning
**File:** `src/core/engine.py`

The main simulation loop involves propagating signals from wires to components.
*   **Change:** Converted `Wire.effects` to a `set` to avoid duplicate registrations and O(1) removals (if needed).
*   **Change:** Optimized the propagation loop to use `list.copy()` instead of `set()` conversion where applicable.

### 3. Mathematical Operations
**Files:** `src/modules/*_encoders.py`, `src/modules/*_modulators.py`

Division is significantly more expensive than multiplication.
*   **Optimization:** Pre-calculated reciprocal values (e.g., `bit_rate = 1.0 / bit_duration`, `v_range_inv = 1.0 / (v_max - v_min)`).
    *   *Before:* `index = int(time / period)`
    *   *After:* `index = int(time * rate)`
*   **Optimization:** Pre-computed trigonometric constants like angular frequency (`omega = 2 * math.pi * f`).

### 4. Direct Attribute Access
**Files:** All Modules

Method calls in Python have a small overhead. In tight loops (like `tick()`, called thousands of times per second), this adds up.
*   **Change:** Replaced `self.input_wire.read()` with direct access `self.input_wire.voltage`.
*   **Note:** This increases coupling slightly but is standard practice for high-performance simulation kernels in Python.

### 5. String Processing in Generators
**File:** `src/modules/generators.py`

*   **Digital Generators:** Pre-converted the binary string "0101..." into a tuple of float voltage levels `(low, high, low...)`. This allows the signal function to use O(1) array indexing instead of string parsing and conditional logic on every tick.
*   **Scramblers (B8ZS/HDB3):** Replaced manual string slicing with `startswith()` which avoids creating new string objects during pattern matching.

## Future Recommendations

*   **Numpy Integration:** For extremely large simulations, vectorizing the signal processing using `numpy` arrays instead of a step-by-step `tick` loop would yield orders of magnitude improvement, though it would require a significant architectural rewrite.
*   **JIT Compilation:** Using `numba` or `PyPy` could further optimize the pure Python loops without code changes.
