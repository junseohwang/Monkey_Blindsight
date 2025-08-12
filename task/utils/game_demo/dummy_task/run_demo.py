"""Run human demo on dummy task.

See README.md for documentation."""
#pylint: disable=import-error, no-name-in-module

from matplotlib import pyplot as plt
import numpy as np
import sys
from . import task as task_lib


class MatplotlibUI(object):
    """Class for visualizing the environment based on Matplotlib."""

    def __init__(self):

        plt.ion()
        self._fig = plt.figure(figsize=(6, 6))
        self._ax = plt.subplot(111)
        self._ax.axis('off')
        self._setup_callbacks()

    @property
    def ax_image(self):
        return self._ax

    def _setup_callbacks(self):
        """Default callbacks for the UI."""

        # Pressing escape should stop the UI
        def _onkeypress(event):
            if event.key == 'escape':
                # Stop UI
                print('Pressed escape, stopping UI.')
                plt.close(self._fig)
                sys.exit()

        self._fig.canvas.mpl_connect('key_release_event', _onkeypress)

    def update(self, reward, img):
        """Draw image."""
        self._ax.clear()
        self._ax.imshow(img, interpolation='none')
        self._ax.set_xticks([])
        self._ax.set_yticks([])

        # Indicate success
        if reward:
            color = 'green'
            linewidth = 8
        else:
            color = 'black'
            linewidth = 1
        for sp in self._ax.spines.values():
            sp.set_color(color)
            sp.set_linewidth(linewidth)
        
        plt.show(block=False)
        plt.pause(0.1)

    def register_callback(self, event_name, callback):
        """Register a callback for the given event."""
        self._fig.canvas.mpl_connect(event_name, callback)


class HumanAgent(object):
    """Demo agent."""

    def __init__(self):
        self._click = None

    def register_callbacks(self, ui):
        """Register the matplotlib callbacks required by the agent."""

        def _onclick(event):
            if event.inaxes and event.inaxes == ui.ax_image:
                # Map the click into axis-fraction positions.
                click = event.inaxes.transAxes.inverted().transform(
                    (event.x, event.y))
                self._click = np.array(click)
            else:
                self._click = None
            return

        ui.register_callback('button_press_event', _onclick)

    def step(self):
        """Take a step."""

        def _get_click():
            """Get mouse click."""
            click = None
            while click is None:
                x = plt.waitforbuttonpress()
                if x:
                    print(
                        'You pressed a key, but were supposed to click with '
                        'the mouse.')
                else:
                    click = self._click
            return click

        # Get action from user.
        print('Click on screen for joystick force')
        click_joystick = _get_click()
        print('Click on screen for eye position')
        click_eye = _get_click()
        action = {
            'joystick': [click_joystick - 0.5],
            'eye': [click_eye],
        }
        return action


def main():
    """Run interactive task demo."""
    task = task_lib.Task(image_size=(512, 512))
    task.reset()

    agent = HumanAgent()
    ui = MatplotlibUI()
    agent.register_callbacks(ui)
    ui.update(0., task.observation())

    while True:
        action = agent.step()
        reward, img = task.step(action)
        ui.update(reward, img)


if __name__ == "__main__":
    main()
