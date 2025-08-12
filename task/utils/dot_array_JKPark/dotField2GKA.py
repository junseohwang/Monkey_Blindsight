import numpy as np
import matplotlib.pyplot as plt


def dotField2GKA(radii, fieldRadius, showPlot=False):
    # Field coordinates
    xx, yy = np.meshgrid(np.arange(-fieldRadius, fieldRadius + 1), np.arange(-fieldRadius, fieldRadius + 1))

    # Distance to nearest object
    d = fieldRadius - np.sqrt(xx ** 2 + yy ** 2)

    #avoid (0,0) to prevent overlap with fixation
    new_d = np.sqrt((0 - xx) ** 2 + (0 - yy) ** 2) - radii[1]
    d = np.minimum(new_d, d)

    # Coordinates of each point
    x = np.zeros(len(radii))
    y = np.zeros(len(radii))

    for i in range(len(radii)):
        is_valid = d > radii[i]
        xo = xx[is_valid]
        if len(xo) == 0:
            print('Ran out of space before placing all dots')
            err = 1
            break
        else:
            err = 0
        yo = yy[is_valid]
        ind = np.random.randint(0, len(xo))
        x[i] = xo[ind]
        y[i] = yo[ind]

        new_d = np.sqrt((x[i] - xx) ** 2 + (y[i] - yy) ** 2) - radii[i]
        d = np.minimum(new_d, d)

    pts = np.column_stack((x, y))

    if showPlot:
        plt.clf()
        for i in range(len(radii)):
            plt.gca().add_patch(plt.Circle((pts[i, 0], pts[i, 1]), radii[i], fill=False))
        plt.gca().add_patch(plt.Circle((0, 0), fieldRadius, fill=False))
        plt.axis('equal')
        plt.show()

    return pts, err