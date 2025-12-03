import nltk
import random
import string

from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ---------------------------------------------------
# DOWNLOAD REQUIRED NLTK DATA (fixes punkt_tab error)
# ---------------------------------------------------
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)  # <--- IMPORTANT FIX
nltk.download("stopwords", quiet=True)
nltk.download("vader_lexicon", quiet=True)

# Initialize tools
sia = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words("english"))

# ---------------------------------------------------
# QUESTION BANK (General + HR + Company-specific)
# ---------------------------------------------------
QUESTION_BANK = [
    # General Technical
    {"id": "g1", "question": "Explain the difference between lists and tuples in Python.", "keywords": ["list", "tuple", "mutable"]},
    {"id": "g2", "question": "What is a REST API and how does it work?", "keywords": ["rest", "api", "endpoint", "http"]},
    {"id": "g3", "question": "Explain OOP concepts with examples.", "keywords": ["oop", "inheritance", "polymorphism", "encapsulation"]},

    # HR Questions
    {"id": "hr1", "question": "Tell me about yourself.", "keywords": ["background", "experience", "strength"]},
    {"id": "hr2", "question": "What are your strengths and weaknesses?", "keywords": ["strength", "weakness"]},

    # Company-specific
    {"id": "a1", "question": "Explain how Netflix recommends movies using ML.", "keywords": ["recommendation", "algorithm", "machine learning"]},
    {"id": "a2", "question": "How does Google use PageRank?", "keywords": ["pagerank", "google", "ranking"]},
    {"id": "a3", "question": "How does Amazon handle large-scale database systems?", "keywords": ["distributed", "database", "scalability"]},

    # Additional
    {"id": "g4", "question": "Explain how hashing works.", "keywords": ["hash", "map", "collision"]},
    {"id": "g5", "question": "What is multithreading?", "keywords": ["thread", "parallel", "concurrency"]},
]


# ---------------------------------------------------
# CLEAN TEXT FUNCTION
# ---------------------------------------------------
def clean_text(text):
    text = text.lower()
    text = "".join([c for c in text if c not in string.punctuation])
    words = word_tokenize(text)
    words = [w for w in words if w not in stop_words]
    return words


# ---------------------------------------------------
# SENTIMENT ANALYSIS SCORE (confidence)
# ---------------------------------------------------
def get_sentiment_score(text):
    score = sia.polarity_scores(text)
    return score["compound"]   # -1 to +1


# ---------------------------------------------------
# KEYWORD MATCHING SCORE
# ---------------------------------------------------
def keyword_score(answer, required_keywords):
    words = clean_text(answer)

    matched = 0
    for kw in required_keywords:
        if kw.lower() in words:
            matched += 1

    if len(required_keywords) == 0:
        return 0

    return round((matched / len(required_keywords)) * 10, 2)  # score /10


# ---------------------------------------------------
# FULL FEEDBACK GENERATOR
# ---------------------------------------------------
def generate_feedback(question, answer, required_keywords):
    kscore = keyword_score(answer, required_keywords)
    sscore = get_sentiment_score(answer)

    feedback = []
    feedback.append(f"Keyword Score: {kscore}/10")
    feedback.append(f"Confidence (Sentiment) Score: {round((sscore + 1) * 5, 2)}/10")

    # Additional comments
    if kscore < 5:
        feedback.append("Include more domain-specific keywords in your answer.")
    else:
        feedback.append("Good use of necessary keywords.")

    if sscore < 0:
        feedback.append("Try answering with more confidence.")
    else:
        feedback.append("Your answer reflects good confidence.")

    final_feedback = " | ".join(feedback)

    return {
        "keyword_score": kscore,
        "sentiment_score": sscore,
        "final_feedback": final_feedback
    }


# ---------------------------------------------------
# DAILY BOOSTER — RANDOM QUESTION
# ---------------------------------------------------
def get_random_question():
    return random.choice(QUESTION_BANK)


# ---------------------------------------------------
# GET QUESTION BY ID
# ---------------------------------------------------
def get_question_by_id(q_id):
    for q in QUESTION_BANK:
        if q["id"] == q_id:
            return q
    return None
