
import cv2
import numpy as np
import math

#read my image i want rotated
image = cv2.imread("pizza1.png")

#get the row and column values to create copy my original image but with a large border similar to the last assignment
numRows = image.shape[0]
numCols = image.shape[1]

#create the size of new image that will have a border
bigImgRows = int(image.shape[0] * 1.8)
bigImgCols = int(image.shape[1] * 1.8)
print(numRows, numCols)

#get large image center values to so we can place our OG image in the center of the new one
centerY = int((bigImgRows - numRows) / 2)
centerX = int((bigImgCols - numCols) / 2)

#create new image with larger rows and columns
emptyIm = np.zeros((bigImgRows, bigImgCols, 3), np.float32)

# iterate over all the pixels in the image and copy the colors
for i in range(1, numRows - 1):
    for j in range(1, numCols - 1):
        emptyIm[i + centerY][j + centerX][0] = image[i][j][0]
        emptyIm[i + centerY][j + centerX][1] = image[i][j][1]
        emptyIm[i + centerY][j + centerX][2] = image[i][j][2]
#=========================================================================================================================================================

#create a copy to use for subtraction in absolute color error calculation
emptyIm2 = emptyIm.copy()

#image we are copying pixels over to and rotating
rotated_image = np.zeros((bigImgRows, bigImgCols, 3), np.float32)

#large image center
new_cy = (bigImgRows // 2)
new_cx = (bigImgCols // 2)


#set theta as our step size
theta = 45

#pass theta to a fuction to convert to radians for rotation matrix
radians = math.radians(theta)

#calculate cycles/rotations
cycles = 180//theta

#create rotation matrix
rot_matrix = np.array([[math.cos(radians), -math.sin(radians)],
                       [math.sin(radians), math.cos(radians)]])


#initialize absolute color error & pixel round error
rgb_error_tot = 0
rnd_err_tot = 0
#=====================================================================================================================================

#create function more matrix multiplication
def matrixMultiplication2(rot_matrix, txty_coords):
    mtx = [0, 0]  #matrix to store values

    for i in range(2):  # For each row of mtx
        for j in range(2):  #single column
            mtx[i] += rot_matrix[i][j] * txty_coords[j]  #dot profuct of each value
    return mtx
#======================================================================================================================================

#k loop for our cycles: rotating 360 with step size 45 then cycles is 8
for k in range(cycles):
    for i in range(1, bigImgRows - 1):       #go through every pixel in the image
        for j in range(1, bigImgCols - 1):

            #tranlate and get new origin
            ty = i - new_cy
            tx = j - new_cx

            #place new origin in a matrix to be multiplied
            txtyCoords = np.array([[tx],
                                    [ty]])

            #call matrix multiplication function
            rotated = matrixMultiplication2(rot_matrix, txtyCoords)

            #get rotated coordinates from matrix multiplication
            rx1, ry1 = rotated[0][0], rotated[1][0]

            #Translate back(rounded)
            fy = int(ry1 + new_cy)
            fx = int(rx1 + new_cx)

            #Unrounded values for round error calculation
            fy1 = (ry1 + new_cy)
            fx1 = (rx1 + new_cx)

            #pixel rounding error formula
            rnd_err = math.sqrt(((fy1 - fy)**2) + ((fx1 - fx)**2))

            #keep running sum
            rnd_err_tot += rnd_err

            #copy color if in bounds
            if 0 <= fy < bigImgRows and 0 <= fx < bigImgCols:
                #rotated_image[fy, fx] = image[i, j]
                rotated_image[i][j] = emptyIm[fy][fx]

    #make a duplicate of the final state of the rotated image
    emptyIm = rotated_image.copy()
#============================================================================================================================================

# go through each pixel in both the original, untouched image and our
# rotated image calculate the difference in color channels using formula
for i in range(bigImgRows):
    for j in range(bigImgCols):
        b_val = ((emptyIm2[i][j][0] - rotated_image[i][j][0])**2)
        g_val = ((emptyIm2[i][j][1] - rotated_image[i][j][1])**2)
        r_val = ((emptyIm2[i][j][2] - rotated_image[i][j][2])**2)

        rgb_calc = math.sqrt(b_val + g_val + r_val)

        rgb_error_tot += rgb_calc   #running sum
#===============================================================================================================================================

#get pixel total
pixel_total = (bigImgRows * bigImgCols)

#calculate pixel pixel round error, absolute color error and the displacement error*
rnd_err_final = (rnd_err_tot) / (pixel_total * cycles)
displaceErr = rnd_err_final * cycles
print(rnd_err_final, "Round error")
print(displaceErr, "Displacement error")
rgb_error_final = (rgb_error_tot) / (pixel_total)
print(rgb_error_final, "RGB error")
#=========================================================================================================================================

#display image and save image
#cv2.imshow("Rotated", rotated_image/255.0)
cv2.imshow("Rotated", emptyIm/255.0)
cv2.imwrite("assign1_RotIMG.png", emptyIm)
cv2.waitKey(0)
cv2.destroyAllWindows()