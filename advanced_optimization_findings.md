# Advanced Optimization Findings

## Numba JIT Compilation - REVERTED

### Attempted Optimization

Implemented Numba JIT (`@jit(nopython=True, cache=True)`) for trigonometric calculations in:
- Digital-to-Analog modulators (ASK, FSK, PSK)  
- Analog-to-Analog modulators (AM, FM, PM)

### Results

**Performance**: -5% regression (407k → 387k steps/s)  
**Decision**: REVERTED all Numba changes

### Why It Failed

1. **Function call overhead**: JIT-compiled functions added extra function call overhead
2. **Small hotspots**: Individual calculations are too small to benefit from JIT
3. **Already optimized**: Built-in `math.sin()` is highly optimized C code
4. **Warm-up cost**: JIT compilation on first call adds latency
5. **NumPy limitation**: Can't use NumPy arrays effectively with scalar operations

### Key Lesson

**JIT compilation helps when:**
- Large numerical computations in loops
- Complex algorithms with branches
- Array/matrix operations

**JIT doesn't help when:**
- Small, simple calculations (like single `sin()`/`cos()`)
- Already optimized C functions
- High function call frequency with minimal computation

---

## Vectorization Analysis

### Investigated Approach

Batch processing multiple simulation steps using NumPy arrays.

### Challenges Identified

1. **Event-driven architecture**: Simulation uses propagation loops that stabilize before advancing
2. **Variable propagation depth**: Number of iterations varies per step
3. **Object-oriented design**: Components use class methods, not pure functions
4. **Wire dependencies**: Cannot easily parallelize due to dependencies

### Conclusion

Current architecture not suitable for vectorization without major restructuring.

---

## Final Recommendation

**Stick with Phase 1-3 optimizations** (28.1% improvement):
1. ✅ Mathematical constants caching
2. ✅ Memory allocation with deque
3. ✅ Wire propagation algorithm

**Advanced optimizations (Numba/vectorization) not effective** for this codebase due to:
- Small computation kernels
- Event-driven architecture
- Already-optimized base functions

---

## Performance Summary

| Optimization | Result | Status |
|---|---|---|
| Math constants caching | +2.7% modulators | ✅ Kept |
| Deque memory | +0.7% overall | ✅ Kept |
| Wire propagation | +26.6% overall | ✅ Kept |
| **Numba JIT** | **-5.0% regression** | ❌ **Reverted** |
| **Vectorization** | Not implemented | ❌ **Not suitable** |
| **Total active** | **+28.1%** | ✅ **Final** |

