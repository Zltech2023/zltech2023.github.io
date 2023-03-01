from flask import Flask, render_template, request
import requests
from playsound import playsound
import os
import azure.cognitiveservices.speech as speechsdk
import openai
import threading

app = Flask(__name__)

# Text to speech
def speak(text = None):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = "EXAVITQu4vr4xnSDxMaL"
    api_key = '06d79c0cbfc6e9efac3cff4226db4261'

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.75
        }
    }

    headers = {
        "Content-Type": "application/json",
        "xi-api-key" : '06d79c0cbfc6e9efac3cff4226db4261'
    }

    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)

    if response.status_code == 200:

        with open(r'C:\Python projects\spoken_eng_learning\p.mp3', 'wb') as f:
            f.write(response.content)

        playsound(r'C:\Python projects\spoken_eng_learning\p.mp3')
        os.remove(r'C:\Python projects\spoken_eng_learning\p.mp3')

    else:
        print("Request failed with status code:", response)

# Speech to text
def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription='7405ba1964654572b1da70ee9d140478', region='australiaeast')
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("请开始对话")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("你: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    else:
        return "exit."

# Get respond from OpenAI for the chat

openai.api_key = "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"

def ask_openai(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.2,
        max_tokens=25,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response

# For checking the input grammar and logic errors
def check_error_openai(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Correct the grammar and logic errors for the sentence:{prompt}.\
               If you cannot find errors in the sentence, only reply: 'This sentence is error free.'\
               If you found errors, only reply the sentence after correcting.",
        temperature=1,
        max_tokens=20,
        top_p=0.2,
        frequency_penalty=2,
        presence_penalty=2
    )
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    while True:
        speech_recognition_result = recognize_from_microphone()
        user_input = speech_recognition_result

        if user_input.lower() in ("exit.", "quit."):
            print("聊天结束")
            break

        prompt = f"{user_input}"
        response = ask_openai(prompt).choices[0].text.lstrip("\n")

        thread = threading.Thread(target=speak, args=(response,))
        thread.start()

        check_grammar = check_error_openai(prompt).choices[0].text.lstrip("\n")
        print(f"你的伙伴： {response}")
        print(f"语法检查： {check_grammar}")

    return "聊天结束"

if __name__ == "__main__":
    app.run(debug=True)
