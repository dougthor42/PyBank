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
#import matplotlib as mpl
#from matplotlib import lines as mpl_lines
#import matplotlib.lines as mpl_lines
from matplotlib.lines import Line2D as mpl_Line2D
#from matplotlib import patches as mpl_patches
#import matplotlib.patches as mpl_patches
from matplotlib.patches import Rectangle as mpl_Rectangle
#import matplotlib.pyplot as plt
#from paretochart import paretochart
#from scipy import stats
#import scipy.stats as stats

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

# Package / Application
try:
    # Imports used for unittests
    from . import pbsql
    from . import utils
    from . import __version__
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import pbsql
        import utils
        from __init__ import __version__
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import pbsql
        from pybank import utils
        from pybank import __version__
        logging.debug("imports for Executable")

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

    from ctypes import windll
    a = windll.user32.GetDoubleClickTime()
    return int(a)

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


# ---------------------------------------------------------------------------
### wx.lib.plot Plots
# ---------------------------------------------------------------------------
class wxLinePlot(wxplot.PlotCanvas):
    """
    A Simple line graph with points.

    `data` must be a list, tuple, or numpy array of (x, y) pairs or a list
    of (y1, y2, y3, ..., yn) values. In this case, the x-values are
    assumed to be (1, 2, 3, ..., n)
    """
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

        self.SetGridColour(wx.Colour(230, 230, 230, 255))
        self.SetEnableGrid(True)
        self.Draw(plot)


        self.canvas.Bind(wx.EVT_LEFT_DOWN, self._on_click)

    def _on_click(self, event):
        print("click")
        pass


class wxParetoPlot(wxplot.PlotCanvas):
    """
    """
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

        self.EnableGrid = True
        self.Draw(plot)

    def _draw(self):
        pass

    def draw(data):
        pass



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
        self.fig = Figure(figsize=(5, 4))
        self.axes = self.fig.add_subplot(111)





        # Create the canvas and add the figure.
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)

        # Set up the layout of the panel.
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Fit()

    def _on_pick(self, event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        print("onpick points: {}  {}".format(xdata[ind], ydata[ind]))

    def _format_axes(self):
        """
        Formats the axes
        """
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
        self.canvas.mpl_connect('pick_event', self._on_pick)

        # Plot the line and points
        p1 = self.axes.plot(self._xdata, self._ydata,
                            color=self._color,
                            linestyle='-',
                            marker='o',
                            drawstyle='steps-mid',
                            picker=5,
                            )
        # and the linear regression
        self._draw_lin_fit()
        self._format_axes()


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

    def clear(self):
        """
        Clears the plot
        """
        self.fig.gca()
        self.axes.cla()
        self.Layout()

class ParetoPlot(wx.Panel):
    """
    Most code taken from Abraham Lee:
        https://github.com/tisimst/paretochart

    Modified to work on numpy arrays of raw data (automatically counts
    each unique element)
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self._data = None           # raw data
        self._cumplot = True        # Plot the cumulative line?
        self._limit = 1.0           # Trim the data

        self._pdata = None          # Pareto data
        self._plabels = None        # Pareto category labels
        self._pcum = None           # Pareto cumulative %age data

        self._init_ui()

#    @property
#    def pdata(self):
#        return _pdata
#
#    @_pdata.setter
#    def pdata(self, value):
#        if self._limit < 1.0:

    def _init_ui(self):
        """
        """
        # Create the figure and plot
        self.fig = Figure(figsize=(5, 4))       # FigSize is in inches :-(
        self.axes = self.fig.add_subplot(111)
        self.ax2 = self.axes.twinx()

        # Create the canvas and add the figure.
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)

        # Set up the layout of the panel.
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(vbox)
        self.Fit()

        self._bind_events()

    ### Events ##############################################################
    def _bind_events(self):
        """
        """
        self.canvas.mpl_connect('button_press_event', self._on_mouse_click)
        self.canvas.mpl_connect('pick_event', self._on_pick)

    def _on_pick(self, event):
        """
        Picking only works on the topmost axis.

        See http://matplotlib.1069221.n5.nabble.com/onpick-on-a-2-y-plot-via-twinx-seems-to-only-allow-picking-of-second-axes-s-artists-td6421.html

        So I need to have the _on_mouse_click event do the check if
        a bar was clicked. >:-(
        """
        print("picked")
        if isinstance(event.artist, mpl_Line2D):
            print("Picked a line")
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print("onpick points: {}  {}".format(xdata[ind], ydata[ind]))
        elif isinstance(event.artist, mpl_Rectangle):
            print("Picked a bar")

    def _on_mouse_click(self, event):
        """
        Handle mouse click events.

        Note that matplotlib does not distinguish between single and double
        clicks. I have to implement that manually via a wx.timer.
        -OR-
        If I make the single-click event something mundane, then I can just
        always process the single-click event. Example would be highlighting
        the item.

        """
        # If we're not in the axes, ignore the event.
        if not event.inaxes:
            return

        # Branch based on double-click and button
        # This prevents the single-click event from firing twice upon
        # double click. However, it does *not* stop the single-click event
        # from firing on the 1st click of the double-click. To stop that,
        # a software debouncer would be needed.
        if event.dblclick:
            if event.button == MB_LEFT:
                self._mouse_click_left_double(event)
            elif event.button == MB_MIDDLE:
                pass
            elif event.button == MB_RIGHT:
                self._mouse_click_right_double(event)
            else:
                return
        else:
            if event.button == MB_LEFT:
                self._mouse_click_left(event)
            elif event.button == MB_MIDDLE:
                pass
            elif event.button == MB_RIGHT:
                self._mouse_click_right(event)
            else:
                return

        # Redraw the figure
        # For some reason, Update() and Refresh() don't work
        self.Layout()


    ### Mouse Click Handlers ################################################
    def _mouse_click_left(self, event):
        """
        Displays the value and changes the color of the bar that was clicked on
        """
        # Revert things back to the default colors
        for item in self.axes.patches:
            item.set_facecolor(None)        # None means default


        # Check if the event happened inside one of the pareto Bars
        in_bar = False
        for n, item in enumerate(self.axes.patches):
            if item.contains(event)[0]:
                bar = item
                bar_num = n
                in_bar = True
                break
        else:
            in_bar = False

        if in_bar:
            lot_str = "Clicked inside bar #{}, value = {}"
            logging.debug(lot_str.format(bar_num, self._pdata[bar_num]))
            bar.set_facecolor('r')

    def _mouse_click_left_double(self, event):
        """
        Super special things.
        """
        logging.debug("Double Left Click")

    def _mouse_click_right(self, event):
        """
        No idea what this should do...
        """
        logging.debug("Right Click")

    def _mouse_click_right_double(self, event):
        """
        No idea what this should do, if anything.
        """
        logging.debug("Double Right Click")

    def _draw_pareto(self):
        """
        Draws and formats the pareto plot.
        """
        # Plot the Pareto
        length = len(self._pdata)
        self.axes.bar(range(length),
                      self._pdata,
                      align='center',
                      picker=10,
                      )

        # Format it
        self.axes.grid()
        self.axes.set_axisbelow(True)

        self.axes.set_xticks(range(length))
        self.axes.set_xlim(-0.5, length - 0.5)
        self.axes.set_xticklabels(self._plabels)

    def _draw_pareto_cum(self, line_data, total_data, limit):
        """
        Draws the pareto cumulative % line.
        """
        # TODO: Clean up this method
        ax2 = self.ax2
        # Add the plot
        x_data = range(len(line_data))

        ax2.plot(x_data,
                 [_x * 100 for _x in line_data],
                 linestyle='--',
                 color='r',
                 marker='o',
                 picker=5,
                 )
        # Adjust the 2nd axis labels.

        # since the sum-total value is not likely to be one of the ticks,
        # we make it the top-most one regardless of label closeness
        self.axes.set_ylim(0, total_data)
        loc = self.axes.get_yticks()
        newloc = [loc[i] for i in range(len(loc)) if loc[i] <= total_data]
        newloc += [total_data]
        self.axes.set_yticks(newloc)
        ax2.set_ylim(0, 100)

        yt = ["{:3d}%".format(int(_x)) for _x in ax2.get_yticks()]
        ax2.set_yticklabels(yt)

        # Add a limit line.
        if limit < 1.0:
            xmin, xmax = self.axes.get_xlim()
            ax2.axhline(limit * 100, xmin - 1, xmax - 1,
                        linestyle='--',
                        color='r',
                        )

    def _draw(self):
        """
        """
        # Create cumulative line data
        self._pcum = calc_pareto_cum_line(self._pdata)

        # Trim the data to the limit
        # TODO: Clean up
        if self._limit < 1:
            (self._pdata,
             self._plabels,
             self._pcum,
             ) = trim_pareto_data(self._limit,
                                  self._pdata,
                                  self._plabels,
                                  self._pcum)

        # Plot the Pareto Bars
        self._draw_pareto()

        # Add the cumulative plot and format it.
        if self._cumplot:
            self._draw_pareto_cum(self._pcum, len(self._data), self._limit)

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
        self._pdata, self._plabels = calc_pareto_data(data)
        self._cumplot = cum_plot
        self._limit = limit

        self._draw()

    @utils.logged
    def clear(self):
        """ """
        self.axes.cla()
        self.ax2.cla()
        self.Layout()


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

    # Line Plot
    plot = LinePlot(panel)
    plot.draw(x, y, 'r')
    plot.clear()
    y = [random.uniform(-1, 1) + _x + 2 for _x in x]
    plot.draw(x, y, 'b')
    y = [random.uniform(-1, 1) + (_x * 0.5) + 2 for _x in reversed(x)]
    plot.draw(x, y, 'g')

    grid.Add(plot, 1, wx.EXPAND)

    # Pareto Plot
    labels = ["a", "b", "c", "d", "e", "e", "d", "d", "e", "e", "c"]
    data = [random.choice(labels) for _ in range(100)]
    pareto_data = data

    plot = ParetoPlot(panel)
    plot.draw(data, True, 0.9991)


    grid.Add(plot, 1, wx.EXPAND)

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
