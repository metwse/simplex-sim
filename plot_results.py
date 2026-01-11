import matplotlib.pyplot as plt
import numpy as np

# Data from baseline and final benchmarks
scenarios = [
    'D2D Encoding',
    'HDB3',
    'Manchester',
    'NRZL',
    'PCM',
    'ASK',
    'FSK',
    'PSK',
    'AM',
    'FM',
    'PM'
]

baseline = [179966, 487985, 322566, 362552, 206687, 
            293702, 304369, 281819, 307169, 292587, 251495]
optimized = [229224, 693311, 369490, 436873, 342026,
             383354, 368100, 356138, 425894, 385210, 329648]

# Calculate improvements
improvements = [(opt - base) / base * 100 for base, opt in zip(baseline, optimized)]

# Create figure with subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Before/After Comparison
x = np.arange(len(scenarios))
width = 0.35

bars1 = ax1.bar(x - width/2, np.array(baseline)/1000, width, label='Baseline', color='#e74c3c', alpha=0.8)
bars2 = ax1.bar(x + width/2, np.array(optimized)/1000, width, label='Optimized', color='#27ae60', alpha=0.8)

ax1.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax1.set_ylabel('Throughput (k steps/s)', fontsize=12, fontweight='bold')
ax1.set_title('Performance Comparison: Baseline vs Optimized', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(scenarios, rotation=45, ha='right')
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}k',
                ha='center', va='bottom', fontsize=8)

# Plot 2: Improvement Percentage
colors = ['#27ae60' if imp > 30 else '#f39c12' if imp > 20 else '#3498db' for imp in improvements]
bars3 = ax2.barh(scenarios, improvements, color=colors, alpha=0.8)

ax2.set_xlabel('Performance Improvement (%)', fontsize=12, fontweight='bold')
ax2.set_title('Performance Improvement by Scenario', fontsize=14, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, imp) in enumerate(zip(bars3, improvements)):
    ax2.text(imp + 1, bar.get_y() + bar.get_height()/2,
            f'+{imp:.1f}%',
            ha='left', va='center', fontsize=9, fontweight='bold')

# Add average line
avg_improvement = np.mean(improvements)
ax2.axvline(avg_improvement, color='red', linestyle='--', linewidth=2, label=f'Average: +{avg_improvement:.1f}%')
ax2.legend(fontsize=11)

plt.tight_layout()
plt.savefig('optimization_comparison.png', dpi=150, bbox_inches='tight')
print("Performance comparison chart saved to: optimization_comparison.png")
print(f"\nOverall Statistics:")
print(f"  Average baseline:  {np.mean(baseline)/1000:.1f}k steps/s")
print(f"  Average optimized: {np.mean(optimized)/1000:.1f}k steps/s")
print(f"  Average improvement: +{avg_improvement:.1f}%")
print(f"  Best improvement: +{max(improvements):.1f}% ({scenarios[improvements.index(max(improvements))]})")
