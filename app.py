from flask import Flask, json, request, render_template, jsonify
import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    texto = request.form.get('texto', '')
    imagem = request.files.get('imagem')

    # ✅ Recupera o histórico que veio do front
    historico = request.form.get('historico')
    try:
        historico = [] if not historico else json.loads(historico)
    except:
        historico = []

    # ✅ Começa com o histórico anterior (se houver)
    parts = historico.copy()

    # ✅ Adiciona a nova entrada do usuário
    parts.append({
        "text": (
            "Você é um assistente de cinema. "
            "Responda apenas perguntas relacionadas a filmes, diretores, atores, gêneros, lançamentos ou premiações. "
            "Se a pergunta não for sobre cinema, diga que você só responde sobre esse tema. "
            f"A pergunta do usuário é: {texto}"
        )
    })

    # ✅ Se houver imagem, adiciona como parte visual
    if imagem:
        try:
            imagem_bytes = imagem.read()
            imagem_b64 = base64.b64encode(imagem_bytes).decode()
            parts.append({
                "inlineData": {
                    "mimeType": imagem.mimetype,
                    "data": imagem_b64
                }
            })
        except Exception as e:
            return jsonify({"resposta": f"Erro ao processar imagem: {e}", "historico": historico})

    # ✅ Envia tudo como contexto acumulado
    body = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }

    url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(url, headers=headers, params=params, json=body)
        data = response.json()
        print("Resposta bruta da API:", data)

        if "candidates" not in data:
            return jsonify({
                "resposta": "Erro: a API Gemini não retornou candidatos.",
                "historico": historico
            })

        resposta = data['candidates'][0]['content']['parts'][0].get('text', 'Sem texto na resposta.')

        # ✅ Atualiza histórico para enviar de volta
        novo_historico = historico + [{"text": texto}, {"text": resposta}]

        return jsonify({
            "resposta": resposta,
            "historico": novo_historico
        })

    except Exception as e:
        print("Erro:", e)
        return jsonify({
            "resposta": "Erro ao se comunicar com o Gemini.",
            "historico": historico
        })

if __name__ == '__main__':
    app.run(debug=True)
