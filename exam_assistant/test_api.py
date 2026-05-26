import time
from ai_client import AIClient, is_error_response
from config import AppConfig

try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

cfg = AppConfig.from_file()
if not cfg.api_key:
    print("Error: OPENROUTER_API_KEY not found in config.env")
    raise SystemExit(1)

client = AIClient(cfg.api_key, base_url=cfg.base_url, model=cfg.model)
print("=== INICIANDO SIMULACION AVANZADA DE PRUEBAS ===\n")
failed = False

# 1. LISTENING (Múltiples alternativas)
print("SECCION: LISTENING (Multiple)")
listening_context = "Transcript: Today we will talk about the French Revolution. It primarily began because of severe financial crises and widespread social inequality."
listening_question = """1. Why did the French Revolution begin?
A) Because of a sudden invasion by a foreign country.
B) Due to financial crises and social inequality.
C) Due to a religious disagreement.
D) Because the King wanted to expand his empire."""
print("Enviando...\n")
res_list = client.ask_text(listening_question, context=listening_context, section="listening")
print(f"Respuesta IA:\n{res_list}\n{'-'*50}")
failed = failed or is_error_response(res_list)
time.sleep(1)

# 2. READING (Múltiples preguntas a la vez con alternativas)
print("SECCION: READING (Varias preguntas con alternativas)")
reading_q = """Based on the text about photosynthesis:
1. What is the primary source of energy for photosynthesis?
A) Soil
B) Water
C) The Sun
D) Wind

2. What gas do plants absorb during this process?
A) Oxygen
B) Carbon Dioxide
C) Nitrogen
D) Hydrogen"""
print("Enviando...\n")
res_read = client.ask_text(reading_q, context="", section="reading")
print(f"Respuesta IA:\n{res_read}\n{'-'*50}")
failed = failed or is_error_response(res_read)
time.sleep(1)

# 3. VOCABULARY (Matching)
print("SECCION: VOCABULARY (Matching)")
vocab_q = """Match the words to their definitions:
1. Ubiquitous
2. Ephemeral

A) Lasting for a very short time.
B) Present, appearing, or found everywhere."""
print("Enviando...\n")
res_vocab = client.ask_text(vocab_q, context="", section="vocabulary")
print(f"Respuesta IA:\n{res_vocab}\n{'-'*50}")
failed = failed or is_error_response(res_vocab)
time.sleep(1)

# 4. GENERAL (Pregunta aleatoria sin contexto específico)
print("SECCION: GENERAL (Detectar tipo automatico)")
gen_q = "Complete the sentence: If I had known you were in town, I (call) _____ you."
print("Enviando...\n")
res_gen = client.ask_text(gen_q, context="", section="general")
print(f"Respuesta IA:\n{res_gen}\n{'-'*50}")
failed = failed or is_error_response(res_gen)

if failed:
    print("\n❌ La simulación detectó respuestas inválidas o errores de API.")
    raise SystemExit(1)

print("\n✅ Todas las pruebas finalizaron con éxito.")
