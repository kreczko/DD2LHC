import os
from itertools import cycle
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import bokeh
import pandas as pd
from flask import send_from_directory

from plotter import get_figure, get_data, get_datasets, DATA_LOCATION
from forms import DatasetForm, UploadForm

ALLOWED_EXTENSIONS = set(['txt', 'csv', 'dat'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DATA_LOCATION
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 's3cr3t'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def index():
    known_datasets = get_datasets()
    dataset_selection = DatasetForm()
    dataset_selection.datasets.choices = zip(get_datasets(), get_datasets())
    dataset_upload = UploadForm()

    selected_datasets = ['PICOSD_p', 'LHC_2_DD_n', 'mMedmDM1', 'DD_2_LHC_p']

    if request.method == 'POST':
        # check if the post request has the file part
        # print(request.values, request.data, request.form)
        print(dataset_selection.datasets.data)
        if dataset_selection.validate():
            selected_datasets = dataset_selection.datasets.data



    # datasets = ['PICOSD_p', 'LHC_2_DD_n', 'mMedmDM1', 'DD_2_LHC_p']
    datasets = selected_datasets
    dfs = map(get_data, datasets)
    colors = cycle(['red', 'blue', 'green', 'orange'])

    p = figure(
        title='DD2LHC Pico (p, axial)',
        tools='wheel_zoom, pan, save',
        x_axis_label='m_med',
        y_axis_label='m_DM',
        y_axis_type="log",
        plot_width=600,
        plot_height=600,
    )

    for df, color in zip(dfs, colors):
        p.line(df['m_med'], df['m_DM'], line_width=2,
               color=color, legend=df['label'][0])

    all_data = pd.concat(dfs)

    script, div = components(p, CDN)
    return render_template('index.html', plot_script=script, plot_div=div,
                           bokeh_version=bokeh.__version__,
                           data_table=all_data.to_html(),
                           datasets = known_datasets,
                           dataset_selection = dataset_selection,
                           selected_datasets = ', '.join(selected_datasets),
                           dataset_upload = dataset_upload)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        f = form.data_file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename
        ))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000)
