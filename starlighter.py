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


def fdistari(image_folder, model_path, imagej_roi=False):
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

    

def nonapari(image_folder, photo_number):
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
                    print(f"File '{all_files[index]}' exists at index {index}")
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
                            #print(csv_name)   This is working fine so far
            
                            # read the CSV file into a dataframe
                            df = pd.read_csv(os.path.join(subdir, file))

                            # store the dataframe in the dictionary using the CSV name as the key
                            if csv_name not in dataframes:
                                dataframes[csv_name] = df
                            else:
                                # if a dataframe with the same CSV name already exists, concatenate them
                                dataframes[csv_name] = pd.concat([dataframes[csv_name], df], ignore_index=True)

                            for index, df in enumerate(dataframes):
                                filename = f'{csv_name}_Results.csv'

                                df.to_csv(filename, index=False)


# df_concat_green = pd.concat(greendfs.values(), keys=greendfs.keys())
#         df_concat_green = df_concat_green.reset_index(level=0)
#         df_concat_green.columns = ['key', 'Label', 'Mean Intensity']
#         df_melted_green = pd.melt(df_concat_green, id_vars=['key', 'Label'], var_name='Variable', value_name='Value')

#         df_melted_green['Log Value'] = np.log10(df_melted_green['Value'])

# all_tables = []

#     for csv_name, df in dataframes.items():
#         df = df.drop('Label', axis=1)
    
#         df_stats = df.describe()
#         df_count = df_stats.loc['count']
#         df_mean = np.log10(df_stats.loc['mean'])
#         df_median = np.log10(df_stats.loc['50%'])
#         df_std = np.log10(df_stats.loc['std'])
    
#         table_data = pd.DataFrame({
#             'Strain': csv_name,
#             'Cell count': df_count,
#             'Mean': df_mean,
#             'Median': df_median,
#             'Std': df_std
#             })
    
#         #print(table_data)


#         # Add the table to the list of tables
#         all_tables.append(table_data)

#             # Concatenate all of the tables into a single DataFrame
#         final_table = pd.concat(all_tables)
#         final_table = final_table.applymap(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)


def reset(image_folder):
    """This function deletes all files created by eFQu in the input folder."""

    for subdir, dirs, files in os.walk(image_folder):
        for file in files:
            if file.endswith('_labels.tif'):
                os.remove(os.path.join(subdir, file))
                
                
            elif file.endswith('_Results.csv'):
                    os.remove(os.path.join(subdir, file))
                    
            else:
                continue
    print('All file created by Starlighter were deleted')
