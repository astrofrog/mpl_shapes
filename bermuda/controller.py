"""
The classes in this module provides a GUI-agnostic interface
for describing mouse events, and updating BBoxes.
"""


def default_mode_chooser(event):
    """
    Choose a anchor drag mode based on the modifier keys of an event.

    Parameters
    ----------
    event : Event instance
        The event to choose the mode from

    Returns
    -------
    mode : str
        A handle drag mode. See :meth:`BBox.move_anchor` for details.

    Notes
    -----
    This default mode chooser mimics the style from Keynote, Illustrator, etc.
    """

    if event.super:
        return 'rotate'
    if event.shift and event.alt:
        return 'resize-center-aspect'
    if event.shift:
        return 'resize-aspect'
    if event.alt:
        return 'resize-center'
    return 'resize'


class MouseEvent(object):

    """
    Encapsulation of a Mouse event

    Parameters
    ----------
    x : float
        X location of the event, in BBox coordinates
    y : float
        Y location of the event, in BBox coordinates
    button : 1, 2, 3, None
        Which mouse button was pressed (1=left, 2=right, 3=middle)
    control : bool
        Whether control key was pressed
    alt : bool
        Whether alt key was pressed
    super : bool
        Whether super/command/windows key was pressed
    """

    def __init__(self, x, y, button,
                 shift=False,
                 control=False,
                 alt=False,
                 super=False):
        # X and Y are in bbox coordinates
        self.x = x
        self.y = y
        self.button = button
        self.control = alt
        self.shift = shift
        self.alt = alt
        self.super = super

    @property
    def left(self):
        return self.button == 1

    @property
    def middle(self):
        return self.button == 3

    @property
    def right(self):
        return self.button == 2

    @classmethod
    def from_mpl(cls, event):
        return cls(event.x, event.y, event.button,
                   shift=event.key and 'shift' in event.key,
                   control=event.key and 'ctrl' in event.key,
                   alt=event.key and 'alt' in event.key,
                   super=event.key and 'super' in event.key)


def callback(func):
    _callbacks = []

    def add_callback(f):
        _callbacks.append(f)

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        for c in _callbacks:
            c()
        return result

    wrapper.add_callback = add_callback

    return wrapper


class Controller(object):

    """
    Object which updates a BBox based on input events
    """

    def __init__(self, shape, bbox, mode_chooser=default_mode_chooser):
        """
        Parameters
        ----------
        shape : Shape instance
        bbox : BBox instance
        mode_chooser : func (optional, default=default_mode_chooser)
        """
        self.shape = shape
        self.bbox = bbox
        self.mode_chooser = mode_chooser

        self._anchor = None
        self._start_bbox = None
        self._start_event = None

    def press(self, event):
        """
        Process a mouse press event
        """

        # XXX support for add_anchor_point to polygons

        self._anchor = self.bbox.pick(event.x, event.y)

        print self._anchor
        if self._anchor is None:
            return
        self._start_bbox = self.bbox.copy()
        self._start_event = event

    @callback
    def move(self, event):
        """
        Process a mouse move event
        """
        if self._anchor is None:
            return

        x, y = event.x, event.y
        id = self._anchor
        mode = self.mode_chooser(event)

        result = self._start_bbox.copy().move_anchor(x, y, id, mode)
        self.bbox.update(result)

    def release(self, event):
        """
        Process a mouse release event
        """
        self._anchor = self._start_bbox = self._start_event = None

    def connect_mpl(self, canvas):
        def wrap(method):
            def result(event):
                event = MouseEvent.from_mpl(event)
                return method(event)
            return result

        self._cid1 = canvas.mpl_connect('button_press_event', wrap(self.press))
        self._cid2 = canvas.mpl_connect('motion_notify_event', wrap(self.move))
        self._cid3 = canvas.mpl_connect('button_release_event', wrap(self.release))
