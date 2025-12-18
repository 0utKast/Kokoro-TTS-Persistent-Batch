import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from processor import TextProcessor
from manager import BatchManager

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROJECTS_FOLDER'] = 'projects'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Rutas globales (apuntando a la carpeta hermana para no duplicar pesos)
MODEL_PATH = "../kokoro-v1.0.onnx"
VOICES_PATH = "../voices-v1.0.bin"

# Ajustar rutas si se ejecuta desde la carpeta batch
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "kokoro-v1.0.onnx"
    VOICES_PATH = "voices-v1.0.bin"

manager = BatchManager(app.config['PROJECTS_FOLDER'], MODEL_PATH, VOICES_PATH)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/voices")
def get_voices():
    # Reutilizar lógica básica o mapeo
    all_voices = manager.kokoro.get_voices()
    voices_data = []
    # Mapeo simplificado para este ejemplo
    for v in all_voices:
        voices_data.append({
            "id": v,
            "label": f"{v.replace('_', ' ').title()}",
            "group": "Español" if v.startswith('e') else "Inglés" if v.startswith('a') or v.startswith('b') else "Otros"
        })
    return jsonify(voices_data)

@app.route("/api/projects")
def get_projects():
    return jsonify(manager.get_projects())

@app.route("/api/create", methods=["POST"])
def create():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    voice = request.form.get('voice', 'es_esteban')
    speed = float(request.form.get('speed', 1.0))
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        text = TextProcessor.extract_text(filepath)
        chunks = TextProcessor.split_into_chunks(text)
        
        # Determinar lang basado en la voz
        lang = "es" if voice.startswith('e') else "en-us"
        
        project_id = manager.create_project(file.filename, chunks, voice, speed, lang)
        return jsonify({"project_id": project_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/api/process/<project_id>", methods=["POST"])
def process(project_id):
    try:
        chunk_id = manager.process_next_chunk(project_id)
        if chunk_id is not None:
            return jsonify({"status": "chunk_done", "chunk_id": chunk_id})
        else:
            return jsonify({"status": "finished"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download/<project_id>")
def download(project_id):
    path = os.path.join(app.config['PROJECTS_FOLDER'], project_id, "final_output.wav")
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Archivo no encontrado", 404

if __name__ == "__main__":
    # Ajustar para que funcione eSpeak NG en Windows si es necesario
    ESPEAK_PATH = r"C:\Program Files\eSpeak NG"
    os.environ["PHONEMIZER_ESPEAK_PATH"] = ESPEAK_PATH
    
    app.run(debug=True, port=5001) # Puerto diferente al original
