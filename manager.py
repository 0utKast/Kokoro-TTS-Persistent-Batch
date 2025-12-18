import os
import json
import time
import soundfile as sf
import numpy as np
from kokoro_onnx import Kokoro
import io

class BatchManager:
    def __init__(self, projects_dir, model_path, voices_path):
        self.projects_dir = projects_dir
        os.makedirs(self.projects_dir, exist_ok=True)
        
        # Inicializar Kokoro una sola vez
        print(f"Cargando modelo Kokoro desde {model_path}...")
        self.kokoro = Kokoro(model_path, voices_path)
        print("Modelo cargado.")

    def create_project(self, name, chunks, voice, speed, lang):
        project_id = f"{int(time.time())}_{name.replace(' ', '_')}"
        project_path = os.path.join(self.projects_dir, project_id)
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "audio_chunks"), exist_ok=True)

        status = {
            "name": name,
            "voice": voice,
            "speed": speed,
            "lang": lang,
            "total_chunks": len(chunks),
            "completed_chunks": 0,
            "is_finished": False,
            "chunks": [{"id": i, "text": text, "status": "pending"} for i, text in enumerate(chunks)]
        }

        with open(os.path.join(project_path, "status.json"), "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)
        
        return project_id

    def get_projects(self):
        projects = []
        for pid in os.listdir(self.projects_dir):
            status_path = os.path.join(self.projects_dir, pid, "status.json")
            if os.path.exists(status_path):
                with open(status_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["id"] = pid
                    projects.append(data)
        return projects

    def process_next_chunk(self, project_id):
        project_path = os.path.join(self.projects_dir, project_id)
        status_path = os.path.join(project_path, "status.json")
        
        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)

        if status["is_finished"]:
            return None

        # Buscar el primer chunk pendiente
        next_chunk = None
        for chunk in status["chunks"]:
            if chunk["status"] == "pending":
                next_chunk = chunk
                break
        
        if not next_chunk:
            status["is_finished"] = True
            # Intentar ensamblar si todo está listo
            self.assemble_audio(project_id)
            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=4)
            return None

        try:
            # Generar audio
            print(f"Procesando chunk {next_chunk['id']} de {status['total_chunks']}...")
            samples, sample_rate = self.kokoro.create(
                next_chunk["text"], 
                voice=status["voice"], 
                speed=status["speed"], 
                lang=status["lang"]
            )
            
            chunk_filename = f"chunk_{next_chunk['id']}.wav"
            chunk_path = os.path.join(project_path, "audio_chunks", chunk_filename)
            sf.write(chunk_path, samples, sample_rate)
            
            # Actualizar estado
            next_chunk["status"] = "completed"
            status["completed_chunks"] += 1
            
            # Si era el último, marcar como finalizado
            if status["completed_chunks"] == status["total_chunks"]:
                status["is_finished"] = True
                self.assemble_audio(project_id)

            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=4)
                
            return next_chunk["id"]
        except Exception as e:
            print(f"Error procesando chunk {next_chunk['id']}: {e}")
            next_chunk["status"] = "error"
            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=4)
            raise e

    def assemble_audio(self, project_id):
        project_path = os.path.join(self.projects_dir, project_id)
        audio_chunks_dir = os.path.join(project_path, "audio_chunks")
        output_path = os.path.join(project_path, "final_output.wav")
        
        # Cargar el archivo de estado para saber el orden
        status_path = os.path.join(project_path, "status.json")
        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)

        all_data = []
        sample_rate = None
        
        for chunk in status["chunks"]:
            chunk_path = os.path.join(audio_chunks_dir, f"chunk_{chunk['id']}.wav")
            if os.path.exists(chunk_path):
                data, sr = sf.read(chunk_path)
                if sample_rate is None:
                    sample_rate = sr
                all_data.append(data)
        
        if all_data:
            combined = np.concatenate(all_data)
            sf.write(output_path, combined, sample_rate)
            print(f"Audio final ensamblado en: {output_path}")
