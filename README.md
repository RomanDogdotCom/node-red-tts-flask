# 🔊 Node-RED Text-to-Speech System with Flask TTS API

This project enables fast, dynamic text-to-speech (TTS) generation in Node-RED using a Flask-based Python server running Coqui TTS models. It converts text to `.wav`, then to `.mp3`, stores output to disk, and supports real-time use cases.

---

## ✅ Features

- 🌐 Flask HTTP API for fast, in-memory TTS generation  
- ⚡ Converts to MP3 using FFmpeg via Node-RED  
- 📁 Saves audio files to disk (exposed via static directory)  
- 🔁 Cleans up old files automatically  
- 🖥️ Auto-starts on Raspberry Pi using systemd  
- 🧠 Model loaded once at boot for ultra-fast responses  
- 🔄 Node-RED handles full flow: text → wav → mp3 → filename  

---

## 🧱 System Overview

```text
[Node-RED] --> POST /synthesize --> [Flask TTS API] --> tts_xxxx.wav
                 |                                      ↓
                 |--> run ffmpeg to create mp3          tts_xxxx.mp3
                 ↓
        (file cleanup & extraction of filename)
```

---

## 📦 Requirements

- Node-RED (any recent version)
- Python 3.9+ (use a virtual environment)
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- FFmpeg
- Raspberry Pi or other Linux system

---

## 🔧 Setup

### 1. Create Python Virtual Environment

```bash
python3 -m venv /home/pi/tts-venv
source /home/pi/tts-venv/bin/activate
pip install TTS Flask
```

### 2. `tts_server.py`

Save this to `/home/pi/.node-red/scripts/tts_server.py`

```python
from flask import Flask, request, jsonify  # Web framework and JSON handling
from TTS.api import TTS                   # Coqui TTS API
import uuid                               # For generating unique filenames
import os                                 # For file path handling

# Initialize Flask app
app = Flask(__name__)

# Load the TTS model into memory once (fast startup, persistent use)
tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")

# Directory to save the output audio files
OUTPUT_DIR = "/home/pi/.node-red/static/audio/tts"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure directory exists

# Define the HTTP POST endpoint for synthesis
@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.json
    text = data.get("text", "")  # Extract text from JSON payload
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Generate a unique filename for the output
    filename = f"tts_{uuid.uuid4().hex}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Run the TTS model and save the output to a WAV file
    tts.tts_to_file(text=text, file_path=filepath)

    # Return the path to the generated audio file
    return jsonify({"audio_path": filepath})

# Run the Flask app (only used if manually executed, not by systemd)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
```

---

### 3. Create systemd Service

Save as `/etc/systemd/system/tts-server.service`

```ini
[Unit]
Description=Flask TTS Server
After=network.target

[Service]
ExecStart=/home/pi/tts-venv/bin/python /home/pi/.node-red/scripts/tts_server.py
WorkingDirectory=/home/pi/.node-red/scripts
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tts-server
sudo systemctl start tts-server
```

---

## 🧠 About Models

I'm currently using the tts model: "glow-tts" in this project. It's fast, small, and has decent voice quality.

To change models, update the `model_name` in `tts_server.py`.

Popular alternatives:

| Model Name                                 | Description                                     |
|-------------------------------------------|-------------------------------------------------|
| `tts_models/en/ljspeech/glow-tts`         | Fast, US English, great for real-time use      |
| `tts_models/en/ljspeech/tacotron2-DDC`    | Smoother, slower, better quality               |
| `tts_models/en/vctk/vits`                 | Multi-speaker (UK voices)                      |
| `tts_models/en/multi-dataset/your_tts`    | Multilingual + voice cloning                   |

Browse all models: 👉 https://tts.readthedocs.io/en/latest/models/

---

## 🌐 Node-RED Flow

Inject → HTTP request → FFmpeg → Delete `.wav` → Return `.mp3` filename.

> Requires:
> - `node-red-node-exec`
> - `node-red-contrib-filesystem` (`fs-remove` used for cleanup)

Ensure static files are stored in:

```
~/.node-red/static/audio/tts/
```

---

## 📁 Example Output

```
/home/pi/.node-red/static/audio/tts/
├── tts_abc123.wav
├── tts_abc123.mp3
```

---

## 🙌 Credits

- [Coqui TTS](https://github.com/coqui-ai/TTS)  
- [Node-RED](https://nodered.org)  
- System design, debugging, and deployment: **you** 💪
