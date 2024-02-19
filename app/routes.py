from flask import Blueprint, request, jsonify
from openai import AsyncOpenAI
import os

import tempfile
import boto3
from werkzeug.utils import secure_filename
from datetime import datetime


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = AsyncOpenAI(
    api_key=os.environ.get(OPENAI_API_KEY),
)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME')
S3_BUCKET_URL = f'https://{S3_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com'

aws_session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
s3_client = aws_session.client(service_name='s3', region_name=AWS_REGION_NAME)
polly_client = aws_session.client(
    service_name='polly', region_name=AWS_REGION_NAME)


api = Blueprint('api', __name__)


@api.route('/api/audiochat/completion')
async def handle_text_to_speech(prompt):
    # test_prompt = 'Hi! My name is Danielle. I will read any text you type here. Hows your condition today?'
    response = polly_client.synthesize_speech(
        Engine='neural',
        Text=prompt,
        OutputFormat='mp3',
        VoiceId='Danielle'
    )

    if 'AudioStream' in response:
        with open('/tmp/output.mp3', 'wb') as file:
            file.write(response['AudioStream'].read())
        s3_file_name = f'output_{datetime.now()}.mp3'
        s3_client.upload_file('/tmp/output.mp3', S3_BUCKET_NAME, s3_file_name)
        print(f"Audio file saved to S3")
    else:
        print("Could not synthesize speech")

    return f'{S3_BUCKET_URL}/{s3_file_name}'


async def handle_chat_completion(user_prompt):
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a native friend."},
                {"role": "system", "content": "Please provide the response in English"},
                {"role": "user", "content": user_prompt},
            ]
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        return {'error': str(e)}


async def handle_speech_to_text(tmp_file_path):
    with open(tmp_file_path, 'rb') as audio_file:
        result = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language='en')
    return result.text


def save_file(audio_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        audio_file.save(tmp_file.name)
        tmp_file_path = tmp_file.name
    return tmp_file_path


@api.route('/')
def get_api_key():
    if not OPENAI_API_KEY:
        return 'API키 유실'
    else:
        return f'your key is {OPENAI_API_KEY}'


@api.route('/users')
def get_users():
    pass


@api.route('/api/audiochat/completion', methods=['POST'])
async def audio_chat_completion_route_handler():
    audio_file = request.files['audioFile']
    tmp_file_path = save_file(audio_file)

    transcribed_text = await handle_speech_to_text(tmp_file_path)
    print('질문', transcribed_text)
    generated_text = await handle_chat_completion(transcribed_text)
    print('대답', generated_text)
    bucket_audio_file_url = await handle_text_to_speech(generated_text)
    return jsonify({'data': bucket_audio_file_url})
