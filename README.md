Image Rotation Algorithm

This repository contains a custom image rotation algorithm implementation developed for CSC340 coursework.

Overview
This Python program implements an image rotation algorithm from scratch that:

Reads an input image and creates a bordered copy to accommodate rotation
Applies matrix-based rotation transformations using a custom matrix multiplication function
Performs multiple rotations based on a specified angle (theta)
Calculates and reports three error metrics:

Pixel rounding error
Displacement error
Absolute color error (RGB)


Visualizes and saves the rotated image

Key Features

Custom Matrix Transformation: Implements rotation using fundamental matrix operations
Error Analysis: Detailed calculation of the differences between original and rotated images
Configurable Rotations: Support for different rotation angles (theta) and multiple rotation cycles
Visual Output: Displays and saves the final rotated image

Requirements

Python 3.x
NumPy
OpenCV (cv2)

Usage

Enter an image named in the same directory as the script(be sure to enter .jpg, jpeg, .png, .pdf at the end of image name)
Run the program:
Copypython ImageRotationAssignment1.py

The program will display the rotated image and save it as "assign1_RotIMG.png"
Console output will show the calculated error metrics

Implementation Details
The rotation algorithm follows these steps:

Create a larger canvas with border to prevent cropping during rotation
Calculate center point for rotation
For each rotation cycle:

Apply a rotation matrix to transform coordinates
Handle pixel value mapping with appropriate transformations
Update the image for the next rotation


Calculate error metrics between the original and final images:

Pixel rounding error: Difference between exact and integer pixel positions
Displacement error: Cumulative effect of multiple rotations
RGB error: Color difference between original and rotated images



Author
Dimitri Montgomery
