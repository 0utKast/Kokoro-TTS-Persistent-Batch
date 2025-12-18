# Kokoro TTS - Persistent Batch Manager

Una aplicación de Texto-a-Voz (TTS) en local diseñada para procesar documentos largos (como libros completos) con total seguridad y persistencia.

## 🚀 Características
- **Procesamiento Batch**: Olvida el streaming inestable para archivos grandes. Convierte libros enteros fragmento a fragmento.
- **Persistencia Total**: Cada fragmento de audio se guarda inmediatamente. Si la aplicación se cierra o hay un fallo, puedes retomar el trabajo exactamente donde se quedó.
- **Ensamblado Automático**: Una vez completados todos los fragmentos, la aplicación los une automáticamente en un único archivo WAV de alta calidad.
- **Basado en Kokoro-82M**: Utiliza el modelo Kokoro ONNX para una síntesis de voz natural y rápida.
- **Compatible con Python 3.13**: Implementación moderna que evita dependencias obsoletas (como `audioop`).

## 🛠️ Requisitos
- Python 3.9 o superior (Probado en 3.13)
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng/releases) (Necesario para el phonemizer en Windows)
- Modelo `kokoro-v1.0.onnx` y archivo de voces `voices-v1.0.bin` (deben estar en la raíz del proyecto).

## 📦 Instalación
1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Coloca los archivos del modelo (`kokoro-v1.0.onnx`) y de voces (`voices-v1.0.bin`) en la carpeta del proyecto.

## 🏁 Uso
### Windows
Simplemente haz doble clic en `lanzar_batch_app.bat`. Esto iniciará el servidor Flask y abrirá tu navegador en `http://localhost:5001`.

### Manual
1. Inicia el servidor:
   ```bash
   python app.py
   ```
2. Abre tu navegador en `http://localhost:5001`.

## 📂 Estructura del Proyecto
- `app.py`: Servidor Flask y rutas API.
- `manager.py`: Lógica de gestión de proyectos, porcesamiento de audio y ensamblado.
- `processor.py`: Extracción de texto y segmentación inteligente.
- `projects/`: Carpeta donde se guardan los proyectos activos y sus fragmentos.

## ⚖️ Licencia
MIT
