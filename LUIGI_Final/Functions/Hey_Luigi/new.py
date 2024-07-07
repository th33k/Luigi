import requests

url = "https://api.elevenlabs.io/v1/text-to-speech/VR6AewLTigWG4xSOukaG"

querystring = {"enable_logging": "true"}

payload = {
    "text": "Hello Guys",
    "voice_settings": {
        "use_speaker_boost": True,
        "style": 0.5,
        "similarity_boost": 0.5,
        "stability": 0.5
    },
    "model_id": "eleven_monolingual_v1"
}
headers = {
    "xi-api-key": "sk_1fbcccdd635adc3cf90b823c8151388899642e0fccec35bd",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, params=querystring)

# Save the response content to a file
with open("output_audio.mp3", "wb") as audio_file:
    audio_file.write(response.content)

print("Audio content saved to output_audio.mp3")
