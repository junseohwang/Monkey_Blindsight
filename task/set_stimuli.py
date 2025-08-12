"""
    sample stimulus
        - controlling for 1) total area/individual area, 2) density/convex hull as in Park, Cognition (2022)
        - input:
        - output: dot radius (rd), field radius (rf), x, y of individual dots
        - based on task.py in MazePong

"""
####  Determine whether on laptop or on rig and update sys.path accordingly

_PYTHON_SITE_PACKAGES = [] # getvar('python_site_packages')
_PWD = [] # getvar('pwd')

import sys

if '' not in sys.path:
    sys.path.insert(0, '')
if _PYTHON_SITE_PACKAGES not in sys.path:
    sys.path.append(_PYTHON_SITE_PACKAGES)
if _PWD not in sys.path:
    sys.path.append(_PWD)

####  Imports

from datetime import datetime
import importlib
import numpy as np
import os
import threading

# from utils import logger_env_wrapper #TBD
# from moog import environment #TBD
# from moog import observers #TBD
# from maze_pong_configs import config as config_lib #TBD

class SetStimuli:
    """
    usage in MazePong/moog.mwel like this
    run_python_string (
        't = TaskManager(level="random.exp_2_prey.exp_2_prey", fixation_phase=True, translucent_occluder=True)')

        % For a balanced design, the minimum and the maximum values of nlim, rdlim,
        %   and rflim should all the equivalent. To achieve this, because area as
        %   in individual area (IA) and field area (FA) is proportionate to the
        %   square of radius, if the range of n differs in 4 folds, the range of
        %   rd (radius of each dot) and rf (radius of the circular field in which
        %   the dots are drawn) should differ in 2 folds.
    """

    def __init__(self,#level,
                 **config_kwargs):
        """Constructor."""
        self.lock = threading.Lock()
        # self._discrete_controller = getvar('discrete_controller')

        self._end_task = False

        # Default values
        self.nlim = [getvar('number_min'), getvar('number_max')] # [1 2 3 6 12]  #   np.round(2 ** np.linspace(np.log2(nlim[0]), np.log2(nlim[1]), level))
        # [1, 8]:12358
        # [8, 32]:8 11 16 23 32
        self.rdlim = [14,20] #getvar('rdlim') # [9, 36] # [6, 24] # [6, 12]
        self.rflim = [120, 240] #getvar('rflim') # [80, 320] # [120, 480] # [120, 240]
        self.level = np.max([5,getvar('n_number_level')])

       #var rdlim = [12,48]
       #var rflim = [160,640]

        # to check sampled number are what we intend
        self.number_set = np.round(2 ** np.linspace(np.log2(self.nlim[0]), np.log2(self.nlim[1]), self.level))
        setvar('number_set_sampled',self.number_set)

        # Buffer allows extra space between the dots
        self.buffer = 1.5 #1.8

        self.scaling_factor = 40 # 640/40=16dva # 20 # 300pixels -> 15dva; 15 # 240 pixels -> 16 dva

        # Create stimulus parameters for a systematic construction of dot arrays
        self.stimDim = self.dotGenJP()

        # Magnitude values containing information about N, r_d, and r_f
        self.magval_r = self.stimDim[0]['magval_r']

    def reset(self):
        """Reset environment.

        This should be called at the beginning of every trial.
        """

        self.number = getvar('number') # 8

        self.nAttempts = 100 # 25

        # List that will contain all the dot-array parameters
        self.dotArrays = {
            'logN': [],
            'logSz': [],
            'logSp': [],
            'num': [],
            'r_d': [],
            'r_f': [],
            'dotX': [],
            'dotY': [],
            'dot_sz': [],
        }

        for i in range(len(self.magval_r)):

            if int(self.magval_r[i][0]) == self.number:

                # Dot coordinates
                for ierr in range(self.nAttempts):
                    radii = self.magval_r[i][1] * self.buffer * np.ones(int(self.magval_r[i][0]))
                    fieldRadius = self.magval_r[i][2]

                    dts, err = self.dotField2GKA(radii, fieldRadius)
                    if err == 0:
                        break
                    if ierr == self.nAttempts-1:
                        print('dotField2GKA failed.')
                        error('dotField2GKA failed.')
                # dts = dts + AxisAdj

                # scaling for visual angle degree
                _x_scaled = dts[:,0] / self.scaling_factor
                _y_scaled = dts[:,1] / self.scaling_factor

                # positions
                setvar('dotX0',_x_scaled.tolist())
                setvar('dotX', _x_scaled.tolist())
                setvar('dotY0', _y_scaled.tolist())
                setvar('dotY', _y_scaled.tolist())
                #
                # # object size
                setvar('dot_sz', self.magval_r[i][1]/self.scaling_factor)

                self.dotArrays['logN'].append(self.stimDim[0]['logN'][i])
                self.dotArrays['logSz'].append(self.stimDim[0]['logSz'][i])
                self.dotArrays['logSp'].append(self.stimDim[0]['logSp'][i])
                self.dotArrays['num'].append(self.magval_r[i][0])
                self.dotArrays['r_d'].append(self.magval_r[i][1])
                self.dotArrays['r_f'].append(self.magval_r[i][2])
                self.dotArrays['dotX'].append(_x_scaled) # append(dts - AxisAdj)  # original coordinates
                self.dotArrays['dotY'].append(_y_scaled)  # append(dts - AxisAdj)  # original coordinates
                self.dotArrays['dot_sz'].append(self.magval_r[i][1]/self.scaling_factor)  # append(dts - AxisAdj)  # original coordinates

                break

        self.complete = False

    def dotField2GKA(self, radii, fieldRadius, showPlot=False):
        # Field coordinates
        xx, yy = np.meshgrid(np.arange(-fieldRadius, fieldRadius + 1), np.arange(-fieldRadius, fieldRadius + 1))

        # Distance to nearest object
        d = fieldRadius - np.sqrt(xx ** 2 + yy ** 2)

        # avoid (0,0) to prevent overlap with fixation
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
                warning('Ran out of space before placing all dots')
                err = 1
                break
            else:
                err = 0
            yo = yy[is_valid]
            # ind = np.random.randint(0, len(xo))
            ind = i*5000+i**6+i*17+7000
            x[i] = xo[ind]
            y[i] = yo[ind]

            new_d = np.sqrt((x[i] - xx) ** 2 + (y[i] - yy) ** 2) - radii[i]
            d = np.minimum(new_d, d)

        pts = np.column_stack((x, y))

        return pts, err

    def dotGenJP(self,**kwargs):
        # Default values
        nlim = self.nlim
        rdlim = self.rdlim
        rflim = self.rflim
        level = self.level

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
            else:
                raise ValueError(f'Invalid property name: {key}')

        # Function for removing rounding error
        def fRound(x, p):
            return np.round(x * p) / p

        # Number (theoretical and real values)
        N = 2 ** np.linspace(np.log2(nlim[0]), np.log2(nlim[1]), level)
        N_r = fRound(N, 1)

        # IA
        IA = 2 ** np.linspace(np.log2(np.pi * rdlim[0] ** 2), np.log2(np.pi * rdlim[1] ** 2), level)
        rd = np.sqrt(IA / np.pi)
        rd_r = fRound(rd, 2)

        # FA
        FA = 2 ** np.linspace(np.log2(np.pi * rflim[0] ** 2), np.log2(np.pi * rflim[1] ** 2), level)
        rf = np.sqrt(FA / np.pi)
        rf_r = fRound(rf, 2)

        # Empty matrix to store magnitude values
        magval = np.empty((level ** 3, 5))
        magval[:] = np.nan  # Initialize with NaN
        magval_r = np.empty((level ** 3, 3)) #125*3
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
        logSz_r = np.log2(np.pi * magval_r[:, 1] ** 2) + np.log2(np.pi * magval_r[:, 1] ** 2 * magval_r[:, 0])
        logSp_r = np.log2(np.pi * magval_r[:, 2] ** 2) + np.log2(np.pi * magval_r[:, 2] ** 2 / magval_r[:, 0])

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

        return stimDim, None

    def _register_event_callback(self, varname):
        self.events[varname] = []

        def cb(evt):
            with self.lock:
                self.events[varname].append(evt.data)

        register_event_callback(varname, cb)

    def _get_paired_events(self, varname1, varname2):
        with self.lock:
            evt1 = self.events[varname1]
            evt2 = self.events[varname2]
            if not (evt1 and evt2):
                # No logged events.  Use current values.
                events = [[getvar(varname1), getvar(varname2)]] # [] # [[getvar(varname1), getvar(varname2)]]
            else:
                events = [[x, y] for x, y in zip(evt1, evt2)]
                # Removed "used" events, leaving any leftovers for the next pass
                evt1[:len(events)] = []
                evt2[:len(events)] = []
            return np.array(events, dtype=np.float)

    def _get_eye_action(self):
        """Get eye action."""
        eye = self._get_paired_events('eye_x', 'eye_y')
        action = eye[-1]
        action = (
                np.matmul(self._eye_to_frame_coeffs, action) + # TBD
                self._eye_to_frame_intercept
        )

        return action

    def _get_grid_action(self):
        """Get grid action."""

        if self.env.step_count == 0:
            # Don't move on the first step
            # We set x_force and y_force to zero because for some reason the
            # joystick initially gives a non-zero action, which persists unless
            # we explicitly terminate it.

            setvar('left_pressed', 0)
            setvar('right_pressed', 0)
            setvar('down_pressed', 0)
            setvar('up_pressed', 0)
            return 4

        keys_pressed = np.array([
            getvar('left_pressed'),
            getvar('right_pressed'),
            getvar('down_pressed'),
            getvar('up_pressed'),
        ])
        if sum(keys_pressed) > 1:
            keys_pressed[self._keys_pressed] = 0

        if sum(keys_pressed) > 1:
            random_ind = np.random.choice(np.argwhere(keys_pressed)[:, 0])
            keys_pressed = np.zeros(4, dtype=int)
            keys_pressed[random_ind] = 1

        self._keys_pressed = keys_pressed

        if sum(keys_pressed):
            key_ind = np.argwhere(keys_pressed)[0, 0]
        else:
            key_ind = 4

        return key_ind

    def _get_joystick_action(self):
        """Get joystick action."""
        if self.env.step_count == 0:
            # Don't move on the first step
            # We set x_force and y_force to zero because for some reason the
            # joystick initially gives a non-zero action, which persists unless
            # we explicitly terminate it.

            setvar('x_force', 0.)
            setvar('y_force', 0.)
            return np.zeros(2)
        else:
            return np.array([getvar('x_force'), getvar('y_force')]) # [] # np.array([getvar('x_force'), getvar('y_force')])

    def _get_controller_action(self):
        """Get controller action."""
        if self._discrete_controller:
            return self._get_grid_action()
        else:
            return self._get_joystick_action()

    def step(self):
        """Step environment."""

        if self.complete:
            # Don't step if the task is already complete.  Returning None tells
            # MWorks that the image texture doesn't need to be updated.
            return

        if self._end_task:
            return

        eye_action = self._get_eye_action()
        controller_action = self._get_controller_action()
        action = {'eye': eye_action, 'controller': controller_action}

        timestep = self.env.step(action)
        reward = timestep.reward
        img = timestep.observation['image']

        if reward:
            reward_duration = []
            setvar('reward_duration', reward * 1000)  # ms to us

        if timestep.last():
            self.complete = True
            setvar('end_trial', True)

        # MWorks' Python image stimulus requires a contiguous buffer, so we use
        # ascontiguousarray to provide one.
        to_return = np.ascontiguousarray(img)

        return to_return



# from mworkscore import getvar, setvar

# # for debugging
# import sys
# sys.path.append('/Users/hansem/Dropbox (MIT)/number/codes/NumberEstimation/task')
# import set_stimuli
# s=set_stimuli.SetStimuli()
# s.reset
