#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('part2_data.csv')

grouped = df.groupby(['GraphID', 'Method'])['TimeSeconds'].agg(['mean', 'std']).reset_index()

plt.figure(figsize=(10, 6))
methods = grouped['Method'].unique()
for method in methods:
    sub_df = grouped[grouped['Method'] == method]
    plt.errorbar(sub_df['GraphID'], sub_df['mean'], yerr=sub_df['std'],
                 marker='o', linestyle='--', label=method)

plt.xlabel('Pseudo-Randomly Generated Graph')
plt.ylabel('Mean Run Time (s) | 5 Runs')
plt.title('Performance Comparison: BK vs ILP')
plt.legend()
plt.tight_layout()
# plt.show()
plt.savefig('part2_plot.png')