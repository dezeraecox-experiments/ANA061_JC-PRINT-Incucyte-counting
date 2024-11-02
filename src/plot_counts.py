
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from loguru import logger

logger.info('Import OK')

input_path = 'results/initial_cleanup/bgcorr_cell_measurements.csv'
output_folder = 'results/count/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read in summary info
summary = pd.read_csv(f'{input_path}')
summary.drop([col for col in summary.columns.tolist() if 'Unnamed: ' in col], axis=1, inplace=True)

summary[['channel', 'well', 'FOV', 'time']] = summary['file_path'].str.split('_', expand=True)
summary['time'] = summary['time'].str.split('.').str[0]
summary['days'] = summary['time'].str[:2].astype(int)
summary['hours'] = summary['time'].str[3:5].astype(int)
summary['mins'] = summary['time'].str[6:8].astype(int)
summary['incubation_length'] = summary['days'] * 24 + summary['hours'] + (summary['mins'] / 60)

summary['log_intensity'] = np.log(summary['intensity_mean'])


# Count number of green objects, normalise to max number of green objects per sample
counts = summary.groupby(['well', 'incubation_length']).count()['area'].reset_index()
max_counts = dict(counts.groupby('well').max().reset_index()[['well', 'area']].values)

for sample, df in counts.groupby('well'):

    sns.lineplot(
        data=df,
        x='incubation_length',
        y='area',
        hue='well',
        marker='o'
    )
    plt.show()


counts['max_val'] = counts['well'].map(max_counts)
counts['prop_total'] = counts['area'] / counts['max_val']

counts.to_csv(f'{output_folder}cells.csv')

# Visualise mean intensity over time

for sample, df in counts.groupby('well'):

    sns.lineplot(
        data=df,
        x='incubation_length',
        y='prop_total',
        hue='well',
        marker='o'

    )
    plt.show()

fig, ax = plt.subplots()
sns.lineplot(
    data=counts[counts['well'].isin(['A3', 'B3'])],
    x='incubation_length',
    y='prop_total',
    hue='well',
    palette={'A3': '#4F5669', 'B3': '#89023E'},
    marker='o'
)
plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.show()

fig, ax = plt.subplots()
sns.lineplot(
    data=counts[counts['well'].isin(['A3', 'B3'])],
    x='incubation_length',
    y='area',
    hue='well',
    palette={'A3': '#4F5669', 'B3': '#89023E'},
    marker='o'
)
plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.show()




# Fluorescence intensity t6 vs tend
intensity = summary[summary['incubation_length'].isin([12.0, summary['incubation_length'].max()])].copy()

mean_intensity = intensity[['well', 'FOV', 'intensity_mean', 'log_intensity', 'incubation_length']].groupby(['well', 'FOV', 'incubation_length']).mean()

mean_intensity.reset_index().to_csv(f'{output_folder}intensity.csv')


sns.boxplot(
    data=intensity,
    x='well',
    y='intensity_mean',
    hue='incubation_length',
    dodge=True,
    palette={12.0: '#F46036', 234.0: '#372248'},
    boxprops=dict(alpha=0.7),
    fliersize=0
    )
sns.stripplot(
    data=intensity,
    x='well',
    y='intensity_mean',
    hue='incubation_length',
    dodge=True,
    palette={12.0: '#F46036', 234.0: '#372248'}
)