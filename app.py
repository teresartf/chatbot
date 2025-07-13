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
    texto = request.form.get('texto', '').strip()
    imagem = request.files.get('imagem')

    # recupera o histórico da conversa
    historico = request.form.get('historico')
    try:
        historico = [] if not historico else json.loads(historico)
    except:
        historico = []

    parts = historico.copy()

    # contexto
    prompt_text = (
        "Você é um assistente especializado em filmes e séries. "
        "Responda apenas perguntas relacionadas a filmes, séries, atores, diretores, gêneros, lançamentos e premiações. "
        "Se a pergunta não for sobre esses temas, informe educadamente que só responde sobre cinema e séries.\n\n"
    )

    # Se enviou texto, adiciona à mensagem de contexto
    if texto:
        prompt_text += f"Pergunta do usuário: {texto}\n"

    # Se enviou imagem, adicionar uma descrição para o assistente
    if imagem:
        try:
            imagem_bytes = imagem.read()
            imagem_b64 = base64.b64encode(imagem_bytes).decode()

            # Adiciona a imagem como parte do contexto para a API
            parts.append({
                "inlineData": {
                    "mimeType": imagem.mimetype,
                    "data": imagem_b64
                }
            })

            prompt_text += (
                "O usuário enviou um pôster de filme/série em anexo. "
                "Analise o pôster para ajudar a responder a pergunta, se possível.\n"
            )
        except Exception as e:
            return jsonify({"resposta": f"Erro ao processar imagem: {e}", "historico": historico})

    # Adiciona o prompt gerado ao contexto da conversa
    parts.append({"text": prompt_text.strip()})

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

        if "candidates" not in data or not data['candidates']:
            return jsonify({
                "resposta": "Erro: a API Gemini não retornou resposta válida.",
                "historico": historico
            })

        resposta = data['candidates'][0]['content']['parts'][0].get('text', 'Sem texto na resposta.')

        # adiciona pergunta (texto e/ou "pôster enviado") e resposta do bot
        novo_historico = historico + []
        if texto:
            novo_historico.append({"text": texto})
        if imagem:
            novo_historico.append({"text": "[Usuário enviou um pôster]"})

        novo_historico.append({"text": resposta})

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
