import math
import os
import sys

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


def render_scene():
    img = Image.new('RGB', (scene_width, scene_height))

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

    draw = ImageDraw.Draw(img, 'RGBA')
    draw.ellipse([x0 - size/2, y0, x1 - size/2, y1], fill=(0,255,0,255))
    draw.ellipse([x0, y0, x1, y1], fill=(255,0,0,127))

    return img.tobytes()
