<p align="center">
  <img src="https://raw.githubusercontent.com/sonidev-creations/nscet-chatbot/master/static/images/screenshot.png" alt="NSCET Chatbot" width="700"/>
</p>
# 🤖 NSCET Chatbot
<br>
<br>
NSCET Chatbot is a free, open-source assistant built with Python(Flask) for Nadar Saraswathi College of Engineering and Technology. It provides students and staff with instant answers to college-related queries.


---

## Features

- Natural language question & answer
- College-specific knowledge base using `intents.json`
- Chat history saved with **SQLite**
- Voice input support
- Simple and clean web interface

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **AI / NLP:** Groq AI
- **Database:** SQLite (`chat_history.db`)

---

## Project Structure
```
nscet-chatbot/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   │   ├── nscet_logo.png
│   │   └── screenshot.png
│   └── js/
│       └── script.js
├── templates/
├── __pycache__/           
├── .gitignore
├── README.md
├── app.py
├── boost_python.py         
├── chat_history.db
├── chatbot.py
├── intents.json
├── package-lock.json
├── package.json
└── requirements.txt
```

---

## Running Locally

1. Clone the repository:
```bash
git clone https://github.com/your-username/nscet-chatbot.git
cd nscet-chatbot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
python app.py
```

Your app should now be running on **localhost:5000**.

---

## 👨‍💻 Developer

Made with ❤️ by **Soni P**  
📧 iamsoni.btech@gmail.com · 🔗 [LinkedIn](https://www.linkedin.com/in/sonipandian/)
