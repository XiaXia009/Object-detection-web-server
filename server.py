from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
import time
import shutil
import os

app = Flask(__name__)
socketio = SocketIO(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DONE_IMAGE_PATH'] = 'push'
model = YOLO("yolov8n.pt")
str_remove = 'runs\\detect\\'

ALLOWED_EXTENSIONS = {'bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm'}

def remove(path):
    path = path.replace(str_remove, '')
    return path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_output():
    for i in range(10):
        time.sleep(1)  # 模擬長時間運行的工作
        socketio.emit('output', {'data': f'Output {i+1}'})
        
@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(generate_output)

@app.route('/')
def index():
    return render_template('index.html', 
                           image_path=None, 
                           done_image_path=None, 
                           error=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return render_template('index.html',
                               image_path=None,
                               done_image_path=None,
                               error=f"Server: Can't save image")

    file = request.files['image']
    conf_float = float(request.form['conf'])

    if file.filename == '':
        return render_template('index.html', 
                               image_path=None, 
                               done_image_path=None, 
                               error=f"Client: No picture selected")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        results = model(file_path, conf=conf_float, save=True)
        save_dir = results[0].save_dir
        image_path = save_dir+"/"+filename
        destination_path = os.path.join('push', filename)
        if os.path.exists(destination_path):
            shutil.copy2(image_path, destination_path)
        else:
            shutil.move(image_path, 'push', copy_function=shutil.copy2)
        shutil.rmtree('runs\detect')
        return render_template('index.html', 
                               image_path=f'/uploads/{filename}',
                               done_image_path=f'/push/{filename}',
                               error=f"None")

@app.route('/uploads/<filename>')
def uploaded_1(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/push/<filename>')
def uploaded_2(filename):
    return send_from_directory(app.config['DONE_IMAGE_PATH'], filename)

@app.route('/error/<error>')
def error(error):
    return error

if __name__ == '__main__':
    socketio.run(app)
