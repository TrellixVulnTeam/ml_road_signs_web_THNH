from rsc_webapp import app
import json, plotly
from flask import render_template, request, redirect, send_from_directory, url_for
from wrangling_scripts.wrangle_data import return_figures
import os
import logging
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

MYDIR = os.path.dirname(__file__)

UPLOAD_FOLDER = MYDIR+'/static/img/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 0.1 * 1024 * 1024 # file size limit: 5MB

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
@app.route('/index')
def index():
    figures = return_figures()

    # plot ids for the html id tag
    ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                           ids=ids,
                           figuresJSON=figuresJSON, 
                           mydir=UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-image', methods=['GET', 'POST'])
def upload_image():
    app.logger.info("/upload-image method:{}, request.files: {}".format(request.method,request.files ))

    if request.method == "POST":
        # check if the post request has the file part
        if 'image' not in request.files:
            app.logger.info('No image uploaded')
            return redirect(request.url)
        file = request.files['image']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            app.logger.info('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('upload_image.html')

    '''
        if request.files:
            image = request.files["image"]
            #image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            image.save('.', image.filename)
            app.logger.info("Image saved: {}".format(image.filename))
            return redirect(request.url)        
    return render_template('upload_image.html')
    '''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return custom HTTP error page."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    error_message = ""
    if e.code==413:
        error_message = "Maximum allowd size is 5MB"
    app.logger.info(str(e.code) + ": " + e.name + ". " + e.description)
    return render_template('error.html',
                           error_code=str(e.code) + ": " + e.name + " " + e.description,
                           error_message=error_message), e.code