"""

A simple demo of dragging anchor points

Hold shift to drag in 'resize-center' mode. Eitherwise drags in 'resize' mode

"""


import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from bermuda.bbox import BBox
from bermuda.controller import Controller

ax = plt.gca()
bb = BBox(center=(300, 200), width=20, height=50)
controller = Controller(None, bb)

# draw the bbox
r = Rectangle((0, 0), width=1, height=1,
              facecolor='none', edgecolor='k',
              transform=bb.transform)
ax.add_patch(r)


def update():
    r.set_transform(controller.bbox.transform)
    ax.figure.canvas.draw()

controller.connect_mpl(ax.figure.canvas)
controller.move.add_callback(update)

# bb.tie_to_axes(ax)

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

plt.show()
