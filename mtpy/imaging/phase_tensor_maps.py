# -*- coding: utf-8 -*-
"""
Plot phase tensor map in Lat-Lon Coordinate System

Revision History:
    Created by @author: jpeacock-pr on Thu May 30 18:20:04 2013

    Modified by Fei.Zhang@ga.gov.au 2017-03:

    brenainn.moushall 26-03-2020 15:07:14 AEDT:
        Add plotting of geotiff as basemap background.
        
    Updated 2022 by J. Peacock to work with v2
    
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colorbar as mcb
import matplotlib.colors as colors

try:
    import contextily as cx

    has_cx = True
except ModuleNotFoundError:
    has_cx = False

from mtpy.imaging.mtplot_tools import PlotBase, add_raster

import mtpy.imaging.mtcolors as mtcl
import mtpy.analysis.pt as MTpt

# ==============================================================================


class PlotPhaseTensorMaps(PlotBase):
    """
    Plots phase tensor ellipses in map view from a list of edi files

    """

    def __init__(self, tf_list, **kwargs):
        """
        Initialise the object
        :param kwargs: keyword-value pairs
        """
        super().__init__(**kwargs)

        self._rotation_angle = 0
        self.tf_list = tf_list

        # set the freq to plot
        self.plot_station = False
        self.plot_freq = 1.0
        self.ftol = 0.1
        self.interpolate = True
        # read in map scale
        self.map_scale = "deg"
        self.map_utm_zone = None
        self.map_epsg = None

        self.minorticks_on = True
        self.x_pad = 0.01
        self.y_pad = 0.01

        # arrow legend
        self.arrow_legend_position = "lower right"
        self.arrow_legend_xborderpad = 0.2
        self.arrow_legend_yborderpad = 0.2
        self.arrow_legend_fontpad = 0.05

        self.ref_ax_loc = (0.85, 0.1, 0.1, 0.1)

        # set a central reference point
        self.reference_point = (0, 0)

        self.cx_source = None
        self.cx_zoom = None
        if has_cx:
            self.cx_source = cx.providers.USGS.USTopo

        # station labels
        self.station_id = (0, 2)
        self.station_pad = 0.0005

        self.arrow_legend_fontdict = {"size": self.font_size, "weight": "bold"}
        self.station_font_dict = {"size": self.font_size, "weight": "bold"}

        for key, value in kwargs.items():
            setattr(self, key, value)

        # --> plot if desired ------------------------
        if self.show_plot:
            self.plot()

    @property
    def map_scale(self):
        return self._map_scale

    @map_scale.setter
    def map_scale(self, map_scale):
        self._map_scale = map_scale

        if self._map_scale == "deg":
            self.xpad = 0.005
            self.ypad = 0.005
            self.ellipse_size = 0.005
            self.tickstrfmt = "%.3f"
            self.y_label = "Latitude (deg)"
            self.x_label = "Longitude (deg)"

        elif self._map_scale == "m":
            self.xpad = 1000
            self.ypad = 1000
            self.ellipse_size = 500
            self.tickstrfmt = "%.0f"
            self.x_label = "Easting (m)"
            self.y_label = "Northing (m)"

        elif self._map_scale == "km":
            self.xpad = 1
            self.ypad = 1
            self.ellipse_size = 0.500
            self.tickstrfmt = "%.0f"
            self.x_label = "Easting (km)"
            self.y_label = "Northing (km)"

        else:
            raise ValueError(f"map scale {map_scale} is not supported.")

    # ---need to rotate data on setting rotz
    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        """
        only a single value is allowed
        """
        for tf in self.tf_list:
            tf.rotation_angle = value
        self._rotation_angle = value

    def _get_tick_format(self):
        """

        :return: DESCRIPTION
        :rtype: TYPE

        """

        # set tick parameters depending on the mapscale
        if self.map_scale == "deg":
            self.tickstrfmt = "%.2f"
        elif self.map_scale == "m" or self.map_scale == "km":
            self.tickstrfmt = "%.0f"

    def _set_axis_labels(self):
        # --> set axes properties depending on map scale------------------------
        if self.map_scale == "deg":
            self.ax.set_xlabel(
                "Longitude", fontsize=self.font_size, fontweight="bold"  # +2,
            )
            self.ax.set_ylabel(
                "Latitude", fontsize=self.font_size, fontweight="bold"  # +2,
            )
        elif self.map_scale == "m":
            self.ax.set_xlabel(
                "Easting (m)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )
            self.ax.set_ylabel(
                "Northing (m)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )
        elif self.map_scale == "km":
            self.ax.set_xlabel(
                "Easting (km)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )
            self.ax.set_ylabel(
                "Northing (km)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )

    def _get_patch(self, tf):
        """
        Get ellipse patch

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        new_Z, new_Tipper = tf.interpolate(
            [self.plot_freq], bounds_error=False
        )
        new_Z.compute_resistivity_phase()
        pt_obj = MTpt.PhaseTensor(z_object=new_Z)

        # if map scale is lat lon set parameters
        if self.map_scale == "deg":
            plotx = tf.longitude - self.reference_point[0]
            ploty = tf.latitude - self.reference_point[1]
        # if map scale is in meters easting and northing
        elif self.map_scale in ["m", "km"]:
            tf.project_point_ll2utm(
                epsg=self.map_epsg, utm_zone=self.map_utm_zone
            )

            plotx = tf.east - self.reference_point[0]
            ploty = tf.north - self.reference_point[1]
            if self.map_scale in ["km"]:
                plotx /= 1000.0
                ploty /= 1000.0
        else:
            raise NameError("mapscale not recognized")
        # --> set local variables
        phimin = np.nan_to_num(pt_obj.phimin[0])
        phimax = np.nan_to_num(pt_obj.phimax[0])
        eangle = np.nan_to_num(pt_obj.azimuth[0])

        color_array = self.get_pt_color_array(pt_obj)
        bounds = np.arange(
            self.ellipse_range[0],
            self.ellipse_range[1] + self.ellipse_range[2],
            self.ellipse_range[2],
        )

        # --> get ellipse properties
        # if the ellipse size is not physically correct make it a dot
        if phimax == 0 or phimax > 100 or phimin == 0 or phimin > 100:
            eheight = 0.0000001
            ewidth = 0.0000001
        else:
            scaling = self.ellipse_size / phimax
            eheight = phimin * scaling
            ewidth = phimax * scaling
        # make an ellipse
        ellipd = patches.Ellipse(
            (plotx, ploty),
            width=ewidth,
            height=eheight,
            angle=90 - eangle,
            lw=self.lw,
        )

        # get ellipse color
        ellipd.set_facecolor(
            mtcl.get_plot_color(
                color_array[0],
                self.ellipse_colorby,
                self.ellipse_cmap,
                self.ellipse_range[0],
                self.ellipse_range[1],
                bounds=bounds,
            )
        )

        if new_Tipper is not None:
            if "r" in self.plot_tipper == "yri":

                if new_Tipper.mag_real[0] <= self.arrow_threshold:
                    txr = (
                        new_Tipper.mag_real[0]
                        * self.arrow_size
                        * np.sin(
                            (new_Tipper.angle_real[0]) * np.pi / 180
                            + self.arrow_direction * np.pi
                        )
                    )
                    tyr = (
                        new_Tipper.mag_real[0]
                        * self.arrow_size
                        * np.cos(
                            (new_Tipper.angle_real[0]) * np.pi / 180
                            + self.arrow_direction * np.pi
                        )
                    )

                    self.ax.arrow(
                        plotx,
                        ploty,
                        txr,
                        tyr,
                        width=self.arrow_lw,
                        facecolor=self.arrow_color_real,
                        edgecolor=self.arrow_color_real,
                        length_includes_head=False,
                        head_width=self.arrow_head_width,
                        head_length=self.arrow_head_length,
                    )
                else:
                    pass
            # plot imaginary tipper
            if "i" in self.plot_tipper:
                if new_Tipper.mag_imag[0] <= self.arrow_threshold:
                    txi = (
                        new_Tipper.mag_imag[0]
                        * self.arrow_size
                        * np.sin(
                            (new_Tipper.angle_imag[0]) * np.pi / 180
                            + self.arrow_direction * np.pi
                        )
                    )
                    tyi = (
                        new_Tipper.mag_imag[0]
                        * self.arrow_size
                        * np.cos(
                            (new_Tipper.angle_imag[0]) * np.pi / 180
                            + self.arrow_direction * np.pi
                        )
                    )

                    self.ax.arrow(
                        plotx,
                        ploty,
                        txi,
                        tyi,
                        width=self.arrow_lw,
                        facecolor=self.arrow_color_imag,
                        edgecolor=self.arrow_color_imag,
                        length_includes_head=False,
                        head_width=self.arrow_head_width,
                        head_length=self.arrow_head_length,
                    )
        return ellipd, plotx, ploty

    def _add_colorbar(self):
        """
        Add phase tensor color bar

        :return: DESCRIPTION
        :rtype: TYPE

        """

        if self.cb_position is None:
            self.ax2, kw = mcb.make_axes(
                self.ax, orientation=self.cb_orientation, shrink=0.35
            )

        else:
            self.ax2 = self.fig.add_axes(self.cb_position)

        # make the colorbar
        if self.ellipse_cmap in list(mtcl.cmapdict.keys()):
            cmap_input = mtcl.cmapdict[self.ellipse_cmap]
        else:
            cmap_input = mtcl.cm.get_cmap(self.ellipse_cmap)

        if "seg" in self.ellipse_cmap:
            norms = colors.BoundaryNorm(self.ellipse_cmap_bounds, cmap_input.N)
            self.cb = mcb.ColorbarBase(
                self.ax2,
                cmap=cmap_input,
                norm=norms,
                orientation=self.cb_orientation,
                ticks=self.ellipse_cmap_bounds,
            )
        else:
            self.cb = mcb.ColorbarBase(
                self.ax2,
                cmap=cmap_input,
                norm=colors.Normalize(
                    vmin=self.ellipse_range[0], vmax=self.ellipse_range[1]
                ),
                orientation=self.cb_orientation,
            )

        # label the color bar accordingly
        self.cb.set_label(
            self.cb_label_dict[self.ellipse_colorby],
            fontdict={"size": self.font_size, "weight": "bold"},
        )

        # place the label in the correct location
        if self.cb_orientation == "horizontal":
            self.cb.ax.xaxis.set_label_position("top")
            self.cb.ax.xaxis.set_label_coords(0.5, 1.3)
        elif self.cb_orientation == "vertical":
            self.cb.ax.yaxis.set_label_position("right")
            self.cb.ax.yaxis.set_label_coords(1.25, 0.5)
            self.cb.ax.yaxis.tick_left()
            self.cb.ax.tick_params(axis="y", direction="in")

    # -----------------------------------------------
    # The main plot method for this module
    # -----------------------------------------------
    def plot(
        self,
        fig=None,
        save_path=None,
        show=True,
        raster_file=None,
        raster_kwargs={},
    ):
        """
        Plots the phase tensor map.
        :param fig: optional figure object
        :param save_path: path to folder for saving plots
        :param show: show plots if True
        :param raster_dict: dictionary containing information for a raster
         to be plotted below the phase tensors.

        """
        self._set_subplot_params()

        # make figure instance
        self.fig = plt.figure(
            self.fig_num, figsize=self.fig_size, dpi=self.fig_dpi
        )

        # clear the figure if there is already one up
        plt.clf()

        self.ax = self.fig.add_subplot(1, 1, 1, aspect="equal")

        self._get_tick_format()

        # make some empty arrays
        self.plot_xarr = np.zeros(len(self.tf_list))
        self.plot_yarr = np.zeros(len(self.tf_list))
        for index, tf in enumerate(self.tf_list):
            ellipse_patch, plot_x, plot_y = self._get_patch(tf)
            self.plot_xarr[index] = plot_x
            self.plot_yarr[index] = plot_y

            # ==> add ellipse to the plot
            self.ax.add_artist(ellipse_patch)

            # ------------Plot station name------------------------------
            if self.plot_station:
                self.ax.text(
                    plot_x,
                    plot_y + self.station_pad,
                    tf.station[self.station_id[0] : self.station_id[1]],
                    horizontalalignment="center",
                    verticalalignment="baseline",
                    fontdict=self.station_font_dict,
                )

        self._set_axis_labels()
        # --> set plot limits
        #    need to exclude zero values from the calculation of min/max!!!!
        self.ax.set_xlim(
            self.plot_xarr[self.plot_xarr != 0.0].min() - self.x_pad,
            self.plot_xarr[self.plot_xarr != 0.0].max() + self.x_pad,
        )
        self.ax.set_ylim(
            self.plot_yarr[self.plot_yarr != 0.0].min() - self.y_pad,
            self.plot_yarr[self.plot_xarr != 0.0].max() + self.y_pad,
        )

        # --> set tick label format
        self.ax.xaxis.set_major_formatter(FormatStrFormatter(self.tickstrfmt))
        self.ax.yaxis.set_major_formatter(FormatStrFormatter(self.tickstrfmt))
        #       self.ax.set_xticklabels(np.round(self.plot_xarr, decimals=2),
        #                                rotation=45)
        plt.setp(self.ax.get_xticklabels(), rotation=45)

        # plot raster data if provided and if mapscale is 'deg'
        ## Leaving this in for posterity, in the future we should use
        ## rasterio for plotting geotiffs or other geophysical data.
        if raster_file is not None:
            self.raster_ax, self.raster_cb = add_raster(
                self.ax, raster_file, **raster_kwargs
            )

        else:
            if has_cx:
                try:
                    cx_kwargs = {"source": self.cx_source, "crs": "EPSG:4326"}
                    if self.cx_zoom is not None:
                        cx_kwargs["zoom"] = self.cx_zoom
                    cx.add_basemap(
                        self.ax,
                        **cx_kwargs,
                    )
                except Exception as error:
                    self.logger.warning(
                        f"Could not add base map because {error}"
                    )

        # --> set title in period or freq
        titlefreq = "{0:.5g} (s)".format(1.0 / self.plot_freq)

        if not self.plot_title:
            self.ax.set_title(
                "Phase Tensor Map for " + titlefreq,
                fontsize=self.font_size + 2,
                fontweight="bold",
            )
        else:
            self.ax.set_title(
                self.plot_title + titlefreq,
                fontsize=self.font_size + 2,
                fontweight="bold",
            )
        # # --> plot induction arrow scale bar -----------------------------------
        # if self.plot_tipper.find("y") == 0:
        #     parrx = self.ax.get_xlim()
        #     parry = self.ax.get_ylim()
        #     try:
        #         axpad = self.arrow_legend_xborderpad
        #     except AttributeError:
        #         axpad = self.xpad + self.arrow_size
        #     try:
        #         aypad = self.arrow_legend_yborderpad
        #     except AttributeError:
        #         aypad = self.ypad
        #     try:
        #         txtpad = self.arrow_legend_fontpad
        #     except AttributeError:
        #         txtpad = 0.25 * es
        #     # make arrow legend postion and arrows coordinates
        #     if self.arrow_legend_position == "lower right":
        #         pax = parrx[1] - axpad
        #         pay = parry[0] + aypad
        #         # ptx = self.arrow_size
        #         # pty = 0
        #         txa = parrx[1] - axpad + self.arrow_size / 2.0
        #         # txy = pay+txtpad
        #     elif self.arrow_legend_position == "upper right":
        #         pax = parrx[1] - axpad
        #         pay = parry[1] - aypad
        #         # ptx = self.arrow_size
        #         # pty = 0
        #         txa = parrx[1] - axpad + self.arrow_size / 2.0
        #         # txy = pay+txtpad
        #     elif self.arrow_legend_position == "lower left":
        #         pax = parrx[0] + axpad
        #         pay = parry[0] + aypad
        #         # ptx = self.arrow_size
        #         # pty = 0
        #         txa = parrx[0] + axpad + self.arrow_size / 2.0
        #         # txy = pay+txtpad
        #     elif self.arrow_legend_position == "upper left":
        #         pax = parrx[0] + axpad
        #         pay = parry[1] - aypad
        #         # ptx = self.arrow_size
        #         # pty = 0
        #         txa = parrx[0] + axpad + self.arrow_size / 2.0
        #         # txy = pay+txtpad
        #     else:
        #         pass  # raise NameError('arrowlegend not supported.')
        #     # FZ: Sudpip?
        #     ptx = self.arrow_size
        #     pty = 0
        #     # txy = pay + txtpad

        #     self.ax.arrow(
        #         pax,
        #         pay,
        #         ptx,
        #         pty,
        #         width=self.arrow_lw,
        #         facecolor=self.arrow_color_real,
        #         edgecolor=self.arrow_color_real,
        #         length_includes_head=False,
        #         head_width=self.arrow_head_width,
        #         head_length=self.arrow_head_length,
        #     )

        # FZ: what is this '|T|=1'? and the horizontal line?
        # self.ax.text(txa,
        #              txy,
        #              '|T|=1',
        #              horizontalalignment='center',
        #              verticalalignment='baseline',
        #              fontdict={'size':self.font_size,'weight':'bold'})
        # END: if self.plot_tipper.find('yes') == 0 ---------------------------

        # make a grid with color lines
        self.ax.grid(True, alpha=0.3, which="both", color=(0.5, 0.5, 0.5))
        if self.minorticks_on:
            plt.minorticks_on()  # turn on minor ticks automatically

        self._add_colorbar()

        # ==> make a colorbar with appropriate colors
        # if self.cb_position is None:
        #     self.ax2, kw = mcb.make_axes(
        #         self.ax, orientation=self.cb_orientation, shrink=0.35
        #     )
        #     # FZ: try to fix colorbar h-position
        #     # from mpl_toolkits.axes_grid1 import make_axes_locatable
        #     #
        #     # # create an axes on the right side of ax. The width of cax will be 5%
        #     # # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        #     # divider = make_axes_locatable(self.ax)
        #     # self.ax2 = divider.append_axes("right", size="5%", pad=0.05)
        # else:
        #     self.ax2 = self.fig.add_axes(self.cb_position)
        # if cmap == "mt_seg_bl2wh2rd":
        #     # make a color list
        #     self.clist = [
        #         (cc, cc, 1) for cc in np.arange(0, 1 + 1.0 / (nseg), 1.0 / (nseg))
        #     ] + [(1, cc, cc) for cc in np.arange(1, -1.0 / (nseg), -1.0 / (nseg))]

        #     # make segmented colormap
        #     mt_seg_bl2wh2rd = colors.ListedColormap(self.clist)

        #     # make bounds so that the middle is white
        #     bounds = np.arange(ckmin - ckstep, ckmax + 2 * ckstep, ckstep)

        #     # normalize the colors
        #     norms = colors.BoundaryNorm(bounds, mt_seg_bl2wh2rd.N)

        #     # make the colorbar
        #     self.cb = mcb.ColorbarBase(
        #         self.ax2,
        #         cmap=mt_seg_bl2wh2rd,
        #         norm=norms,
        #         orientation=self.cb_orientation,
        #         ticks=bounds[1:-1],
        #     )
        # else:
        #     if cmap in list(mtcl.cmapdict.keys()):
        #         cmap_input = mtcl.cmapdict[cmap]
        #     else:
        #         cmap_input = mtcl.cm.get_cmap(cmap)
        #     self.cb = mcb.ColorbarBase(
        #         self.ax2,
        #         cmap=cmap_input,  # mtcl.cmapdict[cmap],
        #         norm=colors.Normalize(vmin=ckmin, vmax=ckmax),
        #         orientation=self.cb_orientation,
        #     )
        # # label the color bar accordingly
        # self.cb.set_label(
        #     mtpl.ckdict[ck], fontdict={"size": self.font_size, "weight": "bold"}
        # )

        # # place the label in the correct location
        # if self.cb_orientation == "horizontal":
        #     self.cb.ax.xaxis.set_label_position("top")
        #     self.cb.ax.xaxis.set_label_coords(0.5, 1.3)
        # elif self.cb_orientation == "vertical":
        #     self.cb.ax.yaxis.set_label_position("right")
        #     self.cb.ax.yaxis.set_label_coords(1.25, 0.5)
        #     self.cb.ax.yaxis.tick_left()
        #     self.cb.ax.tick_params(axis="y", direction="in")
        # # --> add reference ellipse:  (legend of ellipse size=1)
        # # FZ: remove the following section if no show of Phi
        # show_phi = False  # JingMingDuan does not want to show the black circle - it's not useful
        # if show_phi is True:
        #     ref_ellip = patches.Ellipse((0, 0.0), width=es, height=es, angle=0)
        #     ref_ellip.set_facecolor((0, 0, 0))
        #     ref_ax_loc = list(self.ax2.get_position().bounds)
        #     ref_ax_loc[0] *= 0.95
        #     ref_ax_loc[1] -= 0.17
        #     ref_ax_loc[2] = 0.1
        #     ref_ax_loc[3] = 0.1
        #     self.ref_ax = self.fig.add_axes(ref_ax_loc, aspect="equal")
        #     self.ref_ax.add_artist(ref_ellip)
        #     self.ref_ax.set_xlim(-es / 2.0 * 1.05, es / 2.0 * 1.05)
        #     self.ref_ax.set_ylim(-es / 2.0 * 1.05, es / 2.0 * 1.05)
        #     plt.setp(self.ref_ax.xaxis.get_ticklabels(), visible=False)
        #     plt.setp(self.ref_ax.yaxis.get_ticklabels(), visible=False)
        #     self.ref_ax.set_title(r"$\Phi$ = 1")
        # if show:
        #     # always show, and adjust the figure before saving it below. The
        #     # figure size ratio are all different!!
        #     plt.show()
        # # the figure need to be closed (X) then the following code save it to a
        # # file.
        # if save_path is not None:
        #     figfile = self.save_figure(save_path)  # , fig_dpi=300)
        # else:
        #     figfile = None
        # # self.export_params_to_file('E:/tmp')

        # return figfile
