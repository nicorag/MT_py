# -*- coding: utf-8 -*-
"""
===========
mtplottools
===========

Contains helper functions and classes for plotting



@author: jpeacock-pr
"""
# ==============================================================================

import numpy as np

# import mtpy.core.mt
from mtpy.core import mt
import mtpy.core.z as mtz
import mtpy.utils.exceptions as mtex
import mtpy.utils.gis_tools as gis_tools
import matplotlib.mlab as mlab

# ==============================================================================


# define text formating for plotting


# ==============================================================================
# Arrows properties for induction vectors
# ==============================================================================
class MTArrows(object):
    """
    Helper class to read a dictionary of arrow properties
    
    Arguments:
    -----------
        **arrow_dict** : dictionary for arrow properties
                        * 'size' : float
                                  multiplier to scale the arrow. *default* is 5
                        * 'head_length' : float
                                         length of the arrow head *default* is 
                                         1.5
                        * 'head_width' : float
                                        width of the arrow head *default* is 
                                        1.5
                        * 'lw' : float
                                line width of the arrow *default* is .5
                                
                        * 'color' : tuple (real, imaginary)
                                   color of the arrows for real and imaginary
                                   
                        * 'threshold': float
                                      threshold of which any arrow larger than
                                      this number will not be plotted, helps 
                                      clean up if the data is not good. 
                                      *default* is 1, note this is before 
                                      scaling by 'size'
                                      
                        * 'direction : [ 0 | 1 ]
                                     - 0 for arrows to point toward a conductor
                                     - 1 for arrow to point away from conductor
    
    Attributes:
    -----------
    
        -arrow_color_imag     color of imaginary induction arrow
        -arrow_color_real     color of real induction arrow
        -arrow_direction      convention of arrows pointing to or away from 
                              conductors, see above.
        -arrow_head_length    length of arrow head in relative points
        -arrow_head_width     width of arrow head in relative points
        -arrow_lw             line width of arrows
        -arrow_size           scaling factor to multiple arrows by to be visible
        -arrow_threshold      threshold for plotting arrows, anything above 
                              this number will not be plotted.
                              
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.arrow_size = 2.5
        self.arrow_head_length = 0.15 * self.arrow_size
        self.arrow_head_width = 0.1 * self.arrow_size
        self.arrow_lw = 0.5 * self.arrow_size
        self.arrow_threshold = 2
        self.arrow_color_imag = "b"
        self.arrow_color_real = "k"
        self.arrow_direction = 0

        # Set class property values from kwargs and pop them
        for v in vars(self):
            if v in list(kwargs.keys()):
                setattr(self, v, kwargs.pop(v, None))

    def _read_arrow_dict(self, arrow_dict):

        for key in list(arrow_dict.keys()):
            setattr(self, key, arrow_dict[key])


# ==============================================================================
#  ellipse properties
# ==============================================================================
class MTEllipse(object):
    """
    helper class for getting ellipse properties from an input dictionary
    
    Arguments:
    -------------
        **ellipse_dict** : dictionary
                          dictionary of parameters for the phase tensor 
                          ellipses with keys:
                              
                          * 'size' -> size of ellipse in points 
                                     *default* is .25
                          
                          * 'colorby' : [ 'phimin' | 'phimax' | 'beta' | 
                                    'skew_seg' | 'phidet' | 'ellipticity' ]
                                    
                                    - 'phimin' -> colors by minimum phase
                                    - 'phimax' -> colors by maximum phase
                                    - 'skew' -> colors by skew
                                    - 'skew_seg' -> colors by skew in 
                                                   discrete segments 
                                                   defined by the range
                                    - 'normalized_skew' -> colors by 
                                                    normalized_skew
                                                    see Booker, 2014
                                    - 'normalized_skew_seg' -> colors by 
                                                   normalized_skew
                                                   discrete segments 
                                                   defined by the range
                                    - 'phidet' -> colors by determinant of
                                                 the phase tensor
                                    - 'ellipticity' -> colors by ellipticity
                                    *default* is 'phimin'
                            
                          * 'range' : tuple (min, max, step)
                                     Need to input at least the min and max
                                     and if using 'skew_seg' to plot
                                     discrete values input step as well
                                     *default* depends on 'colorby'
                                     
                          * 'cmap' : [ 'mt_yl2rd' | 'mt_bl2yl2rd' | 
                                       'mt_wh2bl' | 'mt_rd2bl' | 
                                       'mt_bl2wh2rd' | 'mt_seg_bl2wh2rd' | 
                                       'mt_rd2gr2bl']
                                      
                                   - 'mt_yl2rd'       --> yellow to red
                                   - 'mt_bl2yl2rd'    --> blue to yellow to red
                                   - 'mt_wh2bl'       --> white to blue
                                   - 'mt_rd2bl'       --> red to blue
                                   - 'mt_bl2wh2rd'    --> blue to white to red
                                   - 'mt_bl2gr2rd'    --> blue to green to red
                                   - 'mt_rd2gr2bl'    --> red to green to blue
                                   - 'mt_seg_bl2wh2rd' --> discrete blue to 
                                                           white to red
    
    Attributes:
    ------------
    
        -ellipse_cmap         ellipse color map, see above for options
        -ellipse_colorby      parameter to color ellipse by
        -ellipse_range        (min, max, step) values to color ellipses
        -ellipse_size         scaling factor to make ellipses visible
                                                           
                                                           
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.ellipse_size = 2
        self.ellipse_colorby = "phimin"
        self.ellipse_range = (0, 90, 10)
        self.ellipse_cmap = "mt_bl2gr2rd"

        # Set class property values from kwargs and pop them
        for v in vars(self):
            if v in list(kwargs.keys()):
                setattr(self, v, kwargs.pop(v, None))

    def _read_ellipse_dict(self, ellipse_dict):
        """
        read in dictionary and set default values if no entry given
        """
        # check all values are populated:
        default_dict = {
            "size": 2,
            "ellipse_range": [0, 0],
            "ellipse_colorby": "skew",
            "ellipse_cmap": "mt_bl2gr2rd",
        }
        for key in list(default_dict.keys()):
            if key not in list(ellipse_dict.keys()):
                ellipse_dict[key] = default_dict[key]
        # --> set the ellipse properties
        for key in list(ellipse_dict.keys()):
            setattr(self, key, ellipse_dict[key])
        try:
            self.ellipse_range[2]
        except IndexError:
            self.ellipse_range = (self.ellipse_range[0], self.ellipse_range[1], 1)
        # set color ranges
        if (
            self.ellipse_range[0] == self.ellipse_range[1]
        ):  # override default-dict values
            if (
                self.ellipse_colorby == "skew"
                or self.ellipse_colorby == "skew_seg"
                or self.ellipse_colorby == "normalized_skew"
                or self.ellipse_colorby == "normalized_skew_seg"
            ):

                self.ellipse_range = (-9, 9, 3)
            elif self.ellipse_colorby == "ellipticity":
                self.ellipse_range = (0, 1, 0.1)
            else:
                self.ellipse_range = (0, 90, 5)
        # end if
        # only one colormap valid for skew_seg at this point in time
        if (
            self.ellipse_colorby == "skew_seg"
            or self.ellipse_colorby == "normalized_skew_seg"
        ):
            print(
                "Updating colormap to mt_seg_bl2wh2rd as this is the only available segmented colormap at this time"
            )
            self.ellipse_cmap = "mt_seg_bl2wh2rd"
        # set colormap to yellow to red
        """
        if self.ellipse_colorby == 'skew' or \
                        self.ellipse_colorby == 'normalized_skew':
            self.ellipse_cmap = 'mt_bl2wh2rd'

        elif self.ellipse_colorby == 'skew_seg' or \
                        self.ellipse_colorby == 'normalized_skew_seg':
            self.ellipse_cmap = 'mt_seg_bl2wh2rd'

        else:
            self.ellipse_cmap = 'mt_bl2gr2rd'
        """


# ==============================================================================
# Plot settings
# ==============================================================================
class PlotSettings(MTArrows, MTEllipse):
    """
    Hold all the plot settings that one might need
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # figure properties:
        self.fig_num = 1
        self.fig_dpi = 150
        self.fig_size = None

        self.font_size = 7
        self.marker_size = 2.5
        self.marker_lw = 0.75
        self.lw = 1
        self.plot_title = None

        # line styles:
        self.xy_ls = ":"
        self.yx_ls = ":"
        self.det_ls = ":"
        self.skew_ls = ":"
        self.strike_ls = ":"

        # marker styles:
        self.xy_marker = "s"
        self.yx_marker = "o"
        self.det_marker = "v"
        self.skew_marker = "d"
        self.strike_inv_marker = "v"
        self.strike_pt_marker = "^"
        self.strike_tip_marker = ">"

        # marker color styles:
        self.xy_color = (0.25, 0.35, 0.75)
        self.yx_color = (0.75, 0.25, 0.25)
        self.det_color = (0.25, 0.75, 0.25)
        self.skew_color = (0.85, 0.35, 0)
        self.strike_inv_color = (0.2, 0.2, 0.7)
        self.strike_pt_color = (0.7, 0.2, 0.2)
        self.strike_tip_color = (0.2, 0.7, 0.2)

        # marker face color styles:
        self.xy_mfc = (0.25, 0.35, 0.75)
        self.yx_mfc = (0.75, 0.25, 0.25)
        self.det_mfc = (0.25, 0.75, 0.25)
        self.skew_mfc = (0.85, 0.35, 0)
        self.strike_inv_mfc = (0.2, 0.2, 0.7)
        self.strike_pt_mfc = (0.7, 0.2, 0.2)
        self.strike_tip_mfc = (0.2, 0.7, 0.2)

        # plot limits
        self.x_limits = None
        self.res_limits = None
        self.phase_limits = None
        self.tipper_limits = None
        self.strike_limits = None
        self.skew_limits = None
        self.pt_limits = None

        # Set class property values from kwargs and pop them
        for v in vars(self):
            if v in list(kwargs.keys()):
                setattr(self, v, kwargs.pop(v, None))
        self.cb_label_dict = {
            "phiminang": r"$\Phi_{min}$ (deg)",
            "phimin": r"$\Phi_{min}$ (deg)",
            "phimaxang": r"$\Phi_{max}$ (deg)",
            "phimax": r"$\Phi_{max}$ (deg)",
            "phidet": r"Det{$\Phi$} (deg)",
            "skew": r"Skew (deg)",
            "normalized_skew": r"Normalized Skew (deg)",
            "ellipticity": r"Ellipticity",
            "skew_seg": r"Skew (deg)",
            "normalized_skew_seg": r"Normalized Skew (deg)",
            "geometric_mean": r"$\sqrt{\Phi_{min} \cdot \Phi_{max}}$",
            "strike": r"Azimuth (deg)",
            "azimuth": r"Azimuth (deg)",
        }

        self.period_label_dict = dict(
            [(ii, "$10^{" + str(ii) + "}$") for ii in range(-20, 21)]
        )


# ==============================================================================
# grid data onto a map view
# ==============================================================================
def grid_data(data_array, x, y, nx=None, ny=None):
    """
    Project data onto a regular grid for plotting.
    
    
    Arguments:
    -----------
        **data_array**: np.ndarray (len(x), len(y))
                        array of data values to be gridded
                        
        **x**: np.ndarray(len(x))
               array of values that coorespond  
    
        **nx**: int
                number of cells in the x-direction.  If none, 2 times the 
                number of x components
                
        **ny**: int
                number of cells in the x-direction.  If none, 2 times the 
                number of y components
                
    Returns:
    ---------
        **grid_array**: np.ndarray(nx, ny)
                        array of data set on a regular grid
        
        **xg**: np.ndarray(nx, ny)
                array of x-grid values
                
        **yg**: np.ndarray(nx, ny)
                array of y-grid values
                
        
    """

    if nx is None:
        nx = 2 * len(x)
    if ny is None:
        ny = 2 * len(y)
    # create evenly spaced intervals to grid over
    xi = np.linspace(x.min(), x.max(), num=nx, endpoint=True)
    yi = np.linspace(y.min(), y.max(), num=ny, endpoint=True)

    xg, yg = np.meshgrid(xi, yi)

    grid_array = mlab.griddata(x, y, data_array, xg, yg)

    return grid_array, xg, yg


# ==============================================================================
# function for writing values to file
# ==============================================================================
def make_value_str(
    value,
    value_list=None,
    spacing="{0:^8}",
    value_format="{0: .2f}",
    append=False,
    add=False,
):
    """
    helper function for writing values to a file, takes in a value and either
    appends or adds value to value_list according to the spacing and format of 
    the string.
    
    Arguments:
    ----------
        **value** : float
        
        **value_list** : list of values converted to strings
        
        **spacing** : spacing of the string that the value will be converted
                      to.
                      
        **value_format** : format of the string that the value is being 
                            coverted to.
        
        **append** : [ True | False]
                     if True then appends the value to value list
        
        **add** : [ True | False ]
                  if True adds value string to the other value strings in
                  value_list
    
    Returns:
    --------
        **value_list** : the input value_list with the new value either 
                        added or appended.
        or
        
        **value_str** : value string if add and append are false
    """

    value_str = spacing.format(value_format.format(value))

    if append is True:
        value_list.append(value_str)
        return value_list
    if add is True:
        value_list += value_str
        return value_list
    if append == False and add == False:
        return value_str
    return value_list


# ==============================================================================
# function for error bar plots
# ==============================================================================
def plot_errorbar(
    ax,
    x_array,
    y_array,
    y_error=None,
    x_error=None,
    color="k",
    marker="x",
    ms=2,
    ls=":",
    lw=1,
    e_capsize=2,
    e_capthick=0.5,
    picker=None,
):
    """
    convinience function to make an error bar instance
    
    Arguments:
    ------------
        **ax** : matplotlib.axes instance 
                 axes to put error bar plot on
    
        **x_array** : np.ndarray(nx)
                      array of x values to plot
                      
        **y_array** : np.ndarray(nx)
                      array of y values to plot
                      
        **y_error** : np.ndarray(nx)
                      array of errors in y-direction to plot
        
        **x_error** : np.ndarray(ns)
                      array of error in x-direction to plot
                      
        **color** : string or (r, g, b)
                    color of marker, line and error bar
                    
        **marker** : string
                     marker type to plot data as
                     
        **ms** : float
                 size of marker
                 
        **ls** : string
                 line style between markers
                 
        **lw** : float
                 width of line between markers
        
        **e_capsize** : float
                        size of error bar cap
        
        **e_capthick** : float
                         thickness of error bar cap
        
        **picker** : float
                     radius in points to be able to pick a point. 
        
        
    Returns:
    ---------
        **errorbar_object** : matplotlib.Axes.errorbar 
                              error bar object containing line data, 
                              errorbars, etc.
    """
    # this is to make sure error bars plot in full and not just a dashed line
    if x_error is not None:
        #        x_err_high = np.array(x_error)
        #        x_err_low = np.array(x_err_high)
        #        x_err_low[x_err_high>=x_array] = x_array[x_err_high>=x_array]*.9999
        #        x_err = [x_err_low, x_err_high]
        x_err = x_error
    else:
        x_err = None
    if y_error is not None:
        #        y_err_high = np.array(y_error)
        #        y_err_low = np.array(y_err_high)
        #        y_err_low[y_err_high>=y_array] = y_array[y_err_high>=y_array]*.9999
        #        y_err = [y_err_low, y_err_high]
        y_err = y_error
    else:
        y_err = None
    errorbar_object = ax.errorbar(
        x_array,
        y_array,
        marker=marker,
        ms=ms,
        mfc="None",
        mew=lw,
        mec=color,
        ls=ls,
        xerr=x_err,
        yerr=y_err,
        ecolor=color,
        color=color,
        picker=picker,
        lw=lw,
        elinewidth=lw,
        capsize=e_capsize,
        #                                  capthick=e_capthick
    )
    return errorbar_object
