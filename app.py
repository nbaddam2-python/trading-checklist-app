from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_PATH = "checklists.db"

PREMARKET_QUESTIONS = [
    "Did you check overnight global market news?",
    "Have you reviewed SPX/QQQ futures and premarket action?",
    "Did you check today’s economic calendar/events?",
    "Have you identified trending sectors and stocks?",
    "Checked for earnings, splits, or other stock-specific news?",
]

PRETRADE_QUESTIONS = [
    "Is your setup clearly defined and confirmed?",
    "Is the trade aligned with overall market and sector trend?",
    "Have you set your stop-loss and target?",
    "Is the position size appropriate for your risk?",
    "Are you emotionally neutral and focused?",
]

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checklist_type TEXT,
                date TEXT,
                responses TEXT
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        checklist_type = request.form['type']
        questions = PREMARKET_QUESTIONS if checklist_type == 'Premarket' else PRETRADE_QUESTIONS
        responses = [request.form.get(f'q{i}', 'no') for i in range(len(questions))]
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO checklists (checklist_type, date, responses) VALUES (?, ?, ?)",
            (checklist_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ';'.join(responses))
        )
        conn.commit()
        conn.close()
        return redirect(url_for('history'))
    return render_template('index.html',
                           premarket_questions=PREMARKET_QUESTIONS,
                           pretrade_questions=PRETRADE_QUESTIONS)

@app.route('/history')
def history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT checklist_type, date, responses FROM checklists ORDER BY date DESC")
    entries = c.fetchall()
    conn.close()
    return render_template('history.html', entries=entries,
                           premarket_questions=PREMARKET_QUESTIONS,
                           pretrade_questions=PRETRADE_QUESTIONS)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)