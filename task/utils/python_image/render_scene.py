import math
import os
import sys

import numpy as np

# MWorks' embedded Python does not add any external directories to sys.path,
# so your code must do so as needed
local_site_packages = os.path.expanduser(
    '~/Library/Python/%d.%d/lib/python/site-packages' % sys.version_info[:2]
    )
if local_site_packages not in sys.path:
    sys.path.append(local_site_packages)

from PIL import Image, ImageDraw


# getvar retrieves the value of the named MWorks variable
scene_width = getvar('scene_width')
scene_height = getvar('scene_height')

# Create a persistent buffer to minimize memory allocation
scene_buffer = np.empty((scene_width * 4, scene_height), np.uint8)


def render_scene():
    # Create an image backed by the buffer for both reading and writing
    img = Image.frombuffer('RGBA',
                           (scene_width, scene_height),
                           scene_buffer,
                           'raw', 'RGBA', 0, 1)
    img.readonly = False

    # Clear the buffer contents before drawing
    scene_buffer.fill(0)

    elapsed_time = getvar('elapsed_time') / 1e6  # microseconds to seconds

    # How the scene is rendered is determined entirely by the code that follows.
    # This example just draws a circle orbiting the center of the image at a
    # fixed angular speed.  The elapsed time is taken from MWorks (see above),
    # but everything else is computed here.

    size = 30
    angular_speed = 1  # radians per second

    theta = angular_speed * elapsed_time
    center_x = 0.5 * (0.9 * math.cos(theta) + 1) * (scene_width - 1)
    center_y = 0.5 * (0.9 * math.sin(theta) + 1) * (scene_height - 1)

    x0 = round(center_x - size/2)
    y0 = round(center_y - size/2)
    x1 = round(center_x + size/2)
    y1 = round(center_y + size/2)

    draw = ImageDraw.Draw(img)
    draw.ellipse([x0, y0, x1, y1], fill='red')
