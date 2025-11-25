import os
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)

# Configuration from environment variables
WHISPER_SERVER = os.getenv('WHISPER_SERVER', 'localhost')
WHISPER_PORT = os.getenv('WHISPER_PORT', '8080')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a', 'aac', 'opus', 'webm'}

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page with file upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and send to Whisper server for transcription."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Send file to Whisper server
        whisper_url = f'http://{WHISPER_SERVER}:{WHISPER_PORT}/inference'
        
        # Detect audio format from file extension
        audio_format = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'wav'
        
        with open(filepath, 'rb') as audio_file:
            files = {'file': (filename, audio_file)}
            data = {
                'temperature': '0.2',
                'response-format': 'json',
                'audio_format': audio_format
            }
            
            response = requests.post(whisper_url, files=files, data=data, timeout=300)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        if response.status_code == 200:
            result = response.json()
            transcription = result.get('text', '')
            return jsonify({
                'success': True,
                'transcription': transcription,
                'filename': filename
            })
        else:
            return jsonify({
                'error': f'Whisper server error: {response.status_code}',
                'details': response.text
            }), 500
            
    except requests.exceptions.RequestException as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({
            'error': 'Failed to connect to Whisper server',
            'details': str(e)
        }), 500
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({
            'error': 'An error occurred during transcription',
            'details': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
