# -*- coding: utf-8 -*-
# pylint: disable=E1101, C0330
#   E1101 = Module X has no Y member
"""
Plotting classes and functions used by PyBank.

Created on Thu Jul 23 15:39:23 2015

Usage:
    gui.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import logging
import sys
import decimal
import os.path as osp

# Third Party
import wx
import wx.lib.plot as wxplot
import numpy as np
import matplotlib as mpl
import wxmplot
#from scipy import stats
#import scipy.stats as stats

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

# Package / Application
try:
    # Imports used for unittests
    from . import __init__ as __pybank_init
    from . import pbsql
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import __init__ as __pybank_init
        import pbsql
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import __init__ as __pybank_init
        from pybank import pbsql
        logging.debug("imports for Executable")


### #------------------------------------------------------------------------
### Module Constants
### #------------------------------------------------------------------------

LEDGER_COLOR_ROW_NEW = wx.Colour(240, 240, 240, 255)
LEDGER_COLOR_ROW_ODD = wx.Colour(255, 255, 255, 255)
LEDGER_COLOR_ROW_EVEN = wx.Colour(255, 255, 204, 255)
LEDGER_COLOR_VALUE_NEGATIVE = wx.Colour(255, 0, 0, 255)
LEDGER_COLOR_VALUE_POSITIVE = wx.Colour(0, 0, 0, 255)
DATABASE = "test_database.db"

### #------------------------------------------------------------------------
### wx.lib.plot Plots
### #------------------------------------------------------------------------
class Graph(wxplot.PlotCanvas):
    """
    Base class for all plots.

    Not yet sure what I'm going to put in here...
    """
    def __init__(self, parnet, data):
        wxplot.PlotCanvas.__init__(self,
                                   parent=parent,
                                   size=(400, 400),
                                   )


class VBarPlot(Graph):
    """
    A vertical bar graph
    """
    pass


class LinePlot(wxplot.PlotCanvas):
    """
    A Simple line graph with points.

    `data` must be a list, tuple, or numpy array of (x, y) pairs or a list
    of (y1, y2, y3, ..., yn) values. In this case, the x-values are
    assumed to be (1, 2, 3, ..., n)
    """
    def __init__(self, parent, data, *args, **wkargs):
#        wx.Panel.__init__(self, parent)
        wxplot.PlotCanvas.__init__(self, parent=parent, size=(400, 300))

        # Then set up how we're presenting the data. Lines? Point? Color?
        data = wxplot.PolyMarker(data,
                                 legend="Green Line",
                                 colour='red',
                                 width=4,
                                 size=1,
                                 marker='square',
#                                 style=wx.PENSTYLE_SOLID,
                                 )

        plot = wxplot.PlotGraphics([data],
                                   title="Title",
                                   xLabel="X label",
                                   yLabel="Monies",
                                   )
        self.Draw(plot)


class TimeLinePlot(Graph):
    """
    A specialized LinePlot where the x-values are date or datetime values.
    """
    pass


class ParetoPlot(Graph):
    """
    A specialized VBarPlot where the items in the x axis are ordered by
    their value (descending).
    """
    pass


class LinerRegression(object):
    """
    An linear regression object.

    Attributes:
    -----------
    r : float
        Pearson's correlation coefficient

    rsq : float
        r^2

    slope : float

    intercept : float

    """

def linreg(data):
    """
    Performs a linear regression on `data`.

    Parameters:
    -----------
    data : iterable of (x, y) pairs.

    Returns:
    --------
    LinearRegression object

    """
    pass


### #------------------------------------------------------------------------
### matplotlib Plots
### #------------------------------------------------------------------------


class LinePlot(wxmplot.PlotPanel):
    """
    """
    def __init__(self, parent):
        wxmplot.PlotPanel.__init__(self, parent)
        self.fake_x_data = np.array([1, 2, 3, 4, 5, 6, 7])
        self.fake_y_data = np.array([15, 13.6, 18.8, 12, 2, -6, 25])


        self.scatterplot(self.fake_x_data, self.fake_y_data)


### #------------------------------------------------------------------------
### matplotlib Plots, without using wxmplot
### #------------------------------------------------------------------------

class LinePlot(wx.Panel):
    """
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._data = None

        self._init_ui()

        # Just some example data and usage
        import random
        dlen = 15
        x = np.arange(dlen)
        y = [random.uniform(-1, 1) + _x for _x in x]

        self.draw(x, y)

    def _init_ui(self):
        """
        Initialize the empty plot
        """
        # Create the figure and plot
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)

        # Enable gridlines
        self.axes.minorticks_on()
        self.axes.grid(b=True,              # not sure what this is...
                       which='major',
                       color='0.10',        # black
                       linestyle='-',       # solid line
                       )
        self.axes.grid(b=True,
                       which='minor',
                       color='0.50',        # grey
#                       linestyle='--',     # dashed line (default is dotted)
                       )

        # Create the canvas and add the figure.
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)

        # Set up the layout of the panel.
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Fit()

    def _lin_fit(self):
        """
        Performs a linear regression fit on the data
        """
#        linreg = stats.linregress(self._xdata, self._ydata)
#        slope, intercept, r_value, _, _ = linreg
#        rsq = r_value**2
#        return slope, intercept, rsq

    def _draw_lin_fit(self):
        """
        Draws the line of best fit, extrapolating a few points.
        """
        predict = 3
        slope, intercept, _ = self._lin_fit()
        xstart, xend = np.min(self._xdata) - 1, np.max(self._xdata) + predict
        ystart = (slope * xstart) + intercept
        yend = (slope * xend) + intercept

        xdata = [xstart, xend]
        ydata = [ystart, yend]

        self.axes.plot(xdata, ydata)

    def _draw(self):
        """
        Actually draw the plot items
        """
        # Plot the line
        self.axes.plot(self._xdata, self._ydata, 'r-')
        # and points
        self.axes.plot(self._xdata, self._ydata, 'bo')
        # and the linear regression
#        self._draw_lin_fit()

    def draw(self, xdata, ydata):
        """
        Draw data.

        Parameters:
        -----------
        xdata : array-like
            1D array of [x1, x2, x3, ...] values.

        ydata: array-like
            1D array of [y1, y2, y3, ...] values.
        """
        # convert to numpy arrays if needed
        if not isinstance(xdata, np.ndarray):
            xdata = np.array(xdata)
        if not isinstance(ydata, np.ndarray):
            ydata = np.array(ydata)

        self._xdata = xdata
        self._ydata = ydata
        self._draw()



def main():
    app = wx.App()
    frame = wx.Frame(None, size=(800, 600))
    panel = LinePlot(frame)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
