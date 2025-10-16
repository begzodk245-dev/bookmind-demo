import os
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import json, random, csv

# 📁 Bazaga to‘liq yo‘lni aniqlaymiz
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "data", "results.db")

# 🚀 Flask ilovasini yaratamiz
app = Flask(__name__)
os.makedirs("data", exist_ok=True)  # Papkani avtomatik yaratish

# ⚙️ Konfiguratsiya
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔗 SQLAlchemy ulaymiz
db = SQLAlchemy(app)

# Model: Result
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# Savollarni yuklash
def load_questions(category):
    with open(f"questions/{category}.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Bosh sahifa
@app.route('/')
def home():
    return render_template("home.html")

# Test boshlanishi
@app.route('/quiz', methods=['POST'])
def quiz():
    category = request.form.get('category')
    username = request.form.get('username')
    questions = load_questions(category)
    random.shuffle(questions)
    question = questions[0]
    return render_template("quiz.html", question=question, category=category, score=0, qnum=1, username=username)

# Javobni tekshirish
@app.route('/answer', methods=['POST'])
def answer():
    user_answer = int(request.form.get('answer'))
    correct_answer = int(request.form.get('correct'))
    category = request.form.get('category')
    score = int(request.form.get('score'))
    qnum = int(request.form.get('qnum'))
    username = request.form.get('username')

    if user_answer == correct_answer:
        score += 10000

    questions = load_questions(category)
    if qnum < len(questions):
        question = questions[qnum]
        return render_template("quiz.html", question=question, category=category, score=score, qnum=qnum+1, username=username)
    else:
        new_result = Result(username=username, score=score)
        db.session.add(new_result)
        db.session.commit()
        return render_template("final.html", username=username, score=score)

# Natijalar sahifasi
@app.route('/results')
def results():
    data = Result.query.all()
    total_games = len(data)
    top_player = max(data, key=lambda x: x.score) if data else None
    average_score = sum(item.score for item in data) // total_games if total_games > 0 else 0
    return render_template("results.html", results=data, total_games=total_games, top_player=top_player, average_score=average_score)

# CSV eksport
@app.route('/export')
def export_results():
    csv_file = "results.csv"
    data = Result.query.all()
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Ism", "Mukofot (so‘m)"])
        for item in data:
            writer.writerow([item.username, item.score])
    return send_file(csv_file, as_attachment=True)

# Flask serverni ishga tushirish
if __name__ == '__main__':
    print("Flask server ishga tushyapti...")
    # Papkani avtomatik yaratish
    with app.app_context():
        db.create_all()
    app.run(debug=True)