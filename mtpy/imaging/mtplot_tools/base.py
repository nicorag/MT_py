# -*- coding: utf-8 -*-
"""
Base classes for plotting classes

:author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
from scipy import stats

import matplotlib.pyplot as plt

from .plot_settings import PlotSettings
from .plotters import add_raster
from .map_interpolation_tools import interpolate_to_map
from mtpy.utils.mtpy_logger import get_mtpy_logger

# =============================================================================
# Base
# =============================================================================


class PlotBase(PlotSettings):
    """
    base class for plotting objects

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.logger = get_mtpy_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        self._basename = self.__class__.__name__.lower()

    def __str__(self):
        """
        rewrite the string builtin to give a useful message
        """

        return f"Plotting {self.__class__.__name__}"

    def __repr__(self):
        return self.__str__()

    def _set_subplot_params(self):
        # set some parameters of the figure and subplot spacing
        plt.rcParams["font.size"] = self.font_size
        plt.rcParams["figure.subplot.bottom"] = self.subplot_bottom
        plt.rcParams["figure.subplot.top"] = self.subplot_top
        plt.rcParams["figure.subplot.left"] = self.subplot_left
        plt.rcParams["figure.subplot.right"] = self.subplot_right

        if self.subplot_wspace is not None:
            plt.rcParams["figure.subplot.wspace"] = self.subplot_wspace
        if self.subplot_hspace is not None:
            plt.rcParams["figure.subplot.hspace"] = self.subplot_hspace

    def plot(self):
        pass

    def save_plot(
        self,
        save_fn,
        file_format="pdf",
        orientation="portrait",
        fig_dpi=None,
        close_plot=True,
    ):
        """
        save_plot will save the figure to save_fn.

        Arguments:
        -----------

            **save_fn** : string
                          full path to save figure to, can be input as
                          * directory path -> the directory path to save to
                            in which the file will be saved as
                            save_fn/station_name_ResPhase.file_format

                          * full path -> file will be save to the given
                            path.  If you use this option then the format
                            will be assumed to be provided by the path

            **file_format** : [ pdf | eps | jpg | png | svg ]
                              file type of saved figure pdf,svg,eps...

            **orientation** : [ landscape | portrait ]
                              orientation in which the file will be saved
                              *default* is portrait

            **fig_dpi** : int
                          The resolution in dots-per-inch the file will be
                          saved.  If None then the fig_dpi will be that at
                          which the figure was made.  I don't think that
                          it can be larger than fig_dpi of the figure.

            **close_plot** : [ true | false ]
                             * True will close the plot after saving.
                             * False will leave plot open

        :Example: ::

            >>> # to save plot as jpg
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.save_plot(r'/home/MT/figures', file_format='jpg')

        """

        if fig_dpi is None:
            fig_dpi = self.fig_dpi
        save_fn = Path(save_fn)
        if not save_fn.is_dir():
            file_format = save_fn.suffix[1:]
        else:
            save_fn = save_fn.joinpath(f"{self._basename}.{file_format}")
        self.fig.savefig(
            save_fn, dpi=fig_dpi, format=file_format, orientation=orientation
        )

        if close_plot:
            plt.close(self.fig)
        else:
            pass
        self.fig_fn = save_fn
        self.logger.info(f"Saved figure to: {self.fig_fn}")

    def update_plot(self):
        """
        update any parameters that where changed using the built-in draw from
        canvas.

        Use this if you change an of the .fig or axes properties

        :Example: ::

            >>> # to change the grid lines to only be on the major ticks
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> [ax.grid(True, which='major') for ax in [p1.axr,p1.axp]]
            >>> p1.update_plot()

        """

        self.fig.canvas.draw()

    def redraw_plot(self):
        """
        use this function if you updated some attributes and want to re-plot.

        :Example: ::

            >>> # change the color and marker of the xy components
            >>> import mtpy.imaging.mtplottools as mtplot
            >>> p1 = mtplot.PlotResPhase(r'/home/MT/mt01.edi')
            >>> p1.xy_color = (.5,.5,.9)
            >>> p1.xy_marker = '*'
            >>> p1.redraw_plot()
        """

        plt.close(self.fig)
        self.plot()


class PlotBaseMaps(PlotBase):
    """
    Base object for plot classes that use map views, includes methods for
    interpolation.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cell_size = 0.002
        self.n_padding_cells = 10
        self.interpolation_method = "delaunay"
        self.interpolation_power = 5
        self.nearest_neighbors = 7

        for key, value in kwargs.items():
            setattr(self, key, value)

    def interpolate_to_map(self, plot_array, component):
        """
        interpolate points onto a 2d map.

        :param plot_array: DESCRIPTION
        :type plot_array: TYPE
        :param component: DESCRIPTION
        :type component: TYPE
        :param cell_size: DESCRIPTION, defaults to 0.002
        :type cell_size: TYPE, optional
        :param n_padding_cells: DESCRIPTION, defaults to 10
        :type n_padding_cells: TYPE, optional
        :param interpolation_method: DESCRIPTION, defaults to "delaunay"
        :type interpolation_method: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        return interpolate_to_map(
            plot_array,
            component,
            cell_size=self.cell_size,
            n_padding_cells=self.n_padding_cells,
            interpolation_method=self.interpolation_method,
            interpolation_power=self.interpolation_power,
            nearest_neighbors=self.nearest_neighbors,
        )

    def _get_interpolated_z(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if not hasattr(tf, "z_interp_dict"):
            tf.z_interp_dict = tf.get_interp1d_functions_z()
        return np.nan_to_num(
            np.array(
                [
                    [
                        tf.z_interp_dict["zxx"]["real"](1 / self.plot_period)[0]
                        + 1j
                        * tf.z_interp_dict["zxx"]["imag"](
                            1.0 / self.plot_period
                        )[0],
                        tf.z_interp_dict["zxy"]["real"](1.0 / self.plot_period)[
                            0
                        ]
                        + 1j
                        * tf.z_interp_dict["zxy"]["imag"](
                            1.0 / self.plot_period
                        )[0],
                    ],
                    [
                        tf.z_interp_dict["zyx"]["real"](1.0 / self.plot_period)[
                            0
                        ]
                        + 1j
                        * tf.z_interp_dict["zyx"]["imag"](
                            1.0 / self.plot_period
                        )[0],
                        tf.z_interp_dict["zyy"]["real"](1.0 / self.plot_period)[
                            0
                        ]
                        + 1j
                        * tf.z_interp_dict["zyy"]["imag"](
                            1.0 / self.plot_period
                        )[0],
                    ],
                ]
            )
        )

    def _get_interpolated_z_err(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if not hasattr(tf, "z_interp_dict"):
            tf.z_interp_dict = tf.get_interp1d_functions_z()
        return np.nan_to_num(
            np.array(
                [
                    [
                        tf.z_interp_dict["zxx"]["err"](1.0 / self.plot_period)[
                            0
                        ],
                        tf.z_interp_dict["zxy"]["err"](1.0 / self.plot_period)[
                            0
                        ],
                    ],
                    [
                        tf.z_interp_dict["zyx"]["err"](1.0 / self.plot_period)[
                            0
                        ],
                        tf.z_interp_dict["zyy"]["err"](1.0 / self.plot_period)[
                            0
                        ],
                    ],
                ]
            )
        )

    def _get_interpolated_t(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if not hasattr(tf, "t_interp_dict"):
            tf.z_interp_dict = tf.get_interp1d_functions_t()
        if tf.t_interp_dict == {}:
            return np.zeros((1, 1, 2), dtype=complex)
        return np.nan_to_num(
            np.array(
                [
                    [
                        [
                            tf.t_interp_dict["tzx"]["real"](
                                1.0 / self.plot_period
                            )[0]
                            + 1j
                            * tf.t_interp_dict["tzx"]["imag"](
                                1.0 / self.plot_period
                            )[0],
                            tf.t_interp_dict["tzy"]["real"](
                                1.0 / self.plot_period
                            )[0]
                            + 1j
                            * tf.t_interp_dict["tzy"]["imag"](
                                1.0 / self.plot_period
                            )[0],
                        ]
                    ]
                ]
            )
        )

    def _get_interpolated_t_err(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        if not hasattr(tf, "t_interp_dict"):
            tf.z_interp_dict = tf.get_interp1d_functions_t()

        if tf.t_interp_dict == {}:
            return np.array((1, 1, 2), dtype=float)
        return np.nan_to_num(
            np.array(
                [
                    [
                        [
                            tf.t_interp_dict["tzx"]["err"](
                                1.0 / self.plot_period
                            )[0],
                            tf.t_interp_dict["tzy"]["err"](
                                1.0 / self.plot_period
                            )[0],
                        ]
                    ]
                ]
            )
        )

    def add_raster(self, ax, raster_fn, add_colorbar=True, **kwargs):
        """
        Add a raster to an axis using rasterio

        :param ax: DESCRIPTION
        :type ax: TYPE
        :param raster_fn: DESCRIPTION
        :type raster_fn: TYPE
        :param add_colorbar: DESCRIPTION, defaults to True
        :type add_colorbar: TYPE, optional
        :param **kwargs: DESCRIPTION
        :type **kwargs: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        return add_raster(ax, raster_fn, add_colorbar=True, **kwargs)


class PlotBaseProfile(PlotBase):
    """
    Base object for profile plots like pseudo sections.

    """

    def __init__(self, tf_list, **kwargs):
        super().__init__(**kwargs)

        self.mt_data = tf_list
        self.profile_vector = None
        self.profile_angle = None
        self.profile_line = None
        self.profile_reverse = False

        self.x_stretch = 5000
        self.y_stretch = 1000
        self.y_scale = "period"

        self._rotation_angle = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    # ---need to rotate data on setting rotz
    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        """
        only a single value is allowed
        """
        for tf in self.mt_data:
            tf.rotation_angle = value
        self._rotation_angle = value

    def _get_profile_line(self, x=None, y=None):
        """
        Get profile line doing a linear regression through data points

        :param x: DESCRIPTION, defaults to None
        :type x: TYPE, optional
        :param y: DESCRIPTION, defaults to None
        :type y: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        if x is None and y is None:
            x = np.zeros(self.mt_data.n_stations)
            y = np.zeros(self.mt_data.n_stations)

            for ii, tf in enumerate(self.mt_data.values()):
                x[ii] = tf.longitude
                y[ii] = tf.latitude

        elif x is None or y is None:
            raise ValueError("get_profile")

        # check regression for 2 profile orientations:
        # horizontal (N=N(E)) or vertical(E=E(N))
        # use the one with the lower standard deviation
        profile1 = stats.linregress(x, y)
        profile2 = stats.linregress(y, x)
        # if the profile is rather E=E(N), the parameters have to converted
        # into N=N(E) form:
        if profile2.stderr < profile1.stderr:
            self.profile_line = (
                1.0 / profile2.slope,
                -profile2.intercept / profile2.slope,
            )
            profile = profile2
        else:
            self.profile_line = profile1[:2]
            profile = profile1

        self.profile_angle = (90 - np.rad2deg(np.arctan(profile.slope))) % 180

        self.profile_vector = np.array([1, profile.slope])
        self.profile_vector /= np.linalg.norm(self.profile_vector)

    def _get_offset(self, tf=None, x=None, y=None):
        """
        Get approximate offset distance for the station

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        if tf is not None:
            station_vector = np.array(
                [tf.longitude, tf.latitude - self.profile_line[1]]
            )
        elif x is not None and y is not None:
            station_vector = np.array([x, y - self.profile_line[1]])
        else:
            raise ValueError(" get_offset needs an input of TF or x and y")

        direction = 1
        if self.profile_reverse:
            direction = -1

        return direction * (
            np.linalg.norm(
                np.dot(self.profile_vector, station_vector)
                * self.profile_vector
            )
            * self.x_stretch
        )

    def _get_interpolated_z(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        return np.nan_to_num(
            np.array(
                [
                    [
                        tf.z_interp_dict["zxx"]["real"](1 / self.plot_period)
                        + 1j
                        * tf.z_interp_dict["zxx"]["imag"](
                            1.0 / self.plot_period
                        ),
                        tf.z_interp_dict["zxy"]["real"](1.0 / self.plot_period)
                        + 1j
                        * tf.z_interp_dict["zxy"]["imag"](
                            1.0 / self.plot_period
                        ),
                    ],
                    [
                        tf.z_interp_dict["zyx"]["real"](1.0 / self.plot_period)
                        + 1j
                        * tf.z_interp_dict["zyx"]["imag"](
                            1.0 / self.plot_period
                        ),
                        tf.z_interp_dict["zyy"]["real"](1.0 / self.plot_period)
                        + 1j
                        * tf.z_interp_dict["zyy"]["imag"](
                            1.0 / self.plot_period
                        ),
                    ],
                ]
            )
        )

    def _get_interpolated_z_err(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        return np.nan_to_num(
            np.array(
                [
                    [
                        tf.z_interp_dict["zxx"]["err"](1.0 / self.plot_period),
                        tf.z_interp_dict["zxy"]["err"](1.0 / self.plot_period),
                    ],
                    [
                        tf.z_interp_dict["zyx"]["err"](1.0 / self.plot_period),
                        tf.z_interp_dict["zyy"]["err"](1.0 / self.plot_period),
                    ],
                ]
            )
        )

    def _get_interpolated_t(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        if tf.t_interp_dict == {}:
            return np.zeros((1, 1, 2), dtype=complex)
        return np.nan_to_num(
            np.array(
                [
                    [
                        [
                            tf.t_interp_dict["tzx"]["real"](
                                1.0 / self.plot_period
                            )
                            + 1j
                            * tf.t_interp_dict["tzx"]["imag"](
                                1.0 / self.plot_period
                            ),
                            tf.t_interp_dict["tzy"]["real"](
                                1.0 / self.plot_period
                            )
                            + 1j
                            * tf.t_interp_dict["tzy"]["imag"](
                                1.0 / self.plot_period
                            ),
                        ]
                    ]
                ]
            )
        )

    def _get_interpolated_t_err(self, tf):
        """

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        if tf.t_interp_dict == {}:
            return np.array((1, 1, 2), dtype=float)
        return np.nan_to_num(
            np.array(
                [
                    [
                        [
                            tf.t_interp_dict["tzx"]["err"](
                                1.0 / self.plot_period
                            ),
                            tf.t_interp_dict["tzy"]["err"](
                                1.0 / self.plot_period
                            ),
                        ]
                    ]
                ]
            )
        )
