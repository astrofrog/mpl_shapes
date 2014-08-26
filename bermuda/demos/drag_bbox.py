"""

A simple demo of dragging anchor points

Hold shift to drag in 'resize-center' mode. Eitherwise drags in 'resize' mode

"""


import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

from bermuda.bbox import BBox


ax = plt.gca()
bb = BBox()
anchors = {}
ACTIVE_ANCHOR = None

# draw the bbox and anchors
r = Rectangle((-0.5, -0.5), width=1, height=1, facecolor='none', edgecolor='k')
ax.add_patch(r)

for k, v in bb.vertices.items():
    c = Circle(v, radius=0.06, facecolor='k', picker=10)
    anchors[c] = k
    ax.add_patch(c)

# event handlers


def on_pick(event):
    global ACTIVE_ANCHOR
    if ACTIVE_ANCHOR is None:
        ACTIVE_ANCHOR = anchors[event.artist]
    else:
        ACTIVE_ANCHOR = None


def on_move(event):
    if not ACTIVE_ANCHOR or not event.inaxes:
        return
    if event.key and 'shift' in event.key:
        mode = 'resize-center'
    else:
        mode = 'resize'

    bb.move_anchor(event.xdata, event.ydata, ACTIVE_ANCHOR, mode=mode)

    # update artists
    r.set_bounds(bb.center[0] - bb.width / 2,
                 bb.center[1] - bb.height / 2,
                 bb.width, bb.height)
    v = bb.vertices
    for artist, key in anchors.items():
        artist.center = v[key]

    ax.figure.canvas.draw()


cid1 = ax.figure.canvas.mpl_connect('pick_event', on_pick)
cid2 = ax.figure.canvas.mpl_connect('motion_notify_event', on_move)

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

plt.show()
