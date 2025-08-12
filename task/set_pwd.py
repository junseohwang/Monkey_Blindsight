"""Set pwd variable depending on laptop vs rig."""

import os

if getvar('platform') == 'laptop':
    _PWD = '/Users/training1/Documents/Monkey/number-train_rig_outer/task'
    _PYTHON_SITE_PACKAGES = (
        '/opt/anaconda3/envs/mworks/lib/python3.8/site-packages'
    )
elif getvar('platform') == 'desktop':
    _PWD = '/Users/training1/Documents/Monkey/number-train_rig_outer/task'
    _PYTHON_SITE_PACKAGES = (
        '/Users/hansem/miniconda3/envs/mworks/lib/python3.8/site-packages'
    )
elif getvar('platform') == 'psychophysics':
    # laptop hansem
    _PWD = '/Users/training1/Documents/Monkey/number-train_rig_outer/task'
    _PYTHON_SITE_PACKAGES = (
        '/opt/anaconda3/envs/mworks/lib/python3.8/site-packages'
    )
elif getvar('platform') == 'monkey_ephys':
    # H
    _PWD = '/Users/training1/Documents/Monkey/number-train_rig_outer/task'
    _PYTHON_SITE_PACKAGES = (
        '/opt/miniconda3/envs/mworks/lib/python3.9/site-packages'
    )
elif getvar('platform') == 'monkey_train':
    # G
    _PWD = '/Users/training1/Documents/Monkey/number-train_rig_outer/task'
    _PYTHON_SITE_PACKAGES = (
        '/opt/anaconda3/envs/mworks/lib/python3.9/site-packages'
    )
else:
    raise ValueError('Invalid platform')

# Update pwd and python_site_packages variables in mworks
setvar('pwd', _PWD)
setvar('python_site_packages', _PYTHON_SITE_PACKAGES)