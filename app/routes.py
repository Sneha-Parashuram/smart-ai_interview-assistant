from flask import Blueprint, request, jsonify, session
from datetime import datetime, date
from . import db
from .models import User, Progress
from .utils import (
    get_random_question,
    analyse_answer_keywords,
    analyse_sentiment,
    generate_feedback_text
)

main = Blueprint('main', __name__)


# ---------------------------------------------------
# BASIC ROOT ENDPOINT
# ---------------------------------------------------
@main.route('/')
def home():
    return jsonify({"status": "API running", "message": "Smart Interview Assistant Backend"})


# ---------------------------------------------------
# AUTH CHECK (optional use)
# ---------------------------------------------------
@main.before_app_request
def load_user():
    user_id = session.get("user_id")
    if user_id:
        session["user_id"] = user_id


# ---------------------------------------------------
# GET A RANDOM INTERVIEW QUESTION
# ---------------------------------------------------
@main.route('/get_question', methods=['GET'])
def get_question():
    question = get_random_question()
    return jsonify({
        "status": "success",
        "question_id": question["id"],
        "question": question["text"],
        "keywords": question["keywords"]
    })


# ---------------------------------------------------
# DAILY BOOSTER QUESTION
# ---------------------------------------------------
@main.route('/daily_question/<int:user_id>', methods=['GET'])
def daily_question(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    today_str = date.today().isoformat()

    # same question allowed for whole day
    if user.last_answered != today_str:
        # new day → generate a new question
        q = get_random_question()
        session['daily_q'] = q
        return jsonify({
            "status": "new_question",
            "question_id": q["id"],
            "question": q["text"],
            "keywords": q["keywords"]
        })

    # same question
    if 'daily_q' in session:
        q = session['daily_q']
        return jsonify({
            "status": "same_question",
            "question_id": q["id"],
            "question": q["text"],
            "keywords": q["keywords"]
        })

    # fallback
    q = get_random_question()
    session['daily_q'] = q
    return jsonify({
        "status": "new_question",
        "question_id": q["id"],
        "question": q["text"],
        "keywords": q["keywords"]
    })


# ---------------------------------------------------
# ANALYSE ANSWER
# ---------------------------------------------------
@main.route('/analyse_answer', methods=['POST'])
def analyse_answer():
    data = request.json

    answer = data.get("answer", "")
    expected_keywords = data.get("expected_keywords", [])
    question_id = data.get("question_id", "")

    # keyword check
    keyword_score, found_keywords = analyse_answer_keywords(answer, expected_keywords)

    # sentiment
    sentiment_score = analyse_sentiment(answer)

    # feedback text
    feedback = generate_feedback_text(found_keywords, expected_keywords, sentiment_score)

    return jsonify({
        "status": "success",
        "keyword_score": keyword_score,
        "sentiment_score": sentiment_score,
        "keywords_found": found_keywords,
        "feedback": feedback
    })


# ---------------------------------------------------
# SAVE PROGRESS
# ---------------------------------------------------
@main.route('/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    user_id = data.get("user_id")
    question_id = data.get("question_id")
    score = data.get("score")
    sentiment = data.get("sentiment")
    keywords = data.get("keywords")

    if not user_id:
        return jsonify({"status": "error", "message": "No user ID"}), 400

    progress = Progress(
        user_id=user_id,
        question_id=question_id,
        score=score,
        sentiment=sentiment,
        keywords=",".join(keywords)
    )

    db.session.add(progress)
    db.session.commit()

    # update streaks
    user = User.query.get(user_id)
    today_str = date.today().isoformat()

    if user.last_answered != today_str:
        user.streak += 1
        user.last_answered = today_str

    user.total_answers += 1
    user.points += int(score)

    db.session.commit()

    return jsonify({"status": "success", "message": "Progress saved"})


# ---------------------------------------------------
# GET DASHBOARD DATA (for charts)
# ---------------------------------------------------
@main.route('/get_progress/<int:user_id>', methods=['GET'])
def get_progress_data(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    records = Progress.query.filter_by(user_id=user_id).all()

    score_list = []
    sentiment_list = []
    keyword_counts = []

    for r in records:
        score_list.append(r.score)
        sentiment_list.append(r.sentiment)
        keyword_counts.append(len(r.keywords.split(",")) if r.keywords else 0)

    return jsonify({
        "status": "success",
        "streak": user.streak,
        "total_answers": user.total_answers,
        "points": user.points,
        "scores": score_list,
        "sentiment": sentiment_list,
        "keyword_counts": keyword_counts
    })
