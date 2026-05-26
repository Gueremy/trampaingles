import openai
import time
import threading

lines = open("config.env", encoding="utf-8").readlines()
cfg = {}
for line in lines:
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()

API_KEY = cfg["OPENROUTER_API_KEY"]
BASE_URL = cfg["AI_BASE_URL"]

# Imagen PNG 1x1 negro — simula screenshot de examen
PIXEL_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScAAAAAElFTkSuQmCC"

MODELS = {
    "nemotron-nano (ACTUAL)": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "mistral-small-4":        "mistralai/mistral-small-4-119b-2603",
    "nemotron-super-120b":    "nvidia/nemotron-3-super-120b-a12b",
}

EXAM_QUESTION = (
    "Which sentence is grammatically correct?\n"
    "A) She don't know the answer.\n"
    "B) She doesn't know the answer.\n"
    "C) She not know the answer.\n"
    "D) She knowing the answer.\n\n"
    "Answer with the correct letter and a brief explanation."
)

results = {}
lock = threading.Lock()


def test_model(label, model_id):
    client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=45)
    r = {"model": model_id}

    # --- TEST 1: Texto (pregunta de examen) ---
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": EXAM_QUESTION}],
            max_tokens=200,
            temperature=0.1,
        )
        r["text_time"] = round(time.time() - t0, 1)
        r["text_answer"] = (resp.choices[0].message.content or "").strip()[:200]
        r["text_ok"] = True
    except Exception as e:
        r["text_time"] = round(time.time() - t0, 1)
        r["text_answer"] = str(e)[:120]
        r["text_ok"] = False

    # --- TEST 2: Vision (imagen adjunta) ---
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe what you see in this image in one sentence."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{PIXEL_B64}"}},
                    ],
                }
            ],
            max_tokens=60,
            temperature=0.1,
        )
        r["vision_time"] = round(time.time() - t0, 1)
        r["vision_answer"] = (resp.choices[0].message.content or "").strip()[:150]
        r["vision_ok"] = True
    except Exception as e:
        r["vision_time"] = round(time.time() - t0, 1)
        r["vision_answer"] = str(e)[:120]
        r["vision_ok"] = False

    # --- TEST 3: Streaming ---
    t0 = time.time()
    chunks = 0
    try:
        stream = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "Complete: The capital of France is"}],
            max_tokens=20,
            temperature=0.1,
            stream=True,
        )
        answer = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
                chunks += 1
        r["stream_time"] = round(time.time() - t0, 1)
        r["stream_answer"] = answer.strip()[:80]
        r["stream_chunks"] = chunks
        r["stream_ok"] = True
    except Exception as e:
        r["stream_time"] = round(time.time() - t0, 1)
        r["stream_answer"] = str(e)[:120]
        r["stream_ok"] = False

    with lock:
        results[label] = r
    print(f"  [DONE] {label}")


print("Iniciando benchmark paralelo (3 modelos x 3 pruebas)...\n")
threads = []
for label, model_id in MODELS.items():
    t = threading.Thread(target=test_model, args=(label, model_id))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

SEP = "=" * 72
print(f"\n{SEP}")
print("  BENCHMARK COMPARATIVO — EXAM ASSISTANT")
print(SEP)

for label, r in results.items():
    t_ok  = "OK  " if r.get("text_ok")   else "FAIL"
    v_ok  = "OK  " if r.get("vision_ok") else "FAIL"
    s_ok  = "OK  " if r.get("stream_ok") else "FAIL"
    print(f"\n  [{label}]")
    print(f"    TEXTO   [{t_ok}] {r.get('text_time','?'):>5}s | {r.get('text_answer','')[:80]}")
    print(f"    VISION  [{v_ok}] {r.get('vision_time','?'):>5}s | {r.get('vision_answer','')[:80]}")
    print(f"    STREAM  [{s_ok}] {r.get('stream_time','?'):>5}s | chunks={r.get('stream_chunks',0):>2} | {r.get('stream_answer','')[:50]}")

print(f"\n{SEP}")
print("Tiempo menor = mas rapido | FAIL = no soportado o timeout")
print(SEP)
