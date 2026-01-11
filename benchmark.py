#!/usr/bin/env python3
from src.simulations import SCENARIOS
from src.simulations.types import Scenario

import time
import statistics
import argparse
import sys


def benchmark_scenario(scenario: Scenario, params: dict,
                       num_steps: int, num_runs: int = 3):
    """Runs scenario multiple times and returns timing statistics."""

    times = []

    for _ in range(num_runs):
        sim = scenario['setup'](**params)

        start = time.perf_counter()
        if hasattr(sim, 'advance_batch'):
            batch_size = getattr(sim, 'batch_size', 1000)
            num_batches = (num_steps + batch_size - 1) // batch_size
            for _ in range(num_batches):
                sim.advance_batch()
        else:
            for _ in range(num_steps):
                sim.advance()
        elapsed = time.perf_counter() - start

        times.append(elapsed)

    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0.0,
        'min': min(times),
        'max': max(times),
        'runs': times
    }


def format_time(seconds: float) -> str:
    """Format time in appropriate units."""
    if seconds < 0.001:
        return f"{seconds * 1e6:.1f}µs"
    elif seconds < 1.0:
        return f"{seconds * 1e3:.1f}ms"
    else:
        return f"{seconds:.3f}s"


def main():
    parser = argparse.ArgumentParser(
        description='Benchmark simplex-sim scenarios'
    )
    parser.add_argument(
        '--steps', type=int, default=30000,
        help='Number of simulation steps per run (default: 10000)'
    )
    parser.add_argument(
        '--runs', type=int, default=3,
        help='Number of runs per scenario (default: 3)'
    )
    parser.add_argument(
        '--warmup', type=int, default=1,
        help='Number of warmup runs (default: 1)'
    )
    parser.add_argument(
        '--filter', type=str, default=None,
        help='Filter scenarios by name substring'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show detailed timing for each run'
    )

    args = parser.parse_args()

    scenarios = SCENARIOS
    if args.filter:
        scenarios = {k: v for k, v in SCENARIOS.items()
                     if args.filter.lower() in k.lower()}

    if not scenarios:
        print(f"No scenarios match filter: {args.filter}")
        sys.exit(1)

    print(f"Benchmarking {len(scenarios)} scenarios")
    print(f"Steps per run: {args.steps}")
    print(f"Runs per scenario: {args.runs}")
    print(f"Warmup runs: {args.warmup}\n")

    print(f"{'Scenario':<50} {'Mean':<12} {'Median':<12} "
          f"{'StdDev':<12} {'Steps/s':<12}")
    print("=" * 98)

    results = []

    for (name, scenario) in scenarios.items():
        params = {k: v['default']
                  for k, v in scenario['parameters'].items()}

        if args.warmup > 0:
            for _ in range(args.warmup):
                sim = scenario['setup'](**params)
            if hasattr(sim, 'advance_batch'):
                sim.advance_batch()
            else:
                for _ in range(min(100, args.steps)):
                    sim.advance()

        stats = benchmark_scenario(scenario, params,
                                   args.steps, args.runs)

        steps_per_sec = args.steps / stats['mean']
        results.append((name, stats, steps_per_sec))

        print(f"{name:<50} "
              f"{format_time(stats['mean']):<12} "
              f"{format_time(stats['median']):<12} "
              f"{format_time(stats['stdev']):<10} "
              f"{steps_per_sec:>10.1f}")

        if args.verbose and len(stats['runs']) > 1:
            for i, t in enumerate(stats['runs'], 1):
                print(f"  Run {i}: {format_time(t)}")

    print("=" * 98)

    total_time = sum(r[1]['mean'] for r in results)
    avg_time = total_time / len(results)
    avg_steps_per_sec = statistics.mean([r[2] for r in results])

    print(f"\nTotal time: {format_time(total_time)}")
    print(f"Average time per scenario: {format_time(avg_time)}")
    print(f"Average throughput: {avg_steps_per_sec:.1f} steps/s")

    fastest = min(results, key=lambda x: x[1]['mean'])
    slowest = max(results, key=lambda x: x[1]['mean'])

    print(f"\nFastest: {fastest[0]}")
    print(f"  {format_time(fastest[1]['mean'])} "
          f"({fastest[2]:.1f} steps/s)")
    print(f"\nSlowest: {slowest[0]}")
    print(f"  {format_time(slowest[1]['mean'])} "
          f"({slowest[2]:.1f} steps/s)")


if __name__ == '__main__':
    main()
