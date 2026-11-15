from flask import Flask, render_template, request, jsonify, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from datetime import datetime, timezone
import json, random, secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Development key; use an environment secret in deployment.
ROOT = Path(__file__).resolve().parent
with (ROOT / "intents.json").open(encoding="utf-8") as f:
    INTENTS = json.load(f)["intents"]

PATTERNS, TAGS = [], []
BY_TAG = {item["tag"]: item for item in INTENTS}
for item in INTENTS:
    for pattern in item["patterns"]:
        PATTERNS.append(pattern)
        TAGS.append(item["tag"])

VECTORIZER = TfidfVectorizer(ngram_range=(1, 2))
TRAINING = VECTORIZER.fit_transform(PATTERNS)
FOLLOW_UPS = {
    "when": "For confirmed dates, check your institution's official timetable. I don't have access to its live calendar.",
    "where": "The exact location depends on your campus. Check the official campus map or ask the department office.",
    "how": "I can break that into steps. Which part would you like to start with?",
    "more": "Sure. Which part would you like me to explain in more detail?"
}

def follow_up_kind(text):
    text = text.lower().strip(" ?.!,'")
    if text in {"when", "when is it", "what date"}: return "when"
    if text in {"where", "where is it"}: return "where"
    if text in {"how", "how do i do that"}: return "how"
    if text in {"tell me more", "more details", "explain more"}: return "more"
    return None


def predict_intent(text):
    scores = cosine_similarity(
        VECTORIZER.transform([text]),
        TRAINING
    )[0]

    # Find the highest and second-highest scores
    ranked_indices = scores.argsort()[::-1]

    best_index = ranked_indices[0]
    best_score = float(scores[best_index])
    best_tag = TAGS[best_index]

    second_score = float(scores[ranked_indices[1]])

    print(f"DEBUG: Input={text!r}")
    print(f"DEBUG: Best intent={best_tag}")
    print(f"DEBUG: Best score={best_score:.4f}")
    print(f"DEBUG: Second score={second_score:.4f}")

    # Reject weak matches
    if best_score < 0.35:
        return None, best_score

    # Reject uncertain matches between different intents
    second_tag = TAGS[ranked_indices[1]]

    if best_tag != second_tag and best_score - second_score < 0.05:
        return None, best_score

    return best_tag, best_score



def log_turn(user_text, bot_text, tag):
    row = {"time": datetime.now(timezone.utc).isoformat(),
           "session_id": session.get("sid"), "user": user_text,
           "assistant": bot_text, "intent": tag}
    with (ROOT / "conversation_log.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\\n")

@app.get("/")
def home():
    session.setdefault("sid", secrets.token_hex(8))
    return render_template("index.html")


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_text = str(data.get("message", "")).strip()[:500]

    if not user_text:
        return jsonify(
            reply="Please type a message first.",
            intent=None
        ), 400

    last_intent = session.get("last_intent")
    follow = follow_up_kind(user_text)

    if follow and last_intent:
        tag = last_intent
        reply = FOLLOW_UPS[follow]

    else:
        tag, confidence = predict_intent(user_text)

        if tag is not None:
            reply = random.choice(BY_TAG[tag]["responses"])
            session["last_intent"] = tag

        else:
            tag = None
            reply = (
                "I'm sorry, I couldn't understand your question. "
                "I can help with courses, attendance, exams, library, "
                "placements, scholarships, projects, and study tips. "
                "Could you please rephrase your question?"
            )
            session["last_intent"] = None

    history = session.get("history", [])
    history.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": reply}
    ])

    session["history"] = history[-40:]

    log_turn(user_text, reply, tag)

    return jsonify(reply=reply, intent=tag)


@app.get("/history")
def history():
    return jsonify(session.get("history", []))

@app.post("/clear")
def clear():
    session["history"] = []
    session["last_intent"] = None
    return jsonify(status="cleared")

if __name__ == "__main__":
    app.run(debug=True)
