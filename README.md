# CampusBuddy

A student-support chatbot built with Python Flask, HTML, CSS, JavaScript and TF-IDF intent matching.

## Features
- 12 intents with multiple example utterances and responses.
- TF-IDF vectorization with unigram/bigram features and cosine similarity.
- Similarity threshold and fallback for unknown questions.
- Basic context-aware follow-ups: "when?", "where?", "how?", and "tell me more".
- Modern responsive browser chat interface with quick prompts and clear-chat control.
- Session conversation history and append-only JSONL conversation log.

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
```
Activate:
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows CMD: `.venv\Scripts\activate.bat`
- macOS/Linux: `source .venv/bin/activate`

Install and run:
```bash
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000.

## Intent matching
Each sample phrase in `intents.json` is labeled with an intent. `TfidfVectorizer` converts phrases into vectors. A new message is transformed with the same vectorizer, then cosine similarity finds the closest training phrase. A match is accepted at a similarity score of 0.22 or higher; otherwise, fallback is used. Similarity is a heuristic, not a calibrated probability.

## Context and history
The last recognized intent is kept in the Flask session. Short follow-ups can use this context. Up to 40 message entries are held in the session, and each exchange is appended to `conversation_log.jsonl`.

## Suggested 20-input test
hello; good morning; bye; thank you; what courses are available; degree programs; attendance percentage; how do I check attendance; when are the exams; exam timetable; when? (after exams); library timings; where? (after library); placement opportunities; placement training; available scholarships; scholarship details; suggest an AI project; study tips; tell me a dinosaur joke (fallback).

Record actual outcomes and capture your own screenshots before submission. Do not report tests as passed until you have run them.

## Important
Responses are generic and should not be treated as official college information. Before deployment, use a strong secret from an environment variable, disable debug mode, and protect conversation logs containing user messages.
