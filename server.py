import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from ultralytics.utils import DEFAULT_CFG

from ultralytics import YOLO

app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath('uploads')
DONE_IMAGE_PATH = os.path.abspath('runs')
ALLOWED_EXTENSIONS = {'bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm'}

model = YOLO("yolov8n.pt")
DEFAULT_CFG.save_dir= f""

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', image_path=None, done_image_path=None, error=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('image')
    confidence = float(request.form.get('conf', 0.5))

    if not uploaded_file or uploaded_file.filename == '':
        return render_template('index.html', error="No file selected")

    if not is_allowed_file(uploaded_file.filename):
        return render_template('index.html', error="Invalid file type")

    filename = secure_filename(uploaded_file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(input_path)

    results = model(input_path, conf=confidence, save=True, save_dir=DONE_IMAGE_PATH)

    output_file_with_jpg = os.path.splitext(filename)[0] + '.jpg'

    return render_template(
        'index.html',
        image_path=f'/uploads/{filename}',
        done_image_path=f'/runs/{output_file_with_jpg}',
        error=None
    )

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/runs/<filename>')
def serve_processed_file(filename):
    return send_from_directory(DONE_IMAGE_PATH, filename)

if __name__ == '__main__':
    app.run(debug=True)
