from flask import (
    Blueprint, request, jsonify, session, render_template,
    redirect, url_for, flash
)
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User, Progress
from .utils import generate_feedback, get_random_question, get_question_by_id

main = Blueprint('main', __name__)

# ---------------------------------------------------
# AUTHENTICATION ROUTES (FIXED & CLEAN)
# ---------------------------------------------------

@main.route("/sign", methods=["GET", "POST"])
def sign_page():

    if request.method == "POST":
        action = request.form.get("action")

        # -----------------------------------------
        # SIGNUP (CREATE ACCOUNT)
        # -----------------------------------------
        if action == "signup":
            first = request.form.get("first_name")
            last = request.form.get("last_name")
            email = request.form.get("email_signup")
            phone = request.form.get("phone_number")
            birthday = request.form.get("birthday")
            password = request.form.get("password_signup")
            confirm = request.form.get("confirm_password")

            # Validate password match
            if password != confirm:
                return render_template("sign.html", error="Passwords do not match")

            # Check existing user
            if User.query.filter_by(email=email).first():
                return render_template("sign.html", error="Email already exists!")

            # Create user
            user = User(
                first_name=first,
                last_name=last,
                email=email,
                phone_number=phone,
                birthday=birthday,
                password=generate_password_hash(password),
                streak=0,
                total_answers=0,
                points=0
            )
            db.session.add(user)
            db.session.commit()

            # Auto login
            session["user_id"] = user.id
            session["user_name"] = user.first_name

            return redirect(url_for("main.dashboard_page"))

        # -----------------------------------------
        # SIGNIN (LOGIN)
        # -----------------------------------------
        elif action == "signin":
            email = request.form.get("email_login")
            password = request.form.get("password_login")

            user = User.query.filter_by(email=email).first()

            if not user:
                return render_template("sign.html", error="Account does not exist")
            if not check_password_hash(user.password, password):
                return render_template("sign.html", error="Wrong password")
            session["user_id"] = user.id
            session["user_name"] = user.first_name

            return redirect(url_for("main.dashboard_page"))

    return render_template("sign.html")



@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.sign_page"))


# ---------------------------------------------------
# FRONTEND PAGES
# ---------------------------------------------------

@main.route("/")
def home():
    return render_template("base.html")


@main.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("main.sign_page"))

    return render_template("dashboard.html", user_id=session["user_id"])


@main.route("/interview")
def interview_page():
    if "user_id" not in session:
        return redirect(url_for("main.sign_page"))

    return render_template("interview_questions.html")


@main.route("/feedback")
def feedback_page():
    return render_template("feedback.html")


# ---------------------------------------------------
# PROGRESS PAGE (REVIEW RESPONSES)
# ---------------------------------------------------

@main.route("/progress/<int:user_id>")
def progress_page(user_id):
    user = User.query.get(user_id)
    if not user:
        return render_template("review_responses.html", feedback_list=[])

    records = Progress.query.filter_by(user_id=user_id).all()

    feedback_list = []
    for r in records:
        q = get_question_by_id(r.question_id)

        feedback_list.append({
            "question": q["question"] if q else "Unknown",
            "answer": r.answer,
            "feedback": r.feedback_text,
            "score": r.score,
            "sentiment": r.sentiment,
            "keywords": r.keywords,
            "time": r.timestamp.strftime("%Y-%m-%d %H:%M")
        })

    return render_template("review_responses.html", feedback_list=feedback_list)


# ---------------------------------------------------
# API ROUTES
# ---------------------------------------------------

@main.route('/get_question')
def get_question():
    q = get_random_question()

    if not q:
        return jsonify({"status": "error", "message": "No questions available"}), 404

    return jsonify({
        "status": "success",
        "question_id": q["id"],
        "question": q["question"],
        "keywords": q["keywords"]
    })



@main.route("/analyse_answer", methods=["POST"])
def analyse_answer():
    data = request.json
    q = get_question_by_id(data["question_id"])

    result = generate_feedback(q["question"], data["answer"], data["expected_keywords"])

    return jsonify({
        "status": "success",
        "keyword_score": result["keyword_score"],
        "sentiment_score": result["sentiment_score"],
        "final_feedback": result["final_feedback"]
    })


@main.route("/save_progress", methods=["POST"])
def save_progress():
    data = request.json

    user_id = data["user_id"]
    user = User.query.get(user_id)

    progress = Progress(
        user_id=user_id,
        question_id=data["question_id"],
        answer=data["answer"],
        feedback_text=data["final_feedback"],
        score=data["score"],
        sentiment=data["sentiment"],
        keywords=",".join(data["keywords"])
    )

    db.session.add(progress)

    today = date.today().isoformat()

    if user.last_answered != today:
        user.streak += 1
        user.last_answered = today

    user.total_answers += 1
    user.points += int(data["score"])

    db.session.commit()

    return jsonify({"status": "success"})


@main.route("/get_progress/<int:user_id>")
def get_progress_data(user_id):
    user = User.query.get(user_id)
    records = Progress.query.filter_by(user_id=user_id).all()

    return jsonify({
        "status": "success",
        "streak": user.streak,
        "total_answers": user.total_answers,
        "points": user.points,
        "scores": [r.score for r in records],
        "sentiment": [r.sentiment for r in records],
        "keyword_counts": [len(r.keywords.split(",")) for r in records]
    })
