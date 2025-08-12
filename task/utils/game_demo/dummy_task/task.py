"""Dummy task.

See README.md for a description.
"""
#pylint: disable=import-error, no-name-in-module

import numpy as np
from PIL import Image
from PIL import ImageDraw


_TRIANGLE = 0.1 * np.array([
    [-1., -1./np.sqrt(3)],
    [1., -1./np.sqrt(3)],
    [0., 2./np.sqrt(3)],
])

_SQUARE = 0.1 * np.array([
    [-1., -1.],
    [-1., 1.],
    [1., 1.],
    [1., -1.],
])


class PILRenderer():
    """Render using Python Image Library (PIL/Pillow)."""

    def __init__(self, image_size=(512, 512)):
        """Construct PIL renderer."""
        self._canvas_size = image_size        
        self._canvas_bg = Image.new('RGB', self._canvas_size, (0, 0, 0))
        self._canvas = Image.new('RGB', self._canvas_size)
        self._draw = ImageDraw.Draw(self._canvas, 'RGBA')

        self._agent_color = [255, 0, 0]
        self._joystick_target_color = [255, 0, 0]
        self._eye_target_color = [0, 255, 0]


    def __call__(self, state):
        """Render state."""
        self._canvas.paste(self._canvas_bg)

        # Render agent
        agent_vertices = _TRIANGLE + state['agent_pos']
        self._draw.polygon(
            [tuple(v) for v in self._canvas_size * agent_vertices],
            fill=tuple(self._agent_color))

        # Render joystick target
        joystick_target_vertices = _SQUARE + state['joystick_target_pos']
        self._draw.polygon(
            [tuple(v) for v in self._canvas_size * joystick_target_vertices],
            fill=tuple(self._joystick_target_color))

        # Render eye target
        eye_target_vertices = _SQUARE + state['eye_target_pos']
        self._draw.polygon(
            [tuple(v) for v in self._canvas_size * eye_target_vertices],
            fill=tuple(self._eye_target_color))

        # PIL uses a coordinate system with the origin (0, 0) at the upper-left, but
        # our environment uses an origin at the bottom-left (i.e. mathematical
        # convention). Hence we need to flip the render vertically to correct for
        # that.
        image = np.flipud(np.array(self._canvas))
        return image


class Task():
    """Task class."""
    
    def __init__(self, image_size=(512, 512), error_tol=0.15):
        """Constructor."""
        self._renderer = PILRenderer(image_size=image_size)
        self._error_tol = error_tol
        
    def reset(self):
        """Begin new trial."""
        self._state = {
            'agent_pos': np.random.uniform(0.1, 0.9, size=(2,)),
            'joystick_target_pos': np.random.uniform(0.1, 0.9, size=(2,)),
            'eye_target_pos': np.random.uniform(0.1, 0.9, size=(2,)),
        }

    def step(self, action):
        """Step the environment with an action."""
        eye_pos = np.mean(action['eye'], axis=0)
        joystick_force = np.mean(action['joystick'], axis=0)

        # Move agent
        self._state['agent_pos'] += 5e-1 * joystick_force
        
        # Get rendered image
        img = self.observation()

        # Get reward
        joystick_error = np.linalg.norm(
            self._state['agent_pos'] - self._state['joystick_target_pos'])
        eye_error = np.linalg.norm(
            eye_pos - self._state['eye_target_pos'])
        if (joystick_error < self._error_tol) and (eye_error < self._error_tol):
            reward = 100  # ms to activate solenoid
            self.reset()
        else:
            reward = 0

        return reward, img

    def observation(self):
        return self._renderer(self._state)
