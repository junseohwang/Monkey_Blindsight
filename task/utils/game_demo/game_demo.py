import os
import sys
import threading

import numpy as np

if '' not in sys.path:
    sys.path.insert(0, '')

local_site_packages = os.path.expanduser(
    '~/Library/Python/%d.%d/lib/python/site-packages' % sys.version_info[:2]
    )
if local_site_packages not in sys.path:
    sys.path.append(local_site_packages)

from dummy_task.task import Task


class TaskManager:

    def __init__(self):
        self.task = Task(image_size=(getvar('image_pixel_width'),
                                     getvar('image_pixel_height')))
        self.lock = threading.Lock()

    def reset(self):
        self.task.reset()

        unregister_event_callbacks()
        self.events = {}
        for varname in ('eye_x', 'eye_y', 'joystick_x', 'joystick_y'):
            self._register_event_callback(varname)

        # image_size and image_origin are used to convert eye positions from
        # MWorks screen coordinates to image pixel coordinates
        self.image_size = np.array([getvar('image_size_x'),
                                    getvar('image_size_y')],
                                   dtype=np.float)
        self.image_origin = np.array([getvar('image_pos_x'),
                                      getvar('image_pos_y')],
                                     dtype=np.float) - self.image_size / 2.0

        self.complete = False

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
                events = [[getvar(varname1), getvar(varname2)]]
            else:
                events = [[x, y] for x, y in zip(evt1, evt2)]
                # Removed "used" events, leaving any leftovers for the next pass
                evt1[:len(events)] = []
                evt2[:len(events)] = []
            return np.array(events, dtype=np.float)

    def update(self):
        eye = self._get_paired_events('eye_x', 'eye_y')
        eye -= self.image_origin
        eye /= self.image_size

        joystick = self._get_paired_events('joystick_x', 'joystick_y')
        joystick /= 100.0  # Fudge factor to get reasonable movement speed

        if self.complete:
            # Don't step if the task is already complete.  Returning None tells
            # MWorks that the image texture doesn't need to be updated.
            return

        action = {
            'eye': eye,
            'joystick': joystick,
        }
        reward, img = self.task.step(action)

        if reward:
            setvar('reward_duration', reward * 1000)  # ms to us
            self.complete = True

        # dummy_task.task.PILRenderer uses numpy.flipud, which returns a
        # non-contiguous array.  However, MWorks' Python image stimulus requires
        # a contiguous buffer, so we use ascontiguousarray to provide one.
        return np.ascontiguousarray(img)
