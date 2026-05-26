# AI Assistant UNIFICADO 🧠⚡

Sistema de IA invisible y contextual para exámenes. La IA usa automáticamente lo que **ve** en pantalla y lo que **escucha** por audio para responderte.

---

## ⚙️ Setup

1. Instala dependencias:
   ```
   pip install keyboard mss pyperclip pystray pillow faster-whisper soundcard numpy openai
   ```
2. Edita `config.env` y pega tus claves:
   ```
   OPENROUTER_API_KEY=tu_key_aqui
   
   # OPCIONAL: Para usar modelos GRATIS o NVIDIA
   AI_MODEL=openrouter/free
   # AI_BASE_URL=https://integrate.api.nvidia.com/v1
   ```
3. Ejecuta como Administrador: `python main.py`

---

## 🎮 Comandos (Atajos)

| Hotkey | Acción |
|--------|--------|
| `Alt+F` | **ANÁLISIS TOTAL**: Captura pantalla + audio + abre pregunta manual |
| `Alt+S` | **Captura Área**: Selecciona un área específica para analizar |
| `Alt+T` | **Texto Seleccionado**: Copia el texto actual y lo analiza |
| `Alt+I` | **Pregunta Manual**: Abre un popup para preguntar manualmente |
| `Alt+V` | **AUTO-ESCRIBIR**: Escribe automáticamente la letra de la respuesta (A-E) |
| `Alt+A` | **Audio**: Activa/Desactiva escucha de audio del sistema |
| `Alt+C` | **Limpiar**: Borra la memoria de la conversación |
| `Alt+H` | **Reglas**: Abre el archivo para personalizar instrucciones de la IA |
| `Alt+Q` | **Salir**: Cierra el programa |

---

## 💡 Funcionamiento Natural

- **Contexto Automático**: Cuando usas `Alt+F`, la IA recibe una foto de toda tu pantalla y las últimas transcripciones de audio. No necesitas decirle en qué sección estás.
- **Autotype**: Si la IA te responde con algo como "✅ B", simplemente presiona `Alt+V` y el sistema escribirá la letra "b" por ti.
- **Reglas Personalizadas**: Usa `Alt+H` para decirle a la IA cómo prefieres que te responda (ej: "sé muy breve", "siempre usa tono formal").

---
