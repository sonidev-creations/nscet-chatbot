import json
import random
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

GROQ_API_KEY = "YOU_GROQ_API_KEY"
groq_client  = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL   = "llama-3.1-8b-instant"

with open('intents.json', 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

intents = data['intents']
def init_db():
    conn = sqlite3.connect('chat_history.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input   TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            source       TEXT DEFAULT 'intent',
            timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_chat(user_input, bot_response, source='intent'):
    try:
        conn = sqlite3.connect('chat_history.db')
        conn.execute(
            'INSERT INTO chat_history (user_input, bot_response, source) VALUES (?, ?, ?)',
            (user_input, bot_response, source)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

def get_chat_history(limit=50):
    try:
        conn   = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_input, bot_response, source, timestamp FROM chat_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        return []

def get_chat_stats():
    try:
        conn   = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chat_history')
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE source='groq'")
        groq_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE source='intent'")
        intent_count = cursor.fetchone()[0]
        conn.close()
        return {'total': total, 'gemini': groq_count, 'intent': intent_count}
    except:
        return {'total': 0, 'gemini': 0, 'intent': 0}

IMAGE_MAP = {
    'cse':                     {'url': '/static/images/cse.jpg',       'label': 'CSE Department'},
    'computer science':        {'url': '/static/images/cse.jpg',       'label': 'CSE Department'},
    'it':                      {'url': '/static/images/it.jpg',        'label': 'IT Department'},
    'information technology':  {'url': '/static/images/it.jpg',        'label': 'IT Department'},
    'ai':                      {'url': '/static/images/aids.jpg',      'label': 'AI & DS Department'},
    'artificial intelligence': {'url': '/static/images/aids.jpg',      'label': 'AI & DS Department'},
    'mechanical':              {'url': '/static/images/mech.jpg',      'label': 'Mechanical Dept'},
    'civil':                   {'url': '/static/images/civil.jpg',     'label': 'Civil Dept'},
    'eee':                     {'url': '/static/images/eee.jpg',       'label': 'EEE Department'},
    'ece':                     {'url': '/static/images/ece.jpg',       'label': 'ECE Department'},
    'campus':                  {'url': '/static/images/campus.jpg',    'label': 'NSCET Campus'},
    'college':                 {'url': '/static/images/campus.jpg',    'label': 'NSCET College'},
    'library':                 {'url': '/static/images/library.jpg',   'label': 'College Library'},
    'lab':                     {'url': '/static/images/lab.jpg',       'label': 'Computer Lab'},
    'hostel':                  {'url': '/static/images/hostel.jpg',    'label': 'Hostel'},
    'canteen':                 {'url': '/static/images/canteen.jpg',   'label': 'Canteen'},
    'sports':                  {'url': '/static/images/sports.jpg',    'label': 'Sports Ground'},
    'placement':               {'url': '/static/images/placement.jpg', 'label': 'Placement Cell'},
}

def get_image_suggestion(user_input):
    lower = user_input.lower()
    for keyword, img_data in IMAGE_MAP.items():
        if keyword in lower:
            return img_data
    return None
def get_reply_length(user_input):
    words = len(user_input.strip().split())
    if words <= 4:
        return 'short'
    elif words <= 10:
        return 'medium'   
    else:
        return 'long'     

def get_word_limit(length):
    if length == 'short':
        return 30
    elif length == 'medium':
        return 60
    else:
        return 100

def get_tfidf_response(user_input):
    patterns  = []
    responses = []

    for intent in intents:
        for pattern in intent['patterns']:
            patterns.append(pattern.lower())
            responses.append(intent['responses'])

    if not patterns:
        return None, 0.0

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix    = vectorizer.fit_transform(patterns + [user_input.lower()])
        user_vector     = tfidf_matrix[-1]
        pattern_vectors = tfidf_matrix[:-1]
        similarities    = cosine_similarity(user_vector, pattern_vectors)[0]
        best_idx        = similarities.argmax()
        best_score      = similarities[best_idx]

        if best_score > 0.35:
            return random.choice(responses[best_idx]), best_score
        return None, best_score
    except:
        return None, 0.0

def enhance_with_groq(user_input, intent_answer):
    length     = get_reply_length(user_input)
    word_limit = get_word_limit(length)

    if length == 'short':
        length_instruction = (
            f"The user asked a SHORT question ({len(user_input.split())} words). "
            f"Give a SHORT reply under {word_limit} words. "
            "Be direct and friendly. No long lists."
        )
    elif length == 'medium':
        length_instruction = (
            f"The user asked a MEDIUM question. "
            f"Give a clear reply under {word_limit} words. "
            "Cover the key points naturally."
        )
    else:
        length_instruction = (
            f"The user asked a DETAILED question. "
            f"Give a complete reply under {word_limit} words. "
            "Cover all important points clearly."
        )

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for NSCET college in Theni, Tamil Nadu. "
                        "Answer in a moderate, friendly and natural tone — not too formal, not too casual. "
                        "Keep ALL facts from the given information. Do not add fake details. "
                        "Use simple English. Add 1 emoji if suitable. "
                        "Never use slang like da, buddy, you know. "
                        f"{length_instruction}"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Student question: {user_input}\n\n"
                        f"College information: {intent_answer}\n\n"
                        f"Answer the question naturally based on the information:"
                    )
                }
            ],
            temperature=0.55,
            max_tokens=200
        )
        result = response.choices[0].message.content.strip()
        return result if result else intent_answer
    except Exception as e:
        print(f"Groq enhance error: {e}")
        return intent_answer
def ask_groq(user_input):
    length     = get_reply_length(user_input)
    word_limit = get_word_limit(length)

    if length == 'short':
        length_instruction = f"Give a SHORT reply under {word_limit} words. Be direct."
    elif length == 'medium':
        length_instruction = f"Give a clear reply under {word_limit} words."
    else:
        length_instruction = f"Give a complete reply under {word_limit} words."

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for NSCET college in Theni, Tamil Nadu, India. "
                        "Answer questions about the college, academics, campus life and general topics. "
                        "Speak in a moderate, friendly and natural tone. "
                        "Use simple English. Add 1 emoji if suitable. "
                        "Never use slang. Never say you are an AI. "
                        f"{length_instruction}"
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.55,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, something went wrong! Please try again. 😊 (Error: {str(e)[:50]})"

def get_response(user_input):
    if not user_input or not user_input.strip():
        return {
            'response': "Please type something! I am here to help. 😊",
            'source':   'system',
            'image':    None
        }

    user_input = user_input.strip()
    image      = get_image_suggestion(user_input)
    intent_text, score = get_tfidf_response(user_input)

    if intent_text:
        enhanced = enhance_with_groq(user_input, intent_text)
        save_chat(user_input, enhanced, source='intent')
        return {
            'response': enhanced,
            'source':   'intent',
            'score':    round(float(score), 2),
            'image':    image
        }
    else:
        groq_response = ask_groq(user_input)
        save_chat(user_input, groq_response, source='groq')
        return {
            'response': groq_response,
            'source':   'gemini',
            'image':    image
        }
init_db()