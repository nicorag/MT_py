# -*- coding: utf-8 -*-
"""
Created on Thu May 30 17:07:50 2013

@author: jpeacock-pr
"""

# ==============================================================================

import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator
from mtpy.imaging.mtplot_tools import PlotBase, plot_pt_lateral, get_log_tick_labels

# reload(mtpl)
# ==============================================================================


class PlotPhaseTensor(PlotBase):
    """
    Will plot phase tensor, strike angle, min and max phase angle,
    azimuth, skew, and ellipticity as subplots on one plot.  It can plot
    the resistivity tensor along side the phase tensor for comparison.


    """

    def __init__(self, pt_object, station=None, **kwargs):
        super().__init__(**kwargs)
        self.pt = pt_object
        self.station = station
        self.skew_cutoff = 3
        self.ellip_cutoff = 0.1

        self.cb_position = (0.045, 0.78, 0.015, 0.12)

        self.subplot_left = 0.1
        self.subplot_right = 0.98
        self.subplot_bottom = 0.1
        self.subplot_top = 0.95
        self.subplot_wspace = 0.21
        self.subplot_hspace = 0.5

        self._set_subplot_params()
        if self.show_plot:
            self.plot()

    def _set_subplot_parameters(self):
        plt.rcParams["font.size"] = self.font_size
        plt.rcParams["figure.subplot.left"] = self.subplot_left
        plt.rcParams["figure.subplot.right"] = self.subplot_right
        plt.rcParams["figure.subplot.bottom"] = self.subplot_bottom
        plt.rcParams["figure.subplot.top"] = self.subplot_top

    def _rotate_pt(self, rotation_angle):
        """

        :param rotation_angle: DESCRIPTION
        :type rotation_angle: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        self.pt.rotate(rotation_angle)

    def _setup_subplots(self):
        self.ax_pt = self.fig.add_subplot(3, 1, 1)
        self.ax_strike = self.fig.add_subplot(3, 2, 3)

    def plot(self, rotation_angle=None):
        """
        plots the phase tensor elements
        """

        if self.x_limits is None:
            self.x_limits = self.set_period_limits(1.0 / self.pt.freq)
        # --> create plot instance
        self.fig = plt.figure(self.fig_num, self.fig_size, dpi=self.fig_dpi)
        plt.clf()
        self._setup_subplots()

        # get phase tensor instance
        if rotation_angle is not None:
            self._rotate_pt(rotation_angle)
        color_array = self.get_pt_color_array(self.pt)

        # -------------plotPhaseTensor-----------------------------------

        self.cbax, self.cbpt, = plot_pt_lateral(
            self.ax_pt,
            self.pt,
            color_array,
            self.ellipse_properties,
            self.fig,
        )

        # ----set axes properties-----------------------------------------------
        # --> set tick labels and limits
        self.ax_pt.set_xlim(np.log10(self.x_limits[0]), np.log10(self.x_limits[1]))

        tklabels, xticks = get_log_tick_labels(self.ax_pt)

        self.ax_pt.set_xticks(xticks)
        self.ax_pt.set_xticklabels(tklabels, fontdict={"size": self.font_size})
        self.ax_pt.set_xlabel("Period (s)", fontdict=self.font_dict)

        # need to reset the x_limits caouse they get reset when calling
        # set_ticks for some reason
        self.ax_pt.set_xlim(np.log10(self.x_limits[0]), np.log10(self.x_limits[1]))
        self.ax_pt.grid(
            True, alpha=0.25, which="major", color=(0.25, 0.25, 0.25), lw=0.25
        )

        plt.setp(self.ax_pt.get_yticklabels(), visible=False)

        self.cbpt.set_label(
            self.cb_label_dict[self.ellipse_colorby],
            fontdict={"size": self.font_size},
        )

        # ---------------plotStrikeAngle-----------------------------------
        # --> set tick labels and limits
        xlimits = (
            np.floor(np.log10(1.0 / self.pt.freq[0])),
            np.ceil(np.log10(1.0 / self.pt.freq[-1])),
        )

        az = self.pt.azimuth
        az_err = self.pt.azimuth_err

        # put the strike into a coordinate system that goes from -90 to 90
        az[np.where(az > 90)] -= 180
        az[np.where(az < -90)] += 180

        stlist = []
        stlabel = []

        # plot phase tensor strike
        ps2 = self.ax_strike.errorbar(
            1.0 / self.pt.freq,
            az,
            marker=self.strike_pt_marker,
            ms=self.marker_size,
            mfc=self.strike_pt_color,
            mec=self.strike_pt_color,
            mew=self.marker_lw,
            ls="none",
            yerr=az_err,
            ecolor=self.strike_pt_color,
            capsize=self.marker_size,
            elinewidth=self.marker_lw,
        )

        stlist.append(ps2[0])
        stlabel.append("PT")

        if self.strike_limits is None:
            self.strike_limits = (-89.99, 89.99)
        self.ax_strike.set_yscale("linear")
        self.ax_strike.set_xscale("log", nonpositive="clip")
        self.ax_strike.set_xlim(xmax=10 ** xlimits[-1], xmin=10 ** xlimits[0])
        self.ax_strike.set_ylim(self.strike_limits)
        self.ax_strike.yaxis.set_major_locator(MultipleLocator(20))
        self.ax_strike.yaxis.set_minor_locator(MultipleLocator(5))
        self.ax_strike.grid(
            True, alpha=0.25, which="both", color=(0.25, 0.25, 0.25), lw=0.25
        )
        self.ax_strike.set_ylabel("Angle (deg)", fontdict=self.font_dict)
        self.ax_strike.set_title("Strike", fontdict=self.font_dict)

        # ---------plot Min & Max Phase-----------------------------------------
        minphi = self.pt.phimin
        minphierr = self.pt.phimin_err
        maxphi = self.pt.phimax
        maxphierr = self.pt.phimax_err

        self.ax3 = self.fig.add_subplot(3, 2, 4, sharex=self.ax_strike)

        ermin = self.ax3.errorbar(
            1.0 / self.pt.freq,
            minphi,
            marker=self.xy_marker,
            ms=self.marker_size,
            mfc="None",
            mec=self.xy_color,
            mew=self.marker_lw,
            ls="None",
            yerr=minphierr,
            ecolor=self.xy_color,
            capsize=self.marker_size,
            elinewidth=self.marker_lw,
        )

        ermax = self.ax3.errorbar(
            1.0 / self.pt.freq,
            maxphi,
            marker=self.yx_marker,
            ms=self.marker_size,
            mfc="None",
            mec=self.yx_color,
            mew=self.marker_lw,
            ls="None",
            yerr=maxphierr,
            ecolor=self.yx_color,
            capsize=self.marker_size,
            elinewidth=self.marker_lw,
        )

        if self.pt_limits is None:
            self.pt_limits = [
                min([self.pt.phimax.min(), self.pt.phimin.min()]) - 3,
                max([self.pt.phimax.max(), self.pt.phimin.max()]) + 3,
            ]
            if self.pt_limits[0] < -10:
                self.pt_limits[0] = -9.9
            if self.pt_limits[1] > 100:
                self.pt_limits[1] = 99.99
        self.ax3.set_xscale("log", nonpositive="clip")
        self.ax3.set_yscale("linear")

        self.ax3.legend(
            (ermin[0], ermax[0]),
            ("$\phi_{min}$", "$\phi_{max}$"),
            loc="lower left",
            markerscale=0.5 * self.marker_size,
            borderaxespad=0.01,
            labelspacing=0.1,
            handletextpad=0.2,
            ncol=2,
            borderpad=0.01,
            columnspacing=0.01,
        )

        leg = plt.gca().get_legend()
        ltext = leg.get_texts()  # all the text.Text instance in the legend
        plt.setp(ltext, fontsize=6.5)  # the legend text fontsize

        self.ax3.set_ylim(self.pt_limits)
        self.ax3.grid(True, alpha=0.25, which="both", color=(0.25, 0.25, 0.25), lw=0.25)

        self.ax3.set_ylabel("Phase (deg)", fontdict=self.font_dict)
        self.ax3.set_title(
            "$\mathbf{\phi_{min}}$ and $\mathbf{\phi_{max}}$", fontdict=self.font_dict
        )

        # -----------------------plotSkew---------------------------------------

        skew = self.pt.beta
        skewerr = self.pt.beta_err

        self.ax4 = self.fig.add_subplot(3, 2, 5, sharex=self.ax_strike)
        erskew = self.ax4.errorbar(
            1.0 / self.pt.freq,
            skew,
            marker=self.skew_marker,
            ms=self.marker_size,
            mfc="None",
            mec=self.skew_color,
            mew=self.marker_lw,
            ls="None",
            yerr=skewerr,
            ecolor=self.skew_color,
            capsize=self.marker_size,
            elinewidth=self.marker_lw,
        )

        # plot lines indicating not 3d
        self.ax4.plot(
            [10 ** xlimits[0], 10 ** xlimits[-1]],
            [self.skew_cutoff, self.skew_cutoff],
            ls="--",
            color=self.skew_color,
            lw=1,
        )

        self.ax4.plot(
            [10 ** xlimits[0], 10 ** xlimits[-1]],
            [-self.skew_cutoff, -self.skew_cutoff],
            ls="--",
            color=self.skew_color,
            lw=1,
        )

        self.ax4.set_xscale("log", nonpositive="clip")
        self.ax4.set_yscale("linear")
        self.ax4.yaxis.set_major_locator(MultipleLocator(self.ellipse_range[2]))

        if self.skew_limits is None:
            self.skew_limits = (-10, 10)
        self.ax4.set_ylim(self.skew_limits)
        self.ax4.grid(True, alpha=0.25, which="both", color=(0.25, 0.25, 0.25), lw=0.25)
        self.ax4.set_xlabel("Period (s)", fontdict=self.font_dict)
        self.ax4.set_ylabel("Skew Angle (deg)", fontdict=self.font_dict)
        self.ax4.set_title("Skew Angle", fontdict=self.font_dict)

        # ----------------------plotEllipticity--------------------------------
        ellipticity = self.pt.ellipticity
        ellipticityerr = self.pt.ellipticity_err

        self.ax5 = self.fig.add_subplot(3, 2, 6, sharex=self.ax_strike)
        erskew = self.ax5.errorbar(
            1.0 / self.pt.freq,
            ellipticity,
            marker=self.det_marker,
            ms=self.marker_size,
            mfc="None",
            mec=self.det_color,
            mew=self.marker_lw,
            ls="None",
            yerr=ellipticityerr,
            ecolor=self.det_color,
            capsize=self.marker_size,
            elinewidth=self.marker_lw,
        )

        # draw a line where the ellipticity is not 2d
        self.ax5.plot(
            [10 ** xlimits[0], 10 ** xlimits[-1]],
            [self.ellip_cutoff, self.ellip_cutoff],
            ls="--",
            color=self.det_color,
            lw=1,
        )

        self.ax5.set_xscale("log", nonpositive="clip")
        self.ax5.set_yscale("linear")

        self.ax5.yaxis.set_major_locator(MultipleLocator(0.1))

        self.ax5.set_ylim(ymin=0, ymax=1)
        self.ax5.grid(True, alpha=0.25, which="both", color=(0.25, 0.25, 0.25), lw=0.25)
        self.ax5.set_xlabel("Period (s)", fontdict=self.font_dict)
        self.ax5.set_ylabel(
            "$\mathbf{\phi_{max}-\phi_{min}/\phi_{max}+\phi_{min}}$",
            fontdict=self.font_dict,
        )
        self.ax5.set_title("Ellipticity", fontdict=self.font_dict)

        try:
            self.fig.suptitle(
                "Phase Tensor Elements for: " + self.station,
                fontdict={"size": self.font_size + 3, "weight": "bold"},
            )
        except:
            self.fig.suptitle(
                'Phase Tensor Elements for Station "unknown"',
                fontdict={"size": self.font_size + 3, "weight": "bold"},
            )
