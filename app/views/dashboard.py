# Pandas for data management
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8


from flask import render_template

# Using included state data from Bokeh for map
# from https://github.com/bokeh/bokeh/issues/7870
#
# def start_dashboard():
#     # thread_bokeh_server = Thread(target=bokeh_thread)
#
#     session = push_session(dashboard())
#     script = server_session(None, session_id=session.id)
#     return render_template("dmplotter.html", script=script)


def dashboard():

    # Create each of the tabs
    data = pd.DataFrame({'hello': ['world', 'sun']})
    tab1 = test_tab(data)
    tab2 = test_plot()

    # Put all the tabs into one application
    tabs = Tabs(tabs=[tab1, tab2])
    script, div = components(tabs)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    html = render_template(
        'dashboard.html', script=script, div=div, js_resources=js_resources, css_resources=css_resources)
    return encode_utf8(html)


def test_tab(data):
    hello_src = ColumnDataSource(data)
    table_columns = [TableColumn(field='hello', title='Hello')]

    hello_table = DataTable(source=hello_src, columns=table_columns, width=1000)
    return Panel(child=hello_table, title='Test Table')


def test_plot():
    p1 = figure(plot_width=300, plot_height=300)
    p1.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)

    return Panel(child=p1, title="circle")
