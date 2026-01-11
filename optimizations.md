# Comprehensive Optimization Report

## 1. Executive Summary

This report details the performance improvements achieved by migrating the `simplex-sim` simulation engine to a vectorized architecture using **NumPy** and **Numba**.

The optimization effort focused on replacing Python-loop-based signal processing with JIT-compiled kernels and batch processing. The results demonstrate massive throughput gains, ranging from **47x to over 100x** speedups across all implemented algorithms.

**Average System Throughput:**
- **Initial:** ~305,000 steps/s
- **Final:** ~22,186,000 steps/s
- **Overall Improvement:** ~72x (7200%)

## 2. Methodology

The optimization strategy consisted of three phases:

1.  **Vectorization**: Moving from single-sample processing (`tick()`) to batch processing (`advance_batch()`). This reduces function call overhead and leverages CPU cache locality.
2.  **JIT Compilation**: Porting core DSP logic (modulation, encoding, decoding) to **Numba** kernels (`@jit(nopython=True)`). This compiles Python code to optimized machine code, eliminating the interpreter lock for heavy math.
3.  **Memory Layout**: Using contiguous NumPy arrays for history and signal buffers instead of Python lists, reducing memory fragmentation.

## 3. Performance Benchmark

The following table compares the initial Python-only implementation with the final Vectorized+JIT implementation.
*Note: Algorithms removed from the scope (B8ZS, HDB3, PCM, Differential Manchester) are excluded.*

### Digital-to-Digital Encoding

| Algorithm | Initial (steps/s) | Vectorized (steps/s) | Speedup Factor | Improvement % |
| :--- | :--- | :--- | :--- | :--- |
| **NRZ-L** | 321,554 | 32,630,343 | **101.5x** | +10,047% |
| **Pseudoternary** | 330,555 | 35,401,640 | **107.1x** | +10,609% |
| **Bipolar AMI** | 304,241 | 23,549,969 | **77.4x** | +7,640% |
| **NRZI** | 302,286 | 21,624,156 | **71.5x** | +7,053% |
| **Manchester** | 299,296 | 14,276,898 | **47.7x** | +4,670% |

### Digital-to-Analog Modulation

| Algorithm | Initial (steps/s) | Vectorized (steps/s) | Speedup Factor | Improvement % |
| :--- | :--- | :--- | :--- | :--- |
| **ASK** | 280,812 | 22,130,971 | **78.8x** | +7,781% |
| **FSK** | 315,350 | 22,241,954 | **70.5x** | +6,953% |
| **PSK** | 288,225 | 14,466,857 | **50.2x** | +4,919% |

### Analog-to-Analog Modulation

| Algorithm | Initial (steps/s) | Vectorized (steps/s) | Speedup Factor | Improvement % |
| :--- | :--- | :--- | :--- | :--- |
| **AM** | 280,743 | 14,068,292 | **50.1x** | +4,911% |
| **FM** | 276,969 | 13,371,301 | **48.3x** | +4,727% |

### Analog-to-Digital

| Algorithm | Initial (steps/s) | Vectorized (steps/s) | Speedup Factor | Improvement % |
| :--- | :--- | :--- | :--- | :--- |
| **Delta Mod** | 313,628 | 30,289,731 | **96.6x** | +9,557% |

## 4. Technical Analysis

### Top Performer: Pseudoternary & NRZ-L (~100x)
These algorithms represent simple state-transition logic or direct mapping. The JIT compiler can unroll these loops efficiently and SIMD-vectorize the operations, leading to throughputs exceeding **35 Million steps/s**.

### Complex Modulations: Manchester / FM / AM (~50x)
These algorithms involve more complex branching (Manchester transitions) or transcendental math operations (Sine/Cosine for AM/FM). While still achieving massive speedups (~50x), the compute density per sample is higher, slightly limiting the peak throughput compared to the simpler digital encoders.

### Conclusion
The vectorization effort has successfully transformed `simplex-sim` from a standard Python prototype into a high-performance simulation engine capable of processing tens of millions of samples per second, enabling real-time visualization of complex signaling scenarios.
