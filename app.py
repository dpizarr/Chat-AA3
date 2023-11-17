from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches
import unidecode

app = Flask(__name__)

def load_certus_p(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)
    return data

def save_certus_p(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def normalize_text(text: str) -> str:
    # Convierte el texto a minúsculas, quita tildes y convierte a Unicode
    normalized = unidecode.unidecode(text.lower())
    return normalized

def find_best_match(user_question: str, questions: list[str]) -> str|None:
    normalized_user_question = normalize_text(user_question)
    
    matches: list = get_close_matches(normalized_user_question, questions, n=1, cutoff=0.6)
    
    return matches[0] if matches else None

def get_answer_for_question(question: str, certus_p: dict) -> str|None:
    for q in certus_p["question"]:
        if normalize_text(q["question"]) == question:
            return q["answer"]
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.form['user_input']

    # cargar la base de conocimiento
    certus_p: dict = load_certus_p('certus_p.json')

    # buscar si existe alguna pregunta relacionada
    best_match: str | None = find_best_match(user_input, [q["question"] for q in certus_p["question"]])

    # si existe: enseñar la pregunta y respuesta
    if best_match:
        answer: str = get_answer_for_question(best_match, certus_p)
        return jsonify({'bot_response': answer})

    # si no existe: responder NO LO SÉ
    else:
        return jsonify({'bot_response': 'No sé la respuesta. ¿Puede enseñármela?'})

if __name__ == '__main__':
    app.run(debug=True)
