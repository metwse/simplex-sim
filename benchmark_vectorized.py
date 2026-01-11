
import time
import numpy as np
from src.core.vectorized import VectorizedSimulation, VectorizedWire
from src.modules.vectorized_modules import (
    VectorizedAMModulator, VectorizedFMModulator, 
    VectorizedASKModulator, VectorizedFSKModulator
)

def create_raw_signal_generator(freq=1.0):
    omega = 2 * np.pi * freq
    def gene(times):
        return np.sin(omega * times)
    return gene

def create_digital_generator(bitstream, baud_rate):
    # vectorized generator
    bit_duration = 1.0 / baud_rate
    bits = np.array([float(b) for b in bitstream], dtype=np.float64)
    n_bits = len(bits)
    
    def gene(times):
        indices = (times * baud_rate).astype(np.int64) % n_bits
        return bits[indices]
    return gene

def benchmark_scenario(name, SetupFunc, steps=100000, batch_size=1000):
    start = time.perf_counter()
    sim = SetupFunc(batch_size=batch_size)
    
    # Warmup JIT
    sim.advance_batch()
    
    # Run
    t0 = time.perf_counter()
    n_batches = steps // batch_size
    for _ in range(n_batches):
        sim.advance_batch()
    
    dt = time.perf_counter() - t0
    total_steps = n_batches * batch_size
    print(f"{name:<30} {total_steps} steps in {dt:.4f}s => {total_steps/dt/1e6:.2f} Msteps/s")
    return total_steps/dt

def setup_am(batch_size=1000):
    w_in = VectorizedWire("Input")
    w_out = VectorizedWire("Output")
    gen = create_raw_signal_generator(1.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.01, batch_size=batch_size)
    mod = VectorizedAMModulator(w_in, w_out, carrier_freq=10.0)
    sim.add_component(mod)
    return sim

def setup_fm(batch_size=1000):
    w_in = VectorizedWire("Input")
    w_out = VectorizedWire("Output")
    gen = create_raw_signal_generator(1.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.01, batch_size=batch_size)
    mod = VectorizedFMModulator(w_in, w_out, carrier_freq=10.0)
    sim.add_component(mod)
    return sim

def setup_ask(batch_size=1000):
    w_in = VectorizedWire("Input")
    w_out = VectorizedWire("Output")
    gen = create_digital_generator("10110", baud_rate=5.0)
    sim = VectorizedSimulation(w_in, gen, dt=0.01, batch_size=batch_size)
    mod = VectorizedASKModulator(w_in, w_out, carrier_freq=10.0, baud_rate=5.0)
    sim.add_component(mod)
    return sim

def main():
    print("Benchmarking Vectorized + JIT Implementation...")
    print("="*60)
    
    benchmark_scenario("AM Vectorized", setup_am, steps=1_000_000)
    benchmark_scenario("FM Vectorized", setup_fm, steps=1_000_000)
    benchmark_scenario("ASK Vectorized", setup_ask, steps=1_000_000)

if __name__ == "__main__":
    main()
