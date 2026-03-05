from flask import Flask, request, jsonify, render_template, send_from_directory
from chatbot import get_response, get_chat_history, get_chat_stats
import os

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '').strip()
    if not user_input:
        return jsonify({'response': 'Please say something!', 'source': 'system', 'image': None})
    result = get_response(user_input)
    return jsonify(result)
@app.route('/history', methods=['GET'])
def history():
    rows = get_chat_history(limit=100)
    return jsonify([{
        'user_input':   row[0],
        'bot_response': row[1],
        'source':       row[2],
        'timestamp':    row[3]
    } for row in rows])
@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(get_chat_stats())
@app.route('/clear-history', methods=['POST'])
def clear_history():
    import sqlite3
    try:
        conn = sqlite3.connect('chat_history.db')
        conn.execute('DELETE FROM chat_history')
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Chat history cleared!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
@app.route('/voice', methods=['POST'])
def voice_input():
    try:
        import speech_recognition as sr
        import sounddevice as sd
        import io
        import wave
        recognizer = sr.Recognizer()
        samplerate = 16000
        duration   = 30
    
        print("🎙️ Recording started...")
        recording  = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        print("✅ Recording done!")
        byte_io = io.BytesIO()
        with wave.open(byte_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())
        byte_io.seek(0)
        with sr.AudioFile(byte_io) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language='en-IN')
        print(f"✅ Heard: {text}")
        return jsonify({'status': 'ok', 'text': text})

    except Exception as e:
        err = str(e)
        print(f"❌ Voice error: {err}")
        if 'UnknownValueError' in err or 'understand' in err.lower():
            return jsonify({'status': 'error', 'message': 'Could not understand. Please speak clearly!'})
        elif 'RequestError' in err or 'network' in err.lower():
            return jsonify({'status': 'error', 'message': 'Internet needed for voice. Check connection!'})
        else:
            return jsonify({'status': 'error', 'message': 'Voice error: ' + err[:80]})
@app.route('/mictest')
def mictest():
    return send_from_directory('.', 'mic_test.html')
if __name__ == '__main__':
    app.run(debug=True)