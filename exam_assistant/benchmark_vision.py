"""Vision-only benchmark using a real screen capture."""
import openai
import time
import base64
import io
import threading

try:
    from PIL import Image
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Question 1:", fill=(0, 0, 0))
    draw.text((10, 30), "What is 2+2?", fill=(0, 0, 0))
    draw.text((10, 50), "A) 3  B) 4  C) 5  D) 6", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    IMG_B64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    MIME = "image/jpeg"
    print(f"[IMG] Imagen generada: {len(buf.getvalue())} bytes")
except Exception as e:
    print(f"[IMG] Error generando imagen: {e}")
    raise SystemExit(1)

lines = open("config.env", encoding="utf-8").readlines()
cfg = {}
for line in lines:
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()

API_KEY = cfg["OPENROUTER_API_KEY"]
BASE_URL = cfg["AI_BASE_URL"]

MODELS = {
    "nemotron-nano (ACTUAL)": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "mistral-small-4":        "mistralai/mistral-small-4-119b-2603",
}

results = {}
lock = threading.Lock()


def test_vision(label, model_id):
    client = openai.OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=45)
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Eres un asistente de examen. Analiza esta imagen de pantalla "
                                "y responde la pregunta visible. Indica la letra correcta con "
                                "una breve justificacion."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{MIME};base64,{IMG_B64}"},
                        },
                    ],
                }
            ],
            max_tokens=150,
            temperature=0.1,
        )
        elapsed = round(time.time() - t0, 1)
        answer = (resp.choices[0].message.content or "").strip()
        with lock:
            results[label] = {"ok": True, "time": elapsed, "answer": answer}
    except Exception as e:
        elapsed = round(time.time() - t0, 1)
        with lock:
            results[label] = {"ok": False, "time": elapsed, "answer": str(e)[:200]}
    print(f"  [DONE] {label}")


print("Probando vision con imagen real (pregunta de examen simulada)...\n")
threads = []
for label, model_id in MODELS.items():
    t = threading.Thread(target=test_vision, args=(label, model_id))
    t.start()
    threads.append(t)
for t in threads:
    t.join()

SEP = "=" * 72
print(f"\n{SEP}")
print("  VISION BENCHMARK — IMAGEN REAL DE EXAMEN")
print(SEP)
for label, r in results.items():
    status = "OK  " if r["ok"] else "FAIL"
    print(f"\n  [{label}]")
    print(f"    [{status}] {r['time']}s")
    print(f"    {r['answer'][:250]}")
print(f"\n{SEP}")
