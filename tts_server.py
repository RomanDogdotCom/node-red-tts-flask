# Name: tts_server.py
#
# Description: Flask API server for real-time text-to-speech using Coqui TTS.
#              Converts input text to a WAV file, stored locally, for use in Node-RED.
#              Designed to preload model for fast response and run persistently on boot.
#
# Input:
#   POST /synthesize
#   JSON:
#     text - string: input text to convert
#
# Output:
#   JSON:
#     audio_path - string: path to the generated WAV file
#
# REVISIONS:
# 02JUL2025 - Final version, rfesler@gmail.com
# 01JUL2025 - Integrated FFmpeg and cleanup hooks, rfesler@gmail.com
# 31JUN2025 - Initial version, rfesler@gmail.com


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
