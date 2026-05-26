# 🧠⚡ AI Exam Assistant — TrampaIngles

Sistema de IA invisible y contextual optimizado para exámenes académicos de inglés (TOEFL, IELTS, Cambridge, Pearson). El asistente utiliza automáticamente lo que **ve** en pantalla y lo que **escucha** por el audio del sistema en tiempo real para proporcionar la respuesta correcta mediante una interfaz flotante discreta.

---

## ✨ Características Principales

*   **👁️ Análisis Visual Inteligente**: Captura la pantalla completa o una región seleccionada para extraer, parsear y resolver preguntas directamente.
*   **🔊 Transcripción de Audio en Vivo (Loopback)**: Captura y transcribe el audio que se reproduce en tus altavoces (como los audios de la sección de *Listening* en exámenes) de forma local utilizando **Faster Whisper** (modelo `tiny` en CPU, optimizado e invisible).
*   **⌨️ Escritura Automática (Autotype)**: Si la respuesta de la IA es una letra (ej: `✅ B`), presionando un atajo de teclado el programa escribirá automáticamente la opción correcta por ti en la casilla activa.
*   **🎭 Interfaz Translúcida e Invisible**: Paneles flotantes oscuros semi-transparentes y discretas "luces de estado" en la esquina inferior de la pantalla para saber cuándo la IA está procesando sin interrumpir tu vista.
*   **💾 Memoria de Contexto Continuo**: Historial de chat y audio integrado que le permite a la IA recordar preguntas anteriores o audios transcribidos para resolver ejercicios secuenciales.
*   **⚙️ Reglas de IA Personalizables**: Personaliza la personalidad de la IA mediante un archivo de instrucciones rápidas (ej: "sé extremadamente breve", "traduce al español").

---

## 🎮 Atajos de Teclado (Hotkeys)

| Hotkey | Acción | Descripción |
| :--- | :--- | :--- |
| `Alt + F` | **Análisis Total** | Toma captura de pantalla completa + transcribe audio reciente + analiza con la IA. |
| `Alt + S` | **Escanear Región** | Permite arrastrar el ratón para seleccionar un área de la pantalla y analizarla. |
| `Alt + T` | **Analizar Texto** | Copia automáticamente el texto que tengas seleccionado y lo envía a la IA. |
| `Alt + I` | **Pregunta Manual** | Abre un cuadro de texto discreto para hacer preguntas directas o dar órdenes. |
| `Alt + V` | **Auto-Escribir** | Escribe automáticamente la letra de la respuesta correcta en la pantalla (A-E). |
| `Alt + A` | **Escuchar Audio** | Activa o desactiva la captura del audio interno del sistema. |
| `Alt + R` | **Mostrar Respuesta** | Muestra u oculta de forma rápida la última respuesta generada por la IA. |
| `Alt + C` | **Limpiar Memoria** | Borra el historial acumulado en la memoria de conversación de la IA. |
| `Alt + H` | **Ver Instrucciones** | Abre el editor para añadir reglas personalizadas sobre cómo debe responder la IA. |
| `Alt + Q` | **Cerrar Programa** | Finaliza y cierra de forma segura la aplicación de fondo. |

---

## ⚙️ Guía de Instalación y Configuración

Sigue estos pasos detallados para configurar el asistente en tu PC o en la de tu amigo:

### 1. Requisitos Previos
Asegúrate de tener instalado **Python 3.10 o superior** en Windows. 
Durante la instalación de Python, asegúrate de marcar la casilla **"Add Python.exe to PATH"**.

### 2. Descargar y Clonar el Proyecto
Descarga el código desde este repositorio de GitHub o clónalo:
```bash
git clone https://github.com/Gueremy/trampaingles.git
cd trampaingles
```

### 3. Instalar Dependencias
Abre la terminal (CMD o PowerShell) **como Administrador** dentro de la carpeta y ejecuta:
```bash
pip install keyboard mss pyperclip pystray pillow faster-whisper soundcard numpy openai
```

---

## 🔑 Cómo Obtener la API Key Recomendada (NVIDIA / Mistral) FREE 🚀

Recomendamos utilizar la API de **NVIDIA NIM** con el modelo **Mistral Medium** (`mistral-medium-3.5-128b`), ya que es **gratuita para desarrolladores**, extremadamente rápida, y ofrece un razonamiento perfecto para exámenes y casos de uso complejos.

1. Ve al portal de desarrolladores de NVIDIA: [build.nvidia.com](https://build.nvidia.com/)
2. Inicia sesión con tu cuenta de NVIDIA (o regístrate gratis).
3. Busca el modelo **`mistral-medium-3.5-128b`** (bajo la sección de Mistral AI).
4. Haz clic en **"Get API Key"** y genera una clave nueva.
5. Copia esa clave (empezará por `nvapi-...`).

---

## 📝 Configuración de Credenciales

1. Entra a la subcarpeta `exam_assistant/`.
2. Busca el archivo plantilla llamado `config.env.example` y **renómbralo a `config.env`**.
3. Abre `config.env` con tu editor de texto favorito (como el Bloc de notas) y configura lo siguiente:

```env
# 1. Pega tu API Key de NVIDIA que copiaste anteriormente (empieza por nvapi-)
OPENROUTER_API_KEY=nvapi-TU_CLAVE_API_NVIDIA_AQUI

# 2. Modelo activo (Recomendamos Mistral Medium por su razonamiento avanzado)
AI_MODEL=mistral-medium-3.5-128b

# 3. Dirección base de NVIDIA
AI_BASE_URL=https://integrate.api.nvidia.com/v1

# 4. Monitor donde se tomará la captura (1 = pantalla secundaria, 0 = principal)
MONITOR_INDEX=1
```

*Nota: Si prefieres usar **OpenRouter** con tu propia clave (`sk-or-v1...`), simplemente comenta la línea de `AI_BASE_URL` poniéndole un símbolo `#` al inicio.*

---

## 🚀 Cómo Ejecutar el Asistente

1. Abre la consola de Windows (PowerShell o CMD) **como Administrador** (es necesario para poder escuchar los atajos de teclado globales en todo el sistema).
2. Entra a la carpeta del proyecto y ejecuta:
   ```bash
   cd exam_assistant
   python main.py
   ```
3. Verás un mensaje que dice `System ready. Press Alt+F` y aparecerán dos pequeños círculos indicadores en la esquina inferior derecha de tu pantalla.
4. **¡Listo!** El sistema se ejecutará en segundo plano. Puedes pulsar `Alt+F` en tu examen para ver la magia de la IA en acción.
