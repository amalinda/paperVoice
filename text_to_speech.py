import requests
import subprocess
import argparse
import base64

# Replace with your Google Cloud Function URL
url = "https://us-central1-.........."

# Argument parser to handle command-line arguments
parser = argparse.ArgumentParser(description='Generate and play or save speech from text.')
parser.add_argument('-input', required=True, help='Specify the input text file.')
parser.add_argument('-output', choices=['mp3', 'speak'], required=True, help='Specify "mp3" to save as output.mp3 or "speak" to play the audio.')

# Parse the arguments
args = parser.parse_args()

# Open the input file for reading
try:
    with open(args.input, "r") as file:
        input_text = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file '{args.input}' was not found.")
    exit(1)

# Prepare the request payload
payload = {
    "text": input_text
}

# Make the POST request to the Google Cloud Function
response = requests.post(url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Decode the base64 audio data
    audio_data = base64.b64decode(response.json()['audio'])

    # Save the audio data to a .mp3 file
    audio_file_path = "output.mp3"
    with open(audio_file_path, "wb") as file:
        file.write(audio_data)
    print("Text-to-speech conversion complete!")

    # Check the output argument to decide action
    if args.output == "mp3":
        print(f"The output is saved as '{audio_file_path}'.")
    elif args.output == "speak":
        # Use Linux native audio player command to play the audio with `play` or `aplay`
        try:
            subprocess.run(["play", audio_file_path], check=True)  # Use "play" command
        except subprocess.CalledProcessError as e:
            print(f"Failed to play audio: {e}")
        except FileNotFoundError:
            print("The 'play' command is not installed or not found. Please install it using 'sudo apt install sox'.")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")

