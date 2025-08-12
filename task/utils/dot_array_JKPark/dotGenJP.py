import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def dotGenJP(**kwargs):
    # Default values
    nlim = [2,32] #[8, 32]
    rdlim = [4,16] #[6, 12]
    rflim = [160,640] #[120, 240]
    level = 31 #5
    showplot = False

    # Update values with provided keyword arguments
    for key, value in kwargs.items():
        if key == 'nlim':
            nlim = value
        elif key == 'rdlim':
            rdlim = value
        elif key == 'rflim':
            rflim = value
        elif key == 'level':
            level = value
        elif key == 'showplot':
            showplot = value
        else:
            raise ValueError(f'Invalid property name: {key}')

    # Function for removing rounding error
    def fRound(x, p):
        return np.round(x * p) / p

    # Number (theoretical and real values)
    N = 2 ** np.linspace(np.log2(nlim[0]), np.log2(nlim[1]), level)
    N_r = fRound(N, 1)

    # IA
    IA = 2 ** np.linspace(np.log2(np.pi * rdlim[0]**2), np.log2(np.pi * rdlim[1]**2), level)
    rd = np.sqrt(IA / np.pi)
    rd_r = fRound(rd, 2)

    # FA
    FA = 2 ** np.linspace(np.log2(np.pi * rflim[0]**2), np.log2(np.pi * rflim[1]**2), level)
    rf = np.sqrt(FA / np.pi)
    rf_r = fRound(rf, 2)

    # Empty matrix to store magnitude values
    magval = np.empty((level**3, 5))
    magval[:] = np.nan  # Initialize with NaN
    magval_r = np.empty((level**3, 3))
    magval_r[:] = np.nan  # Initialize with NaN
    counter = 0

    for iIA in range(level):
        for iFA in range(level):
            for iN in range(level):
                # Theoretical values
                magval[counter, 0] = N[iN]
                magval[counter, 1] = IA[iIA]
                magval[counter, 2] = FA[iFA]
                magval[counter, 3] = IA[iIA] * N[iN]  # TA
                magval[counter, 4] = FA[iFA] / N[iN]  # Spar

                # Real values
                magval_r[counter, 0] = N_r[iN]
                magval_r[counter, 1] = rd_r[iIA]
                magval_r[counter, 2] = rf_r[iFA]

                counter += 1

    magvalLog = np.log2(magval)

    logN = magvalLog[:, 0]
    logSz = magvalLog[:, 1] + np.log2(magval[:, 3])
    logSp = magvalLog[:, 2] + np.log2(magval[:, 4])

    # Round up to 10e-3 place
    logN = fRound(logN, 100)
    logSz = fRound(logSz, 100)
    logSp = fRound(logSp, 100)

    # Min/max Sz
    midTA = IA[0] * N[-1]
    minlogSz = np.log2(midTA) + np.log2(IA[0])
    maxlogSz = np.log2(midTA) + np.log2(IA[-1])

    # Min/max Sp
    midSpar = FA[0] / N[0]
    minlogSp = np.log2(midSpar) + np.log2(FA[0])
    maxlogSp = np.log2(midSpar) + np.log2(FA[-1])

    # Remove rounding error
    minlogSz = fRound(minlogSz, 100)
    maxlogSz = fRound(maxlogSz, 100)
    minlogSp = fRound(minlogSp, 100)
    maxlogSp = fRound(maxlogSp, 100)

    # Index within min and max of logSZ and logSp
    idx = (logSz >= minlogSz) & (logSz <= maxlogSz) & (logSp >= minlogSp) & (logSp <= maxlogSp)

    logN = logN[idx]
    logSz = logSz[idx]
    logSp = logSp[idx]

    magval = magval[idx]
    magval_r = magval_r[idx]

    logN_r = np.log2(magval_r[:, 0])
    logSz_r = np.log2(np.pi * magval_r[:, 1]**2) + np.log2(np.pi * magval_r[:, 1]**2 * magval_r[:, 0])
    logSp_r = np.log2(np.pi * magval_r[:, 2]**2) + np.log2(np.pi * magval_r[:, 2]**2 / magval_r[:, 0])

    if showplot:
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        axs[0].scatter(logSz, logSp, c=logN, cmap='viridis')
        axs[0].set_xlabel('logSz')
        axs[0].set_ylabel('logSp')
        axs[0].set_zlabel('logN')
        axs[0].set_title('Theoretical values')
        axs[0].axis('equal')

        msqerr = np.mean(np.sqrt(np.sum((np.vstack([logN, logSz, logSp]).T - np.vstack([logN_r, logSz_r, logSp_r]).T) ** 2, axis=1)))
        axs[1].scatter(logSz_r, logSp_r, c=logN_r, cmap='viridis')
        axs[1].set_xlabel('logSz')
        axs[1].set_ylabel('logSp')
        axs[1].set_zlabel('logN')
        axs[1].set_title(f'Real values; msqerr = {msqerr:.4f}')
        axs[1].axis('equal')

        plt.show()
    else:
        fig = None

    # Output struct
    stimDim = {
        'desc': f'Generated from {__name__}.py at {str(datetime.now())}.\n'
                'logN/Sz/Sp and magval are theoretical values.\n'
                'The columns for magval represent: N, IA, FA, TA, Spar.\n'
                'logN_r/Sz_r/Sp_r and magval_r are real values.\n'
                'The columns for magval_r represent: N, r_d, r_f.\n',
        'idx': np.arange(1, len(logN) + 1),
        'logN': logN.tolist(),
        'logSz': logSz.tolist(),
        'logSp': logSp.tolist(),
        'magval': magval.tolist(),
        'logN_r': logN_r.tolist(),
        'logSz_r': logSz_r.tolist(),
        'logSp_r': logSp_r.tolist(),
        'magval_r': magval_r.tolist(),
    }

    return stimDim, fig