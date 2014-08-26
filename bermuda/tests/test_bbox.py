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

    TEST_CASES = product('ul uc ur ll lc lr cl cr'.split(), dx, dy)

    @pytest.mark.parametrize(('anchor', 'dx', 'dy'), TEST_CASES)
    def test_drag(self, anchor, dx, dy):
        bb = BBox(center=self.CENTER, width=self.WIDTH,
                  height=self.HEIGHT, theta=self.THETA)
        self.bb0 = bb.copy()

        x, y = bb.anchor_pos(anchor)
        bb.move_anchor(x + dx, y + dy, anchor)
        self.check(anchor, dx, dy, bb)

    def check(self, anchor, dx, dy, bb):
        raise NotImplementedError()
