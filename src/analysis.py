
import os
import numpy as np
from skimage.io import imread
from skimage import filters, measure
import pandas as pd
import matplotlib.pyplot as plt

from loguru import logger


logger.info('Import OK')

input_folder = open('experimental_data/root_path.txt', 'r').readlines()[0]
output_folder = 'results/initial_cleanup/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get a list of all the available image files for processing
file_list = [filename for filename in os.listdir(input_folder) if 'ch2_' in filename]

# Set a fluorescence threshold
thresh = 25

# Repeat for each image
cells = []
for file_path in reversed(file_list):   
    # Read in image
    img = imread(f'{input_folder}{file_path}')
    # logger.info(f'{file_path} read')

    # Calculate background as gaussian-smoothed
    background = filters.gaussian(img, sigma=100, preserve_range=True)
    # plt.imshow(background)
    # logger.info(f'{file_path} background calculated')

    # subtract background 
    corr_image = (img - background)
    # logger.info(f'{file_path} background corrected')
    
    # Apply threshold then label thresholded ROIs
    # thresh_img = np.where(corr_image > thresh, corr_image, 0)
    mask = measure.label(np.where(corr_image > thresh, 1, 0))
    # logger.info(f'{file_path} mask created')
    
    # Gather measurements from the ROI
    cell_measurements = pd.DataFrame(measure.regionprops_table(mask, intensity_image=corr_image, properties=('label', 'bbox', 'area', 'intensity_mean')))
    # logger.info(f'{file_path} mask measured')
    
    # Filter for minimum size
    cell_measurements = cell_measurements[cell_measurements['area'] > 25].copy()
    
    # Add file path to later assign treatment info
    cell_measurements['file_path'] = file_path
    
    cells.append(cell_measurements)
    logger.info(f'{file_path} processed with {len(cell_measurements)} cells')
    
    pd.concat(cells).to_csv(f'{output_folder}inprogress.csv')

summary = pd.concat(cells)

summary.to_csv(f'{output_folder}bgcorr_cell_measurements.csv')
