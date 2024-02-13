from flask import Flask
import os

app = Flask(__name__)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def get_api_key():
    if not OPENAI_API_KEY:
        return 'API키 유실'
    else:
        return f'your key is {OPENAI_API_KEY}'

@app.route('/api/speech-to-text')
def convert_stt():
    pass 

if __name__ == '__main__':
    app.run(debug = True)
