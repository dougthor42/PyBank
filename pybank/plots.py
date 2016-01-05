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
#import sys
#import decimal
#import os.path as osp
#from operator import itemgetter
import random
#from enum import Enum

# Third Party
import wx
import wx.lib.plot as wxplot
import numpy as np

# Package / Application
try:
    # Imports used by unit test runners
    from . import __version__
    from . import utils
    logging.debug("Imports for plots.py complete (Method: UnitTest)")
except SystemError:
    try:
        # Imports used by Spyder
        from __init__ import __version__
        import utils
        logging.debug("Imports for plots.py complete (Method: Spyder IDE)")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import __version__
        from pybank import utils
        logging.debug("Imports for plots.py complete (Method: Executable)")

# ---------------------------------------------------------------------------
### Functions required for Module Constants
# ---------------------------------------------------------------------------
def get_double_click_time():
    """
    Calls the windows API GetDoubleClickTime function

    # TODO: generalize this to all operating systems
        Windows: user32.dll
        Linux: ???
        Mac: ???
    """
    try:
        from ctypes import windll
        a = windll.user32.GetDoubleClickTime()
        return int(a)
    except ImportError:
        return 750

# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
DOUBLE_CLICK_TIME = get_double_click_time()
LEDGER_COLOR_ROW_NEW = wx.Colour(240, 240, 240, 255)
LEDGER_COLOR_ROW_ODD = wx.Colour(255, 255, 255, 255)
LEDGER_COLOR_ROW_EVEN = wx.Colour(255, 255, 204, 255)
LEDGER_COLOR_VALUE_NEGATIVE = wx.Colour(255, 0, 0, 255)
LEDGER_COLOR_VALUE_POSITIVE = wx.Colour(0, 0, 0, 255)
DATABASE = "test_database.db"

# Mouse Buttons
MB_LEFT = 1
MB_MIDDLE = 2
MB_RIGHT = 3

# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------
class wxLinePlot(wxplot.PlotCanvas):
    """
    A Simple line graph with points.

    `data` must be a list, tuple, or numpy array of (x, y) pairs or a list
    of (y1, y2, y3, ..., yn) values. In this case, the x-values are
    assumed to be (1, 2, 3, ..., n)
    """
    # TODO: Add linear fit
    #       +
    def __init__(self, parent, data, *args, **wkargs):
        wxplot.PlotCanvas.__init__(self, parent=parent, size=(400, 300))

        # Then set up how we're presenting the data. Lines? Point? Color?
        # XXX: Note that wxplot.PolyLine has been changed by me!
        line = wxplot.PolyLine(data,
                               colour='red',
                               width=2,
                               drawstyle='steps-post',
                               )

        markers = wxplot.PolyMarker(data,
                                    colour='red',
#                                    width=3,
                                    size=2,
                                    marker='square',
                                    )

        plot = wxplot.PlotGraphics([line, markers],
                                   title="Title",
                                   xLabel="X label",
                                   yLabel="Monies",
                                   )

        self.GridPen = wx.Pen(wx.Colour(230, 230, 230, 255))
        self.EnableGrid = (True, True)
        self.Draw(plot)


        self.canvas.Bind(wx.EVT_LEFT_DOWN, self._on_click)

    def _on_click(self, event):
        print("click")
        pass


    #-- From the old MPL code. Need to modify for wx --#
    def _lin_fit(self):
        """
        Performs a linear regression fit on the data
        """
        linreg = linear_regression(self._xdata, self._ydata)
        slope, intercept, r_value = linreg
        rsq = r_value**2
        return slope, intercept, rsq

    #-- From the old MPL code. Need to modify for wx --#
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


class wxParetoPlot(wxplot.PlotCanvas):
    """
    """
    # TODO: Add events to ParetoPlot, mimicing those I made in MPL.
    #       + On click of a box, highlight it.
    #       + On double-click of a box, break down into subgroups?
    #       + On-Pick event that gets the closest point. This needed?

    def __init__(self, parent, data):
        wxplot.PlotCanvas.__init__(self, parent=parent, size=(400, 300))


        # create the cumulative % data
        counts, categories = calc_pareto_data(data)
        num_categories = len(categories)

        # Fake the cumulative line - make it use the left axis
        cum_line_data = list(zip(np.arange(num_categories),
                                 np.cumsum(np.array(counts)))
                             )


        # Create the bar plots
        # For now, we create them as lines from the x axis up to the point.
        bars = []
        for n, (count, category) in enumerate(zip(counts, categories)):
            pts = [(n, 0), (n, count)]
            ln = wxplot.PolyLine(pts,
                                 colour='green',
#                                 legend='Feb.',
                                 width=20,
                                 )

            bars.append(ln)


        # Create the cumulative data line and pts
        cum_line = wxplot.PolyLine(cum_line_data,
                                   colour='blue',
                                   width=2,
                                   )

        cum_line_pts = wxplot.PolyMarker(cum_line_data,
                                         colour='blue',
                                         width=2,
                                         marker='square',
                                         )

        plot_items = bars + [cum_line, cum_line_pts]

        plot = wxplot.PlotGraphics(plot_items,
                                   title="Pareto",
                                   xLabel="X",
                                   yLabel="Y",
                                   )

        self.GridPen = wx.Pen(wx.Colour(230, 230, 230, 255),
                              1,
                              wx.PENSTYLE_DOT)

        self.EnableGrid = (False, True)
        self.Draw(plot)

    def _draw(self):
        pass

    def draw(data):
        pass


@utils.logged
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


@utils.logged
def calc_pareto_data(data):
    """
    Calculates Pareto data (histogram bins in decending order).

    Parameters:
    -----------
    data : array-like
        1D array of discrete values.

    Returns:
    --------
    counts : array
        The counts for each category, in decending order

    categories : array
        The categories that the data falls in, in decending count order.

    """
    # Get the histogram information
    labels, counts = np.unique(data, return_counts=True)

    # re-order in descending order
    sort_order = np.argsort(counts, kind='heapsort')[::-1]
    counts = counts[sort_order]
    categories = labels[sort_order]

    return counts, categories


def calc_pareto_cum_line(counts):
    """
    Calculates the cumulative line for pareto data
    """
    # create cumulative line data
    line_data = [0.0] * len(counts)
    total_data = float(sum(counts))
    for i, d in enumerate(counts):
        # TODO: this loop seems wonky. Is there a better way?
        if i == 0:
            line_data[i] = d/total_data
        else: line_data[i] = sum(counts[:i + 1])/total_data

    return line_data


def trim_pareto_data(limit, counts, categories, cumulative_data=None):
    """
    Trims pareto data so that counts that are greater than limit% of total
    are kept.

    Note that the 1st point that falls above `limit` is also displayed.

    Parameters:
    -----------
    limit : float
        The cumulative percentage value at which the input data should be
        "chopped off" (must be between 0 and 1 inclusive).

    counts : array-like
        The bin counts for the pareto. Must be the same length as `categories`
        and must be sorted so that `counts[n]` correlates to `categories[n]`.

    categries : array-like
        The category names for the pareto. Must be the same length as `counts`
        and must be sorted so that `categories[n]` correlates to `counts[n]`.

    cumulative_data : array-like
        The cumulative percentages for each bin.
        If `None`, this value will be calculated.

    Returns:
    --------
    counts, categories, cumulative_data : array-like
        each input, trimmed so that any values that have cumulative_data
        greater than limit are excluded.

    """
    if not (0.0 <= limit <= 1.0):
        raise ValueError("Limit must be positive scalar between 0 and 1")

    if cumulative_data is None:
        cumulative_data = calc_pareto_cum_line(counts)

    # trimming
    ltcount = 0
    for _x in cumulative_data:
        if _x < limit:
            ltcount += 1
    limit_loc = range(ltcount + 1)

    counts = [counts[i] for i in limit_loc]
    categories = [categories[i] for i in limit_loc]
    cumulative_data = [cumulative_data[i] for i in limit_loc]

    return counts, categories, cumulative_data


def main():
    # Just some example data and usage
    dlen = 15
    x = np.arange(dlen)
    y = [random.uniform(-1, 1) + _x for _x in x]

    # Example wx App
    app = wx.App()
    frame = wx.Frame(None, size=(1000, 800))

    panel = wx.Panel(frame)

    grid = wx.GridSizer(2, 2, 5, 5)

    # Pareto Data
    labels = ["a", "b", "c", "d", "e", "e", "d", "d", "e", "e", "c"]
    data = [random.choice(labels) for _ in range(100)]
    pareto_data = data

    # Line Plot
    x = np.array([1, 2, 3, 4, 5, 6, 7])
    y = np.array([5, 3, 8, 4, 9, 13, 15])
    data = np.array(list(zip(x, y)))
    plot = wxLinePlot(panel, data)
    grid.Add(plot, 1, wx.EXPAND)

    panel.SetSizer(grid)


    pareto = wxParetoPlot(panel, pareto_data)
    grid.Add(pareto, 1, wx.EXPAND)


    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    random.seed(5633)
    main()
    get_double_click_time()
