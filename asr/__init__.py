import uuid

import gevent.monkey
gevent.monkey.patch_all()
import base64
from email.mime.multipart import MIMEMultipart
from email.message import Message
import json
import struct
import os
import requests
from flask import Flask, request, Response, abort
from google.cloud import speech

app = Flask(__name__)

#define your language locale
lang = "en-US"
#AUTH_URL = "0.0.0.0" #server to check for paid user
#API_KEY = os.environ['SPEECH_API_KEY'] #not used by google anymore

# We know gunicorn does this, but it doesn't *say* it does this, so we must signal it manually.
@app.before_request
def handle_chunking():
    request.environ['wsgi.input_terminated'] = 1


def parse_chunks(stream):
    boundary = b'--' + request.headers['content-type'].split(';')[1].split('=')[1].encode('utf-8').strip()  # super lazy/brittle parsing.
    this_frame = b''
    while True:
        content = stream.read(4096)
        this_frame += content
        end = this_frame.find(boundary)
        if end > -1:
            frame = this_frame[:end]
            this_frame = this_frame[end + len(boundary):]
            if frame != b'':
                try:
                    header, content = frame.split(b'\r\n\r\n', 1)
                except ValueError:
                    continue
                yield content[:-2]
        if content == b'':
            print("End of input.")
            break


@app.route('/heartbeat')
def heartbeat():
    return 'asr'

@app.route('/NmspServlet/', methods=["POST"])
def recognise():
    stream = request.stream
    
#no auth and lang was only pulled from the nuance server hostname
    #access_token, lang = request.host.split('.', 1)[0].split('-', 1)

# MAKE FREE
#     auth_req = requests.get(f"{AUTH_URL}/api/v1/me/token", headers={'Authorization': f"Bearer {access_token}"})
#     if not auth_req.ok:
#         abort(401)

    chunks = iter(list(parse_chunks(stream)))
    content = next(chunks).decode('utf-8')

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.SPEEX_WITH_HEADER_BYTE,
        sample_rate_hertz=16000,
        language_code=lang,
        # Enable automatic punctuation
        enable_automatic_punctuation=True,
        max_alternatives=1,
        model="latest_short",
        enable_spoken_punctuation=True,
        enable_spoken_emojis=True
    )

    audio = {
            'content': base64.b64encode(b''.join((struct.pack('B', len(x)) + x for x in chunks))).decode('utf-8')
            }
    
    #old API_KEY method
    #result = requests.post(f'https://speech.googleapis.com/v1/speech:recognize?key={API_KEY}', json=body)
    #result.raise_for_status()
    #use speech library
    client = speech.SpeechClient.from_service_account_json("/code/asr/key.json")
    response = client.recognize(config=config, audio=audio)
 

    words = []
    #updated syntax
    if 'results' in response:
        for result in response.results:
            words.extend({
                    'word': x,
                    'confidence': str(result.alternatives[0].confidence),
                } for x in result.alternatives[0].transcript.split(' '))

    # Now for some reason we also need to give back a mime/multipart message...
    parts = MIMEMultipart()
    response_part = Message()
    response_part.add_header('Content-Type', 'application/JSON; charset=utf-8')

    if len(words) > 0:
        response_part.add_header('Content-Disposition', 'form-data; name="QueryResult"')
        words[0]['word'] += '\\*no-space-before'
        words[0]['word'] = words[0]['word'][0].upper() + words[0]['word'][1:]
        response_part.set_payload(json.dumps({
            'words': [words],
        }))
    else:
        response_part.add_header('Content-Disposition', 'form-data; name="QueryRetry"')
        # Other errors probably exist, but I don't know what they are.
        # This is a Nuance error verbatim.
        response_part.set_payload(json.dumps({
            "Cause": 1,
            "Name": "AUDIO_INFO",
            "Prompt": "Sorry, speech not recognized. Please try again."
        }))
    parts.attach(response_part)

    parts.set_boundary('--Nuance_NMSP_vutc5w1XobDdefsYG3wq')

    response = Response('\r\n' + parts.as_string().split("\n", 3)[3].replace('\n', '\r\n'))
    response.headers['Content-Type'] = f'multipart/form-data; boundary={parts.get_boundary()}'
    return response

