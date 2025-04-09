#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file (make sure that 'data.csv' is in your working directory)
df = pd.read_csv('part2_data.csv')

# Group the data by GraphID and Method to calculate the mean and standard deviation of run times
grouped = df.groupby(['GraphID', 'Method'])['TimeSeconds'].agg(['mean', 'std']).reset_index()

# Plot the results using error bars
plt.figure(figsize=(10, 6))
methods = grouped['Method'].unique()
for method in methods:
    sub_df = grouped[grouped['Method'] == method]
    plt.errorbar(sub_df['GraphID'], sub_df['mean'], yerr=sub_df['std'],
                 marker='o', linestyle='--', label=method)

plt.xlabel('GraphID')
plt.ylabel('Mean Run Time (Seconds)')
plt.title('Performance Comparison: BK vs ILP by GraphID')
plt.legend()
plt.tight_layout()
# plt.show()
plt.savefig('part2_plot.png')