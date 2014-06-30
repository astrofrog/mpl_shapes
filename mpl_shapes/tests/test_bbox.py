from itertools import product
from numpy.testing import assert_allclose
import pytest

from ..bbox import AnchorPoint, FrozenError, BBox


class TestAnchor(object):

    def setup_method(self, method):
        self.a = AnchorPoint(x=1, y=2)

    def test_anchor_init(self):
        assert self.a.x == 1
        assert self.a.y == 2
        assert not self.a.frozen
        assert not self.a.visible

    def test_anchor_change(self):
        assert self.a.x == 1
        assert self.a.y == 2
        self.a.x = 3
        self.a.y = 4
        assert self.a.x == 3
        assert self.a.y == 4

    def test_anchor_freeze(self):
        assert self.a.x == 1
        assert self.a.y == 2
        self.a.frozen = True
        with pytest.raises(FrozenError):
            self.a.x = 3
        with pytest.raises(FrozenError):
            self.a.y = 4
        self.a.frozen = False
        self.a.x = 3
        self.a.y = 4
        assert self.a.x == 3
        assert self.a.y == 4

    def test_anchor_toggle_visibility(self):
        self.a.visible = False
        self.a.visible = True


class TestBBox(object):

    def setup_method(self, method):
        self.bbox = BBox(center=(3, 4), width=2, height=3, theta=0)

    def check_corners(self, vertices, corners):
        """
        Check that the corners of a BBox vertices dict mach expectations
        """
        assert_allclose(vertices['ul'], corners[0])
        assert_allclose(vertices['ur'], corners[1])
        assert_allclose(vertices['lr'], corners[2])
        assert_allclose(vertices['ll'], corners[3])

    def test_vertices(self):
        self.check_corners(self.bbox.vertices,
                           [(2, 5.5), (4, 5.5), (4, 2.5), (2, 2.5)])

    def test_center(self):
        self.bbox.center = (4, 5)
        assert self.bbox.center == (4, 5)
        self.check_corners(self.bbox.vertices,
                           [(3, 6.5), (5, 6.5), (5, 3.5), (3, 3.5)])

    def test_width(self):
        self.bbox.width = 4
        assert self.bbox.width == 4
        self.check_corners(self.bbox.vertices,
                           [(1, 5.5), (5, 5.5), (5, 2.5), (1, 2.5)])

    def test_height(self):
        self.bbox.height = 4
        assert self.bbox.height == 4
        self.check_corners(self.bbox.vertices,
                           [(2, 6), (4, 6), (4, 2), (2, 2)])

    def test_rotate_pos(self):
        self.bbox.theta = 90.
        assert self.bbox.theta == 90.
        self.check_corners(self.bbox.vertices,
                           [(1.5, 3), (1.5, 5), (4.5, 5), (4.5, 3)])

    def test_rotate_neg(self):
        self.bbox.theta = -90.
        assert self.bbox.theta == -90.
        self.check_corners(self.bbox.vertices,
                           [(4.5, 5), (4.5, 3), (1.5, 3), (1.5, 5)])

    def test_aspect(self):
        assert_allclose(self.bbox.aspect, 2. / 3.)
        self.bbox.width = 3
        assert_allclose(self.bbox.aspect, 1.)
        self.bbox.width = 4
        assert_allclose(self.bbox.aspect, 4. / 3.)

    def test_aspect_set(self):
        self.bbox.aspect = 1
        assert_allclose(self.bbox.height, 2.)


class AnchorDragBase(object):

    """ Base class, that moves all anchors in several directions

    Subclasses override the check method, to test that the drag behaves
    as expected
    """

    # starting position of bbox
    CENTER = (1, 2)
    WIDTH = 2
    HEIGHT = 4
    THETA = 0

    # drag each handle through every combination of these
    # displacements
    dx = [-1, 0, 1]
    dy = [-1, 0, 1]

    def iter_drags(self):
        """ Drag an anchor in a variety of different directions """
        for anchor, dx, dy in product('ul uc ur ll lc lr cl cr'.split(),
                                      self.dx,
                                      self.dy):
            bb = BBox(center=self.CENTER, width=self.WIDTH,
                      height=self.HEIGHT, theta=self.THETA)
            x, y = bb.anchor_pos(anchor)
            bb.move_anchor(x + dx, y + dy, anchor)
            yield anchor, dx, dy, bb

    def test_drags(self):
        """ Assert that the bbox changes as expected
            as a particular anchor moves

            Parameters
            ----------
            anchor : which anchor to drag
            dx_sign : Direction of width change if anchor is moved right
            dy_sign: Direction of height change if anchor is moved up
        """
        for anchor, dx, dy, bb in self.iter_drags():
            yield self.check, anchor, dx, dy, bb

    def check(self, anchor, dx, dy, bb):
        raise NotImplementedError()


class TestDragUnconstrained(AnchorDragBase):

    """
    Dragging of anchors with no constraints
    """

    def check(self, anchor, dx, dy, bb):
        dx_sign = dict(l=-1, c=0, r=1)[anchor[1]]
        dy_sign = dict(u=1, c=0, l=-1)[anchor[0]]

        assert bb.width == self.WIDTH + dx_sign * dx
        assert bb.height == self.HEIGHT + dy_sign * dy
        assert_allclose(bb.center[0], self.CENTER[0] + dx_sign / 2. * dx)
        assert_allclose(bb.center[1], self.CENTER[1] + dy_sign / 2. * dy)
        assert bb.theta == self.THETA
