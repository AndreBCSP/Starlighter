from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import csv
import os
import sys
from glob import glob

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import seaborn.objects as so
import skimage.io
import skimage.measure
from csbdeep.io import save_tiff_imagej_compatible
from csbdeep.utils import Path, normalize
from skimage.io import imread
from stardist import _draw_polygons, export_imagej_rois, random_label_cmap
from stardist.models import StarDist2D
from tifffile import imread

matplotlib.rcParams['image.interpolation'] = 'None'

np.random.seed(6)
lbl_cmap = random_label_cmap()


def segment(image_folder, model_path, imagej_roi=False):
    """This function allows the use of a trained model in Stardist2D to segment cells in a folder with microscopy images. This outputs 
    TIF images that are labeled."""

    root_dir = image_folder

    for subdir, dirs, files in os.walk(root_dir):



        # Get only the first image in each subdirectory which should be phase contrast images
        
        img_files = sorted([f for f in files if f.endswith('.tif')])[:1]
        if not img_files:
            continue
        img_file = img_files[0]




        # Load the image
        img_path = os.path.join(subdir, img_file)
        img = imread(img_path)
                




        # Process image

        n_channel = 1 if img.ndim == 2 else img.shape[-1]
        axis_norm = (0,1)   
        
        if n_channel > 1:
            print("Normalizing image channels %s." % ('jointly' if axis_norm is None or 2 in axis_norm else 'independently'))



        #Specify the model
        model_name = os.path.basename(model_path)
        model_path_dir = os.path.dirname(model_path)
        model = StarDist2D(None, name=model_name, basedir=model_path_dir)   
        



        # The model is then used to predict cells in the image

        img = normalize(img, 1,99.8, axis=axis_norm)
        labels, polygons = model.predict_instances(img)



        # Export labeled images to image directory

        
        basename = img_file[:img_file.find('_C00_ORG.tif')]
        label_path_img = os.path.join(root_dir, subdir, f'Z{basename}_labels.tif')
        
        print(f'Processing: {label_path_img}')
        
        save_tiff_imagej_compatible(label_path_img, labels, axes='YX')

        if imagej_roi:
            roi_path_img = os.path.join(root_dir, subdir, f'Z{basename}_ROI.zip')
            export_imagej_rois(roi_path_img, polygons['coord'])

    

def quantify(image_folder, photo_number):
    """This function takes a labeled image from Stardist and labels a fluorescence image, quantifies the signal from each cell and exports the data to CSV format"""
    root_dir = image_folder
    index = photo_number - 1
    
    for subdir, dirs, files in os.walk(root_dir):
        

        for file in files:

            if file.startswith("Z") and file.endswith("_labels.tif"):
                labeled_image = skimage.io.imread(os.path.join(subdir, file))
                
                # Get a list of files in the directory
                all_files = os.listdir(subdir)

                # Check if a file exists at the specified index
                if index < len(all_files) and all_files[index].endswith(".tif"):
                    print(f"File '{all_files[index]}' is being quantified")
                    unlabeled_image = skimage.io.imread(os.path.join(subdir, all_files[index]))
                else:
                    print(f"No file exists at index {index}")
                    continue

                labels_image = skimage.measure.label(labeled_image)

                props = skimage.measure.regionprops(labels_image, intensity_image=unlabeled_image)

                # Extract the mean intensity values for each label
                mean_intensities = [prop.mean_intensity for prop in props]

                basename = os.path.basename(file)
                new_filename = basename[1:].replace("_labels.tif", "")

                
                with open(os.path.join(root_dir, subdir, f"{new_filename}_Results.csv"), "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Label", "Mean Intensity"])
                    for i, mean_intensity in enumerate(mean_intensities):
                        writer.writerow([i+1, mean_intensity])






def analyse(image_folder):
    """This function takes CSV files, processes their data and plots them into violin plots and a table with statistical information"""

    # create an empty dictionary to store the dataframes
    dataframes = {}
    root_dir = image_folder

    # loop through the directory
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            # check if the file is a CSV file

            if file.endswith('_Results.csv'):
            # extract the name of the CSV file (without the extension or '_Results' suffix)
                csv_name = file[:-12]
                
            
                # read the CSV file into a dataframe
                df = pd.read_csv(os.path.join(subdir, file))
                # store the dataframe in the dictionary using the CSV name as the key
                if csv_name not in dataframes:
                    dataframes[csv_name] = df
                else:
                    # if a dataframe with the same CSV name already exists, concatenate them
                    dataframes[csv_name] = pd.concat([dataframes[csv_name], df], ignore_index=True)



    
            

    all_tables = []
    os.mkdir(f'{image_folder}/Results')
    for csv_name, df in dataframes.items():

        df['Log Value'] = np.log10(df['Mean Intensity'])
        df.to_csv(f'{image_folder}/Results/{csv_name}_Results.csv', index=False)

        df_stats = df['Log Value'].describe()
        df_count = df_stats.loc['count']
        df_mean = df_stats.loc['mean']
        df_median = df_stats.loc['50%']
        df_std = df_stats.loc['std']
        df_25 = df_stats.loc['25%']
        df_75 = df_stats.loc['75%']



        strain_list = [csv_name]
        cell_count_list = [df_count]
        mean_list = [df_mean]
        median_list = [df_median]
        std_list = [df_std]
        q25_list = [df_25]
        q75_list = [df_75]
    
        table_data = pd.DataFrame({

            'Strain': strain_list,
            'Cell count': cell_count_list,
            'Mean': mean_list,
            'Median': median_list,
            'Std': std_list,
            '25%': q25_list,
            '75%': q75_list
            })
    
        

        table_df = pd.DataFrame(table_data)
        table_df.set_index('Strain', inplace=True)

        # Add the table to the list of tables
        all_tables.append(table_df)

            # Concatenate all of the tables into a single DataFrame
    final_table = pd.concat(all_tables)
    final_table = final_table.applymap(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)

       

    final_table.to_csv(f'{image_folder}/Results/Stats.csv', index=True)
    
    print('You can find the results in the "Results" folder in the image folder')





def reset(image_folder):
    """This function deletes all files created by Starlighter in the input folder."""

    for subdir, dirs, files in os.walk(image_folder):
        for file in files:
            if file.endswith('_labels.tif'):
                os.remove(os.path.join(subdir, file))
                
                
            elif file.endswith('_Results.csv'):
                    os.remove(os.path.join(subdir, file))
                    
            else:
                continue
    print('All files created by Starlighter were deleted')
