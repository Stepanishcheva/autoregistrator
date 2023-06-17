import os
import registrator.main
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


@app.route('/process', methods=['POST'])
def process():
    date = request.form['dateValue']
    number = request.form['numberValue']
    label_image = ''
    file_path = upload_file()
    result_path = registrator.main.process(file_path, '', label_image, date, number)
    return send_file(result_path)


def upload_file():
    if 'file' not in request.files:
        return ''

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return ''

    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    file.save('uploads/' + file.filename)
    return 'uploads/' + file.filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
