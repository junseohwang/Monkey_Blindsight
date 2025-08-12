# Number estimation (NE) task

## conditions
- stimuli: artificial (dot/banana), natural (coco)
- eye fixation: O or X
- movie: stimuli moved to choice targets

## steps
1. Install MWorks. Preferred version is the "bleeding edge"
   nightly build of MWorks, which you can install by downloading the "Nighly
   Build" on the [MWorks downloads page](https://mworks.github.io/downloads/). 

2. Open the following mwel files for each task in MWorks client:
   - NE with dot stimuli: NE_dot.mwel
        - modify 'subject' (human/monkey) and platform
        - DOUBLE CHECK if number_list sampled are what you intended (Mworks server console; set_stimuli.py)
        - related subfunctions are:
            - set_stimuli.py: JK Parks' algorithm to sample dot positions and size (c.f. script_generate_dots.py, dotGenJP.py, dotField2GKA.py)
            - keyboard.mwel: specify your keyboard's preferred_location_id
            - variables.mwel: list and define all variables
            - stimuli.mwel: specify visual stimuli objects
            - actions.mwel: specify animations' parameters
   - NE with banana stimuli: NE_banana.mwel
   - (To be done) NE with natural stimuli: NE_natural.mwel
