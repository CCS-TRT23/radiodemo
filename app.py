import os
import uuid
from gtts import gTTS
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

OUTPUT_DIR = os.path.join("static", "audios")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def gerar_roteiro_radio(tipo, empresa, oferta, cidade, tom, duracao, observacoes):
    """
    Protótipo 'IA' simples:
    monta o texto com base em regras e variações.
    Para demo ao chefe, funciona bem e parece um assistente inteligente.
    """

    abertura_map = {
        "animado": "Atenção!",
        "urgente": "Corre que é por tempo limitado!",
        "emocional": "Tem novidade especial pra você.",
        "institucional": "Informação importante."
    }

    fechamento_map = {
        "animado": f"Passe na {empresa} e aproveite.",
        "urgente": "Não deixe para depois.",
        "emocional": "Esperamos você.",
        "institucional": "Contamos com a sua atenção."
    }

    abertura = abertura_map.get(tom, "Atenção!")
    fechamento = fechamento_map.get(tom, f"Passe na {empresa}.")

    if tipo == "promoção":
        roteiro = (
            f"{abertura} "
            f"A {empresa} está com uma oferta especial em {cidade}. "
            f"{oferta}. "
            f"{fechamento}"
        )
    elif tipo == "aviso":
        roteiro = (
            f"{abertura} "
            f"A {empresa} informa: {oferta}. "
            f"Mensagem para o público de {cidade}. "
            f"{fechamento}"
        )
    elif tipo == "vinheta":
        roteiro = (
            f"{empresa}. "
            f"Presença forte em {cidade}. "
            f"{oferta}. "
            f"{fechamento}"
        )
    else:  # institucional
        roteiro = (
            f"{abertura} "
            f"{empresa} comunica ao público de {cidade}: {oferta}. "
            f"{fechamento}"
        )

    if duracao == "15":
        roteiro = roteiro[:180]
    elif duracao == "30":
        roteiro = roteiro[:320]

    if observacoes:
        roteiro += f" Observação: {observacoes}."

    return " ".join(roteiro.split())




def gerar_audio_elevenlabs(texto):
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    tts = gTTS(text=texto, lang="pt")
    tts.save(filepath)

    return f"/static/audios/{filename}"





@app.route("/")
def home():
    return render_template("index.html")


@app.route("/gerar-roteiro", methods=["POST"])
def gerar_roteiro():
    data = request.get_json()

    roteiro = gerar_roteiro_radio(
        tipo=data.get("tipo", "promoção"),
        empresa=data.get("empresa", "").strip(),
        oferta=data.get("oferta", "").strip(),
        cidade=data.get("cidade", "").strip(),
        tom=data.get("tom", "animado"),
        duracao=data.get("duracao", "30"),
        observacoes=data.get("observacoes", "").strip()
    )

    return jsonify({"roteiro": roteiro})


@app.route("/gerar-audio", methods=["POST"])
def gerar_audio():
    data = request.get_json()
    texto = data.get("texto", "").strip()

    if not texto:
        return jsonify({"erro": "Texto vazio"}), 400

    try:
        audio_url = gerar_audio_elevenlabs(texto)
        return jsonify({"audio_url": audio_url})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)