import numpy as np

from matplotlib.transforms import Transform
from matplotlib.path import Path

class BBoxTransform(Transform):
    """
    A class to transform from the frame of reference of the bounding box to
    display coordinates.

    This is evaluated on-the-fly using the current bounding box and axes.

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        The Axes that the bounding box is being plotted into
    """

    input_dims = 2
    output_dims = 2
    is_separable = False

    def transform_path(self, path):
        """
        Transform a Matplotlib Path

        Parameters
        ----------
        path : :class:`~matplotlib.path.Path`
            The path to transform

        Returns
        -------
        path : :class:`~matplotlib.path.Path`
            The resulting path
        """
        return Path(self.transform(path.vertices), path.codes)

    transform_path_non_affine = transform_path

    def __init__(self, ax, bbox):
        self.ax = ax
        self.bbox = bbox
        super(BBoxTransform, self).__init__()

    def transform(self, coords):
        """
        Transform from bounding box coordinates to display coordinates.
        """

        # Make a copy of the coordinates
        data = coords.copy()
        x_data, y_data = data[:, 0], data[:, 1]

        # Apply bounding box scaling
        x_data *= self.bbox.width
        y_data *= self.bbox.height

        # Move to correct location
        x_data += self.bbox.center[0] - self.bbox.width * 0.5
        y_data += self.bbox.center[1] - self.bbox.height * 0.5

        # Transform to figure coordinates
        display = self.ax.transData.transform(data)
        x_disp, y_disp = display[:, 0], display[:, 1]

        # Find center of bounding box in display coordinates
        xc, yc = self.ax.transData.transform([self.bbox.center])[0]

        # Center on origin prior to rotation
        x_disp -= xc
        y_disp -= yc

        # Pre-compute cos and sin
        theta_rad = np.radians(self.bbox.theta)
        cos_theta = np.cos(theta_rad)
        sin_theta = np.sin(theta_rad)

        # Rotate
        x_disp[:], y_disp[:] = (x_disp * cos_theta - y_disp * sin_theta,
                                x_disp * sin_theta + y_disp * cos_theta)

        # Move back to original center
        x_disp += xc
        y_disp += yc

        return display

    def inverted(self, coords):
        raise NotImplementedError("")
