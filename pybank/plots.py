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
# ----------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import logging
import sys
import decimal
import os.path as osp
from operator import itemgetter
import random

# Third Party
import wx
import wx.lib.plot as wxplot
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import wxmplot
#from paretochart import paretochart
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


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------

LEDGER_COLOR_ROW_NEW = wx.Colour(240, 240, 240, 255)
LEDGER_COLOR_ROW_ODD = wx.Colour(255, 255, 255, 255)
LEDGER_COLOR_ROW_EVEN = wx.Colour(255, 255, 204, 255)
LEDGER_COLOR_VALUE_NEGATIVE = wx.Colour(255, 0, 0, 255)
LEDGER_COLOR_VALUE_POSITIVE = wx.Colour(0, 0, 0, 255)
DATABASE = "test_database.db"


def linear_regression(x, y, rsq=False):
    """
    Calculate a linear regression of X and Y data.

    This function is defined because I cannot seem to get scipy.stats to
    work correctly when freezing the program as an exe with cx_freeze.

    The source code of this function was taken from scipy.stats.linregress
    and modified for my input and output needs.

    Parameters:
    -----------
    x, y : array-like
        Two sets of measurements. Both arrays should have the same length.
        If y is not given, then the function assumes that x is the dependent
        variable and that the independent variable is 1, 2, ... n.

    rsq : boolean
        If True, the return value "r_value" is the Pearson correlation
        coefficient squared.

    Returns:
    --------
    slope : float
        The slope of the best-fit line

    intercept : float
        The y-intercept of the best-fit line

    r_value : float
        Pearson Correlation coefficient or (r_value)^2 if rsq = True

    """

    if y is None:  # assume y = x and x = [0, 1, 2, ..., n]
        y = x
        x = np.arange(len(x))

    xmean = np.mean(x, None)
    ymean = np.mean(y, None)

    # average sum of squares:
    ssxm, ssxym, ssyxm, ssym = np.cov(x, y, bias=1).flat
    r_num = ssxym
    r_den = np.sqrt(ssxm * ssym)
    if r_den == 0.0:
        r = 0.0
    else:
        r = r_num / r_den
        # test for numerical error propagation
        if r > 1.0:
            r = 1.0
        elif r < -1.0:
            r = -1.0

    if rsq:
        r = r**2

    slope = r_num / ssxm
    intercept = ymean - slope*xmean
    r_value = r

    return slope, intercept, r_value


# ---------------------------------------------------------------------------
### wx.lib.plot Plots
# ---------------------------------------------------------------------------
#class LinePlot(wxplot.PlotCanvas):
#    """
#    A Simple line graph with points.
#
#    `data` must be a list, tuple, or numpy array of (x, y) pairs or a list
#    of (y1, y2, y3, ..., yn) values. In this case, the x-values are
#    assumed to be (1, 2, 3, ..., n)
#    """
#    def __init__(self, parent, data, *args, **wkargs):
#        wxplot.PlotCanvas.__init__(self, parent=parent, size=(400, 300))
#
#        # Then set up how we're presenting the data. Lines? Point? Color?
#        data = wxplot.PolyMarker(data,
#                                 legend="Green Line",
#                                 colour='red',
#                                 width=4,
#                                 size=1,
#                                 marker='square',
#                                 )
#
#        plot = wxplot.PlotGraphics([data],
#                                   title="Title",
#                                   xLabel="X label",
#                                   yLabel="Monies",
#                                   )
#        self.Draw(plot)


# ---------------------------------------------------------------------------
### wxmplot Plots
# ---------------------------------------------------------------------------


#class LinePlot(wxmplot.PlotPanel):
#    """
#    """
#    def __init__(self, parent):
#        wxmplot.PlotPanel.__init__(self, parent)
#        self.fake_x_data = np.array([1, 2, 3, 4, 5, 6, 7])
#        self.fake_y_data = np.array([15, 13.6, 18.8, 12, 2, -6, 25])
#
#
#        self.scatterplot(self.fake_x_data, self.fake_y_data)


# ---------------------------------------------------------------------------
### matplotlib Plots, without using wxmplot
# ---------------------------------------------------------------------------

class LinePlot(wx.Panel):
    """
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._xdata = None
        self._ydata = None
        self._color = None

        self._init_ui()

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
        linreg = linear_regression(self._xdata, self._ydata)
        slope, intercept, r_value = linreg
        rsq = r_value**2
        return slope, intercept, rsq

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

        self.axes.plot(xdata, ydata, color=self._color)

    def _draw(self):
        """
        Actually draw the plot items
        """
        # Plot the line and points
        p1 = self.axes.plot(self._xdata, self._ydata,
                            color=self._color,
                            linestyle='-',
                            marker='o',
                            drawstyle='steps-post',
                            )
        # and the linear regression
        self._draw_lin_fit()


    def draw(self, xdata, ydata, color):
        """
        Draw data.

        Parameters:
        -----------
        xdata : array-like
            1D array of [x1, x2, x3, ...] values.

        ydata : array-like
            1D array of [y1, y2, y3, ...] values.

        color : valid MatPlotLib color
            Determines the color of the plotted items. Must be a valid
            matplotlib color.
        """
        # convert to numpy arrays if needed
        if not isinstance(xdata, np.ndarray):
            xdata = np.array(xdata)
        if not isinstance(ydata, np.ndarray):
            ydata = np.array(ydata)

        self._xdata = xdata
        self._ydata = ydata
        self._color = color
        self._draw()

class ParetoPlot(wx.Panel):
    """
    Most code taken from Abraham Lee:
        https://github.com/tisimst/paretochart

    Modified to work on numpy arrays of raw data (automatically counts
    each unique element)
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._init_ui()

    def _init_ui(self):
        """
        """
        # Create the figure and plot
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)

        # Create the canvas and add the figure.
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)

        # Set up the layout of the panel.
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Fit()

    def _draw(self):
        """
        """
        # get counts of unique items
        data = self._data
        labels, counts = np.unique(data, return_counts=True)

        # re-order in descending order
        sort_order = np.argsort(counts, kind='heapsort')[::-1]
        ordered_data = counts[sort_order]
        ordered_labels = labels[sort_order]
        n = len(ordered_data)

        limit = self._limit

        # allow trimming of data (e.g. 'limit=0.95' keeps top 95%)
        if not (0.0 <= limit <= 1.0):
            raise ValueError("Limit must be positive scalar between 0 and 1")

        # create cumulative line data
        line_data = [0.0] * n
        total_data = float(sum(ordered_data))
        for i, d in enumerate(ordered_data):
            # TODO: this loop seems wonky. Is there a better way?
            if i == 0:
                line_data[i] = d/total_data
            else: line_data[i] = sum(ordered_data[:i + 1])/total_data

        # trimming
        ltcount = 0
        for _x in line_data:
            if _x < limit:
                ltcount += 1
        limit_loc = range(ltcount + 1)

        ordered_data = [ordered_data[i] for i in limit_loc]
        ordered_labels = [ordered_labels[i] for i in limit_loc]
        line_data = [line_data[i] for i in limit_loc]

        ax1 = self.axes

        # Plot the Pareto Bars
        ax1.bar(limit_loc,
                ordered_data,
                align='center',
                )

        # Formatting for the Parteo Bars and X axis.
        ax1.grid()
        ax1.set_axisbelow(True)

        ax1.set_xticks(limit_loc)
        ax1.set_xlim(-0.5, len(limit_loc) - 0.5)
        ax1.set_xticklabels(ordered_labels)

        # Add the cumulative plot and format it.
        if self._cumplot:

            ax2 = ax1.twinx()
            # Add the plot
            ax2.plot(limit_loc,
                     [_x * 100 for _x in line_data],
                     linestyle='--',
                     color='r',
                     marker='o',
                     )
            # Adjust the 2nd axis labels.

            # since the sum-total value is not likely to be one of the ticks,
            # we make it the top-most one regardless of label closeness
            ax1.set_ylim(0, total_data)
            loc = ax1.get_yticks()
            newloc = [loc[i] for i in range(len(loc)) if loc[i] <= total_data]
            newloc += [total_data]
            ax1.set_yticks(newloc)
            ax2.set_ylim(0, 100)

            yt = ["{:3d}%".format(int(_x)) for _x in ax2.get_yticks()]
            ax2.set_yticklabels(yt)

            # Add a limit line.
            if limit < 1.0:
                xmin, xmax = ax1.get_xlim()
                ax2.axhline(limit * 100, xmin - 1, xmax - 1,
                            linestyle='--',
                            color='r',
                            )

    def draw(self, data, cum_plot=True, limit=1.0):
        """
        Plots a pareto chart of data.

        Parameters:
        -----------
        data : array-like
            An array of discrete data points.

        cum_plot : boolean
            If True, plots the cumulative distribution of the pareto.

        limit : float
            Must be between 0 and 1 inclusive. Cumulative percentage value
            after which data will not be plotted. Useful for plots with many
            small categories and few large categories.

        Returns:
        --------
        None
        """
        # convert to numpy arrays if needed
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        self._data = data
        self._cumplot = cum_plot
        self._limit = limit

        self._draw()


def main():
    # Just some example data and usage
    dlen = 15
    x = np.arange(dlen)
    y = [random.uniform(-1, 1) + _x for _x in x]

    # Example wx App
    app = wx.App()
    frame = wx.Frame(None, size=(800, 600))

    panel = wx.Panel(frame)

    hbox = wx.BoxSizer(wx.HORIZONTAL)

    # Line Plot
    plot = LinePlot(panel)
    plot.draw(x, y, 'r')
    y = [random.uniform(-1, 1) + _x + 2 for _x in x]
    plot.draw(x, y, 'b')
    y = [random.uniform(-1, 1) + (_x * 0.5) + 2 for _x in reversed(x)]
    plot.draw(x, y, 'g')

    hbox.Add(plot, 0, wx.EXPAND)

    # Pareto Plot
    labels = ["a", "b", "c", "d", "e", "e", "e", "e", "d", "d", "e", "c", "c"]
    data = [random.choice(labels) for _ in range(150)]

    plot = ParetoPlot(panel)
    plot.draw(data)


    hbox.Add(plot, 0, wx.EXPAND)
    panel.SetSizer(hbox)



    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    random.seed(153121)
    main()
