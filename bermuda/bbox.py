import numpy as np

from .transforms import BBoxTransform


class FrozenError(Exception):
    pass


class AnchorPoint(object):

    def __init__(self, x=0, y=0, frozen=False, visible=False):
        self._x = x
        self._y = y
        self._frozen = frozen
        self._visible = visible

    def _check_frozen(self):
        if self.frozen:
            raise FrozenError("Cannot move: anchor is frozen")

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._check_frozen()
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._check_frozen()
        self._y = value

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = bool(value)

    @property
    def frozen(self):
        return self._frozen

    @frozen.setter
    def frozen(self, value):
        self._frozen = bool(value)


class Pointer(object):

    def __init__(self, label):
        self.label = label

    def __get__(self, instance, owner=None):
        return getattr(instance, self.label)

    def __set__(self, instance, value):
        setattr(instance, self.label, value)


class BBox(object):

    center = Pointer('_center')
    width = Pointer('_width')
    height = Pointer('_height')
    theta = Pointer('_theta')

    def __init__(self, center=(0, 0), width=1, height=1, theta=0):
        self._center = center
        self._width = width
        self._height = height
        self._theta = theta
        self._transform = BBoxTransform(self)

    def copy(self):
        return BBox(self.center, self.width, self.height, self.theta)

    @property
    def transform(self, ax=None):
        """
        Return a matplotlib transform to transform from the frame of reference
        of the bounding box to the display coordinates.
        """
        return self._transform

    def tie_to_axes(self, ax):
        self._transform.tie_to_axes(ax)

    @property
    def aspect(self):
        """
        The aspect ratio (width / height)
        """
        return 1.0 * self._width / self._height

    @aspect.setter
    def aspect(self, value):
        """
        Change the aspect ratio (width/height), preserving the width
        """
        self._height = self._width / value

    @property
    def vertices(self):
        """
        The 4 corners of the Bbox, as a dict of tuples

        Returns a dict mapping vertex label to coordinate tuple
        """
        x = np.array([-0.5, 0, 0.5, 0.5, 0.5, 0, -0.5, -0.5]) * self.width
        y = np.array([0.5, 0.5, 0.5, 0, -0.5, -0.5, -0.5, 0]) * self.height

        # rotate
        t = np.radians(self.theta)
        x0 = x
        x = x * np.cos(t) - y * np.sin(t)
        y = x0 * np.sin(t) + y * np.cos(t)

        # translate
        x += self.center[0]
        y += self.center[1]

        labels = 'ul uc ur cr lr lc ll cl'.split()
        return dict((lbl, (x, y)) for lbl, x, y in zip(labels, x, y))

    def anchor_pos(self, anchor_id):
        """Return the coordinates of one of the anchor points of the bouding box

        Parameters
        ----------
        anchor_id: 'ul'|'uc'|'ur'|'cl'|'cc'|'cr'|'ll'|'lc'|'lr'
            An anchor label

        Returns
        -------
        Tuple of (x, y)
        """
        return self.vertices[anchor_id]

    def move_anchor(self, x, y, id, mode='resize'):
        """
        Update the bounding box by moving a particular anchor point.

        Parameters
        ----------
        x : float
            The x-location the anhchor was dragged to
        y : float
            The y-location the anchor was dragged to
        id : 'ul'|'uc'|'ur'|'cl'|'cc'|'cr'|'ll'|'lc'|'lr'
            The ID of the anchor point.
        mode : str, optional (default 'resize')
            How to respond to the update

            'resize' moves as few anchor points as possible during resizing
            'resize-center' preserves the center position
            'resize-aspect' preserves the aspect ratio
            'resize-center-aspect' preserves the center position and aspect ratio
            'resize-square' fixes the aspect ratio to 1
            'resize-center-square' fixes the aspect ratio to 1 and preserves the center
        """

        # Find id of opposite anchor
        opposite_id = {'ul': 'lr', 'uc': 'lc', 'ur': 'll', 'cl': 'cr',
                       'lr': 'ul', 'lc': 'uc', 'll': 'ur', 'cr': 'cl'}[id]

        v = self.vertices
        x0, y0 = v[id]
        x1, y1 = v[opposite_id]

        if mode == 'resize':

            if id[1] != 'c':  # update horizontal
                self._width = abs(x1 - x)
                self._center = (x + x1) / 2., self._center[1]
            if id[0] != 'c':  # update vertical
                self._height = abs(y1 - y)
                self._center = self._center[0], (y + y1) / 2.

            return self

        if mode == 'resize-center':
            if id[1] != 'c':  # update horizontal
                dx = (x - x0)
                l, r = x0 + dx, x1 - dx
                self._width = abs(l - r)
                self._center = (l + r) / 2., self._center[0]
            if id[0] != 'c':  # update vertical
                dy = (y - y0)
                b, t = y0 + dy, y1 - dy
                self._height = abs(b - t)
                self._center = self._center[0], (b + t) / 2.
            return self

        raise NotImplementedError(mode)
