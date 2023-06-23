# Starlighter

This program was designed in order to process a great amount of fluorescence microscopy data. This program is comprised of three separate modules:

## Segmentation: 
Using code from Stardist2D, processes an image folder with microscopy images, predicts where the cells are in the images using a custom-trained model and
exports the information to a labeled tif image. 

## Quantification:
Takes a labeled tif image and an unlabeled tif image and labels the unlabeled image. Then, it calculates the mean pixel intensities for each cell and exports
this data into a CSV file. 



## Inputs and Outputs:
Starlighter requires the following inputs:

-A folder with sub-folders containing the images

<img src="https://user-images.githubusercontent.com/131555736/234348105-1e6548ba-831c-4b3c-ad25-1e4bea6af6d0.jpg" width="250">



-The path to the folder containing the model folder

-The number of the position of the image you want to quantify in the folders



Here is an example of the output of the entire program:

<img src="https://user-images.githubusercontent.com/131555736/234344748-497467fb-6e80-4f02-989e-685f92db7950.png" width="700">

<img src="https://user-images.githubusercontent.com/131555736/234346766-ddad9edd-f849-407f-8b31-24d8eea272e6.png" witdh="1">
