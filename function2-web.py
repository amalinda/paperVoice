import functions_framework
from flask import request, send_file, render_template_string
import io
import requests
from pydub import AudioSegment

@functions_framework.http
def text_to_speech(request):
    """HTTP Cloud Function to convert text to speech and provide a download link for the MP3 file.
    Args:
        request (flask.Request): The request object.
    Returns:
        HTML form or downloadable MP3 file.
    """
    # Replace with your OpenAI API key
    api_key = ""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if request.method == 'POST':
        if 'process_text' in request.form:
            # Handle text input
            text = request.form.get('text', '').strip()
            if not text:
                return "No text provided.", 400
            text_to_process = text
            file = None
        elif 'process_file' in request.form:
            # Handle file upload
            file = request.files.get('file')
            if not file or not file.filename.endswith('.txt'):
                return "No file selected or file is not a .txt file.", 400
            text_to_process = file.read().decode('utf-8')
        else:
            return "Invalid request.", 400

        # Define the maximum character limit per API request
        max_length = 4096
        start_index = 0
        audio_segments = []

        # Process text in chunks
        while start_index < len(text_to_process):
            chunk = text_to_process[start_index:start_index + max_length]

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
                return f"Error: {response.status_code} - {response.text}", response.status_code

        # Combine all audio segments into one
        combined_audio = sum(audio_segments)

        # Export the combined audio to a file-like object in MP3 format
        audio_file = io.BytesIO()
        combined_audio.export(audio_file, format="mp3")
        audio_file.seek(0)

        # Serve the audio file for download
        return send_file(
            audio_file,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='converted_speech.mp3'
        )

    else:
        # Serve the HTML form
        html_form = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Upload Text File or Enter Text</title>
        </head>
        <body>
            <h1>Upload a Text File or Enter Text to Convert to Speech</h1>
            <form action="/" method="post" enctype="multipart/form-data">
                <textarea name="text" rows="4" cols="50" placeholder="Enter text here..."></textarea><br>
                <button type="submit" name="process_text">Process Text</button>
                <br><br>
                <input type="file" name="file" accept=".txt"><br>
                <button type="submit" name="process_file">Upload and Process File</button>
            </form>
        </body>
        </html>
        '''
        return render_template_string(html_form)
