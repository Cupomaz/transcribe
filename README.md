# Whisper Transcription Web App

A Flask-based web application for audio transcription using Whisper.cpp server. Upload audio files through a modern web interface and get instant transcriptions.

## Features

- 🎙️ **Modern Web Interface** - Drag-and-drop file upload with real-time feedback
- 🚀 **Fast Transcription** - Leverages Whisper.cpp server for efficient audio-to-text conversion
- 🐳 **Docker Ready** - Containerized application for easy deployment
- ☸️ **Kubernetes Deployments** - Production-ready K8s manifests included
- 🔄 **CI/CD Pipeline** - Automatic Docker image builds via GitHub Actions
- 📁 **Multiple Formats** - Supports WAV, MP3, OGG, FLAC, M4A, AAC, OPUS, WEBM
- 🔒 **Secure** - Runs as non-root user with resource limits

## Prerequisites

- Python 3.11+
- Running Whisper.cpp server
- Docker (for containerized deployment)
- Kubernetes cluster (for K8s deployment)

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd transcribe
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Whisper server details
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   Open your browser at `http://localhost:5000`

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t whisper-transcribe:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e WHISPER_SERVER=your-whisper-server \
     -e WHISPER_PORT=8080 \
     --name whisper-transcribe \
     whisper-transcribe:latest
   ```

### Kubernetes Deployment

1. **Update the configuration**
   Edit `k8s/deployment.yaml`:
   - Update `WHISPER_SERVER` and `WHISPER_PORT` in the ConfigMap
   - Change the image name to your registry
   - Update the Ingress host to your domain

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

3. **Verify deployment**
   ```bash
   kubectl get pods -l app=whisper-transcribe
   kubectl get svc whisper-transcribe
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_SERVER` | Whisper.cpp server hostname | `localhost` |
| `WHISPER_PORT` | Whisper.cpp server port | `8080` |
| `PORT` | Flask application port | `5000` |
| `UPLOAD_FOLDER` | Temporary upload directory | `/tmp/uploads` |

### Whisper.cpp Server Setup

This application requires a running Whisper.cpp server. To set one up:

```bash
# Clone whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# Build
make

# Download a model
bash ./models/download-ggml-model.sh base

# Run server
./server -m models/ggml-base.bin --host 0.0.0.0 --port 8080
```

## GitHub Actions CI/CD

The repository includes automatic Docker image builds:

1. **Enable GitHub Container Registry**
   - Go to repository Settings → Actions → General
   - Enable "Read and write permissions" for workflows

2. **Push to trigger build**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Images are built for:**
   - Every push to `main` or `develop` branches
   - Every tag matching `v*` (e.g., `v1.0.0`)
   - Pull requests (build only, no push)

4. **Access your images**
   ```
   docker pull ghcr.io/<your-username>/<repo-name>:latest
   ```

## API Endpoints

### `GET /`
Returns the web interface

### `POST /upload`
Upload and transcribe an audio file

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (audio file)

**Response:**
```json
{
  "success": true,
  "transcription": "The transcribed text...",
  "filename": "audio.mp3"
}
```

### `GET /health`
Health check endpoint for monitoring

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
.
├── app.py                          # Flask application
├── templates/
│   └── index.html                  # Web interface
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── k8s/
│   └── deployment.yaml            # Kubernetes manifests
├── .github/
│   └── workflows/
│       └── docker-build.yml       # CI/CD pipeline
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Security Considerations

- Application runs as non-root user (UID 1000)
- File size limit: 100MB
- Temporary files are cleaned up after processing
- Resource limits enforced in Kubernetes
- Health checks for container orchestration

## Troubleshooting

### Cannot connect to Whisper server
- Verify Whisper server is running: `curl http://whisper-server:8080/`
- Check environment variables are set correctly
- Ensure network connectivity between services

### File upload fails
- Check file size (max 100MB)
- Verify file format is supported
- Check server logs for errors

### Kubernetes pod not starting
```bash
kubectl logs -l app=whisper-transcribe
kubectl describe pod -l app=whisper-transcribe
```

## Development

### Running tests
```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest
```

### Building locally with Docker Buildx
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t whisper-transcribe:latest .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license here]

## Acknowledgments

- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Fast inference of OpenAI's Whisper
- [Flask](https://flask.palletsprojects.com/) - Lightweight WSGI web application framework
