import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt

from dotGenJP import dotGenJP
from dotField2GKA import dotField2GKA

# Create stimulus parameters for a systematic construction of dot arrays
stimDim = dotGenJP()

# Magnitude values containing information about N, r_d, and r_f
magval_r = stimDim[0]['magval_r']

# Buffer allows extra space between the dots
buffer = 1.5

nAttempts = 100000 #100 # 25

N = 2000 #500  # width/height of the image in pixels
AxisAdj = np.ceil(N / 2).astype(int)

nDots = 1  # number of unique dot arrays generated for each stimulus parameter point

# List that will contain all the dot-array parameters
dotArrays = {
    'logN':[],
    'logSz':[],
    'logSp':[],
    'num': [],
    'r_d': [],
    'r_f': [],
    'coord': [],
    'img': [],
             }

for i in range(len(magval_r)):

    for j in range(nDots):

        # Dot coordinates
        for ierr in range(nAttempts):
            radii = magval_r[i][1] * buffer * np.ones(int(magval_r[i][0]))
            fieldRadius = magval_r[i][2]

            dts, err = dotField2GKA(radii,fieldRadius)
            if err == 0:
                break
            if ierr == nAttempts-1:
                print('dotField2GKA failed.')
        dts = dts + AxisAdj

        # Create a background image that's "mulfac" times larger (for anti-aliasing)
        mulfac = 8

        M = np.zeros((mulfac * N, mulfac * N))
        dts_aa = (dts * mulfac).astype(int)

        M[dts_aa[:, 0], dts_aa[:, 1]] = 1
        J = (distance_transform_edt(np.logical_not(M)) <= magval_r[i][1] * mulfac).astype(float)

        # Reduce the image by "mulfac" times and trim <0 and >1 values
        J = np.clip(J, 0, 1)
        J = np.array(np.uint8(255 * J))


        # dotArrays['logN'].append(stimDim[0]['logN'][i])
        # dotArrays['logSz'].append(stimDim[0]['logSz'][i])
        # dotArrays['logSp'].append(stimDim[0]['logSp'][i])
        # dotArrays['num'].append(magval_r[i][0])
        # dotArrays['r_d'].append(magval_r[i][1])
        # dotArrays['r_f'].append(magval_r[i][2])
        # dotArrays['coord'].append(dts - AxisAdj)  # original coordinates
        # dotArrays['img'].append(J)

        # plt.figure()
        # plt.imshow(J, cmap='gray')
        # # plt.axis('square')
        # plt.show()