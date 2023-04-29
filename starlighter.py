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


def fdistari(image_folder, model_name, model_path):
    """This function allows the use of a trained model in Stardist2D to segment cells in a folder with microscopy images. This outputs 
    TIF images that are labeled."""

    root_dir = image_folder

    for subdir, dirs, files in os.walk(root_dir):



        # Get only the first image in each subdirectory
        
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




        # Show all test images
        if False:
            fig, ax = plt.subplots(7,8, figsize=(16,16))
            for i,(a,x) in enumerate(zip(ax.flat, X)):
                a.imshow(x if x.ndim==2 else x[...,0], cmap='gray')
                a.set_title(i)
                [a.axis('off') for a in ax.flat]
                plt.tight_layout()
            None;



            
        demo_model = False

        if demo_model:
            print (
                "NOTE: This is loading a previously trained demo model!\n"
                "      Please set the variable 'demo_model = False' to load your own trained model.",
                file=sys.stderr, flush=True
            )
            model = StarDist2D.from_pretrained('2D_demo')
        else:
            model = StarDist2D(None, name=model_name, basedir=model_path)   
        None;



        # The model is then used to predict cells in the image

        img = normalize(img, 1,99.8, axis=axis_norm)
        labels, polygons = model.predict_instances(img)

        # Export ROIs to image directory

        
        basename = img_file[:img_file.find('_C00_ORG.tif')]
        roi_path_img = os.path.join(root_dir, subdir, f'Z{basename}_labels.tif')
        
        print(f'Processing: {roi_path_img}')
        
        save_tiff_imagej_compatible(roi_path_img, labels, axes='YX')





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






def stradivari(input_folder):
    """This function takes CSV files, processes their data and plots them into violin plots and a table with statistical information"""

    # create an empty dictionary to store the dataframes
    dataframes = {}
    root_dir = input_folder

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




            # Loop through the dictionary and print the concatenated dataframes
    dfs = {}

    for csv_name, df in dataframes.items():
        color_count = 0

        green_keyword = ['GFP']
        yellow_keyword = ['Cit', 'YFP']
        red_keyword = ['mCherry', 'mScarlet']
        blue_keyword = ['CFP']
    
        # Flag variables
        green_found = False
        yellow_found = False
        red_found = False
        blue_found = False

        

        for df_name, df in dataframes.items():

            if any(keyword in df_name for keyword in green_keyword):
                if not green_found:
                    color_count += 1
                    green_found = True
                
            if any(keyword in df_name for keyword in yellow_keyword):
                if not yellow_found:
                    color_count += 1
                    yellow_found = True

            if any(keyword in df_name for keyword in red_keyword):
                if not red_found:
                    color_count += 1
                    red_found = True

            if any(keyword in df_name for keyword in blue_keyword):
                if not blue_found:
                    color_count += 1
                    blue_found = True

    #print(color_count)



    
    greendfs = {}
    yellowdfs = {}
    bluedfs = {}
    reddfs = {}


    for csv_name, df in dataframes.items():
        color_found = False
        no_color = True
    
        for keyword in green_keyword:
            if keyword in csv_name:
                greendfs[csv_name] = df
                color_found = True
                no_color = False
                break
                
        if not color_found:
            for keyword in yellow_keyword:
                if keyword in csv_name:
                    yellowdfs[csv_name] = df
                    color_found = True
                    no_color = False
                    break
                    
        if not color_found:
            for keyword in red_keyword:
                if keyword in csv_name:
                    reddfs[csv_name] = df
                    color_found = True
                    no_color = False
                    break
                    
        if not color_found:
            for keyword in blue_keyword:
                if keyword in csv_name:
                    bluedfs[csv_name] = df
                    color_found = True
                    no_color = False
                    break
                
        if no_color:
            greendfs[csv_name] = df
            yellowdfs[csv_name] = df
            reddfs[csv_name] = df
            bluedfs[csv_name] = df
    
    
    # For the green channel
    df_concat = pd.concat(greendfs.values(), keys=greendfs.keys())
    df_concat = df_concat.reset_index(level=0)
    df_concat.columns = ['key', 'Label', 'Mean Intensity']
    df_melted = pd.melt(df_concat, id_vars=['key', 'Label'], var_name='Variable', value_name='Value')

    df_melted['Log Value'] = np.log10(df_melted['Value'])

    # For the yellow channel
    df_concat2 = pd.concat(yellowdfs.values(), keys=yellowdfs.keys())
    df_concat2 = df_concat2.reset_index(level=0)
    df_concat2.columns = ['key', 'Label', 'Mean Intensity']
    df_melted2 = pd.melt(df_concat2, id_vars=['key', 'Label'], var_name='Variable', value_name='Value')

    df_melted2['Log Value'] = np.log10(df_melted2['Value'])


    fig, axs = plt.subplots(ncols=color_count, figsize=(8*color_count,8))
    fig.subplots_adjust(bottom=0.25)
    
    sns.violinplot(ax= axs[0], x='key', y='Log Value', data=df_melted, color=('#32E00B'))




    sns.violinplot(ax= axs[1], x='key', y='Log Value', data=df_melted2, color=('#FFFF00'))


    axs[0].set_xlabel('Strains')
    axs[1].set_xlabel('Strains')
    axs[0].set_ylabel('Log Average Fluorescence')
    axs[1].set_ylabel('')
    

    # Set the diagonal x-tick labels for each subplot
    for ax in axs:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.show()
    

    all_tables = []

    for csv_name, df in dataframes.items():
        df = df.drop('Label', axis=1)
    
        df_stats = df.describe()
        df_count = df_stats.loc['count']
        df_mean = np.log10(df_stats.loc['mean'])
        df_median = np.log(df_stats.loc['50%'])
        df_std = np.log10(df_stats.loc['std'])
    
        table_data = pd.DataFrame({
            'Strain': csv_name,
            'Cell count': df_count,
            'Mean': df_mean,
            'Median': df_median,
            'Std': df_std
            })
    
        #print(table_data)


        # Add the table to the list of tables
        all_tables.append(table_data)

            # Concatenate all of the tables into a single DataFrame
        final_table = pd.concat(all_tables)
        final_table = final_table.applymap(lambda x: f'{x:.2f}' if isinstance(x, (int, float)) else x)

        # Create a plot of the table
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=final_table.values, colLabels=final_table.columns, loc='center')

    final_table.to_csv('Final_Results.csv', index=False)
    plt.show()







def reset(input_folder):
    """This function deletes all files created by Starlighter in the input folder."""

    for subdir, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('_labels.tif'):
                os.remove(os.path.join(subdir, file))
                
                
            elif file.endswith('_Results.csv'):
                    os.remove(os.path.join(subdir, file))
                    
            else:
                continue