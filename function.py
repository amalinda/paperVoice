import json
import requests
import base64
from pydub import AudioSegment
from flask import jsonify
import io  # Added to use BytesIO for in-memory file handling

def text_to_speech(request):
    # Set your OpenAI API key
    api_key = "YOUR_KEY"
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    request_json = request.get_json(silent=True)
    if request_json and 'text' in request_json:
        text = request_json['text']
    else:
        return jsonify({"error": "Invalid request. Please provide 'text'."}), 400

    # Define the maximum character limit per API request
    max_length = 4096
    start_index = 0
    audio_segments = []

    # Process text in chunks
    while start_index < len(text):
        chunk = text[start_index:start_index + max_length]

        # Define the request payload with the required parameters
        data = {
            "model": "tts-1",
            "input": chunk,
            "voice": "alloy",
            "response_format": "wav",
            "speed": 1.0
        }

        # Make the POST request to the OpenAI API
        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            audio_data = response.content
            # Load the audio data into an AudioSegment
            audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))
            audio_segments.append(audio_segment)
            start_index += max_length
        else:
            return jsonify({"error": f"{response.status_code} - {response.text}"}), response.status_code

    # Combine all audio segments into one
    combined_audio = sum(audio_segments)

    # Export the combined audio to a file-like object in MP3 format
    audio_file = io.BytesIO()
    combined_audio.export(audio_file, format="mp3")
    audio_file.seek(0)

    # Encode the audio file in base64 to return it
    encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

    return jsonify({'audio': encoded_audio}), 200
