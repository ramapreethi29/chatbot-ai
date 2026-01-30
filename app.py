from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
import openai

app = Flask(__name__)

# Configure OpenAI API key from environment variable
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Check if the API key is properly set
if not openai.api_key or openai.api_key.startswith('sk-'):
    print("Warning: OpenAI API key not set. Please configure your OPENAI_API_KEY environment variable.")

# Initialize database
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_message TEXT NOT NULL,
                  bot_response TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Save user message to database
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("INSERT INTO conversations (user_message, bot_response) VALUES (?, ?)", 
              (user_message, ""))
    conn.commit()
    conversation_id = c.lastrowid
    
    # Generate bot response using OpenAI API
    try:
        # Check if API key is properly set
        if not openai.api_key or openai.api_key.startswith('sk-...'):
            raise Exception("OpenAI API key not set. Please configure your API key.")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )

        bot_response = response.choices[0].message['content'].strip()

        # Update the conversation with bot response
        c.execute("UPDATE conversations SET bot_response = ? WHERE id = ?",
                  (bot_response, conversation_id))
        conn.commit()
    except Exception as e:
        bot_response = f"Sorry, I encountered an error: {str(e)}"
        # Still update the conversation with the error message
        c.execute("UPDATE conversations SET bot_response = ? WHERE id = ?",
                  (bot_response, conversation_id))
        conn.commit()
    
    conn.close()
    
    return jsonify({
        'response': bot_response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("SELECT user_message, bot_response, timestamp FROM conversations ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'user_message': row[0],
            'bot_response': row[1],
            'timestamp': row[2]
        })
    
    return jsonify(history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)