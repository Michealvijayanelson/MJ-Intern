from flask import Flask, request, redirect, url_for, render_template
import boto3

app = Flask(__name__)

# Configure S3 client
s3 = boto3.client('s3')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    s3.upload_fileobj(file, 'original-images-bucket', file.filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
