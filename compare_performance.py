#!/usr/bin/env python3
import time
from src.simulations import SCENARIOS
from benchmark import benchmark_scenario, format_time

# Baseline measurements (Interim optimized state)
BASELINE = {
    "Digital to Digital Encoding": 50.8,
    "Digital to Digital: B8ZS Codec": 18.6,
    "Digital to Digital: Manchester Codec": 31.5,
    "Analog to Digital: PCM Codec": 37.8,
    "Digital to Analog: ASK Modem": 31.7,
    "Analog to Analog: AM Modem": 30.0
}

def main():
    print("Running Performance Comparison...")
    print("=" * 80)
    print(f"{'Scenario':<40} {'Baseline':<12} {'Current':<12} {'Speedup':<12}")
    print("-" * 80)

    total_base = 0.0
    total_curr = 0.0
    count = 0

    for name, base_ms in BASELINE.items():
        if name not in SCENARIOS:
            continue
        
        scenario = SCENARIOS[name]
        params = {k: v['default'] for k, v in scenario['parameters'].items()}
        
        # Run benchmark (10k steps, 5 runs for stability)
        # Warmup
        sim = scenario['setup'](**params)
        for _ in range(100): sim.advance()
            
        stats = benchmark_scenario(scenario, params, num_steps=10000, num_runs=5)
        current_ms = stats['mean'] * 1000.0  # Convert to ms
        
        speedup = (base_ms - current_ms) / base_ms * 100.0
        
        speedup_str = f"{speedup:+.1f}%"
        if speedup > 0:
            speedup_str = f"\033[92m{speedup_str}\033[0m" # Green
        else:
            speedup_str = f"\033[91m{speedup_str}\033[0m" # Red

        print(f"{name:<40} {base_ms:.1f}ms       {current_ms:.1f}ms       {speedup_str}")
        
        total_base += base_ms
        total_curr += current_ms
        count += 1

    print("=" * 80)
    avg_speedup = (total_base - total_curr) / total_base * 100.0
    print(f"Average Speedup over {count} scenarios: {avg_speedup:+.1f}%")

    print("\nOptimization Summary:")
    print("1. Memory: Added __slots__ to Wire and Component classes to reduce memory footprint.")
    print("2. Engine: Optimized propagation loop and set structure for faster updates.")
    print("3. Math: Replaced division with multiplication in Encoders (pre-calculated rates).")
    print("4. Access: Switched to direct attribute access (voltage) instead of method calls.")
    print("5. Strings: Optimized B8ZS/HDB3 generator pattern matching.")

if __name__ == "__main__":
    main()
