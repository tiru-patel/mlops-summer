# importing dependencies
from prediction import runVideo
import glob
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


app = Flask(__name__)
app.secret_key = "detectform"

ALLOWED_EXTENSIONS = {'mp4'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

BASE_DIR = os.getcwd()
dir = os.path.join(BASE_DIR, "uploads")

for root, dirs, files in os.walk(dir):
    for file in files:
        path = os.path.join(dir, file)
        os.remove(path)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MAIN APP MAKING

# Home Page


@app.route('/')
def index():
    return render_template('index.html')

# Prediction - Vehicle Details Page


@app.route('/cardetails', methods=['POST'])
def upload_file():
    global videoPath
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        videoPath = UPLOAD_FOLDER + "\\" + uploaded_file.filename
        uploaded_file.save(videoPath)

    vehInfo = runVideo(videoPath)
    print(vehInfo)

    # EMPTY UPLOAD FOLDER
    BASE_DIR = os.getcwd()
    dir = os.path.join(BASE_DIR, "uploads")

    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(dir, file)
            os.remove(path)

    carDesc = vehInfo["CarMake"]["CurrentTextValue"]
    carModel = vehInfo["CarModel"]["CurrentTextValue"]
    return render_template("/details.html", carDesc=carDesc, carModel=carModel, vehInfo=vehInfo)
