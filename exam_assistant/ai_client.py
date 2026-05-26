from __future__ import annotations

import base64
import io
import json
import re
import time
from collections.abc import Iterator
from typing import Callable

from openai import OpenAI

try:
    from PIL import Image as _PILImage
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

_MAX_IMAGE_PX = 2560  # resize longest side to this before sending (2560 = 1440p)
_API_TIMEOUT = 60.0   # seconds

from config import DEFAULT_BASE_URL, DEFAULT_MODEL, load_user_rules

_RULES_CACHE_TTL = 30.0  # seconds


class AIClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        user_rules_loader: Callable[[], str] = load_user_rules,
        openai_factory: Callable[..., OpenAI] = OpenAI,
    ):
        self.client = openai_factory(base_url=base_url, api_key=api_key, timeout=_API_TIMEOUT)
        self.model = model
        self._load_user_rules = user_rules_loader
        self._rules_cache: str = ""
        self._rules_cache_ts: float = 0.0

    def ask_text(self, question: str, context: str, section: str = "general") -> str:
        prompt = self._build_prompt(question, context, section)
        return self._create_completion([{"role": "user", "content": prompt}])

    def stream_text(self, question: str, context: str, section: str = "general") -> Iterator[str]:
        prompt = self._build_prompt(question, context, section)
        yield from self._create_stream([{"role": "user", "content": prompt}])

    def stream_image(self, image_bytes: bytes, question: str, context: str, section: str = "general") -> Iterator[str]:
        """Stream a response that includes both the image and the question."""
        prompt = self._build_prompt(question, context, section)
        img_data, mime = self._resize_image(image_bytes)
        base64_image = base64.b64encode(img_data).decode("utf-8")
        yield from self._create_stream([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}},
                ],
            }
        ])

    def ask_image_with_question(self, image_bytes: bytes, question: str, context: str, section: str = "general") -> str:
        """Ask a question with an image and get a single blocked response."""
        prompt = self._build_prompt(question, context, section)
        img_data, mime = self._resize_image(image_bytes)
        base64_image = base64.b64encode(img_data).decode("utf-8")
        return self._create_completion([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}},
                ],
            }
        ])

    def _create_stream(self, messages: list[dict]) -> Iterator[str]:
        try:
            print(f"[STREAM] starting | model={self.model}")
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **self._extra_args(),
            )
            total = 0
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                content = delta.content
                reasoning = getattr(delta, "reasoning_content", None)
                if content:
                    total += len(content)
                    yield content
                elif reasoning and total == 0:
                    pass  # skip thinking-only chunks silently
            print(f"[STREAM] done | total_content_chars={total}")
        except Exception as exc:
            print(f"[STREAM] EXCEPTION: {exc}")
            yield f"API Error: {exc}"

    @staticmethod
    def _resize_image(image_bytes: bytes, max_px: int = _MAX_IMAGE_PX) -> tuple[bytes, str]:
        if not _HAS_PIL:
            return image_bytes, "image/png"
        img = _PILImage.open(io.BytesIO(image_bytes))
        w, h = img.size
        if max(w, h) <= max_px:
            print(f"[IMG] {w}x{h} {len(image_bytes)}B -> NO COMPRESSION (PNG)")
            return image_bytes, "image/png"
            
        scale = max_px / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), _PILImage.LANCZOS)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        out = buf.getvalue()
        print(f"[IMG] {w}x{h} {len(image_bytes)}B -> PNG {len(out)}B")
        return out, "image/png"

    def ask_image(self, image_bytes: bytes, context: str, section: str = "general") -> str:
        prompt = self._build_prompt("[See attached screenshot - answer the question/task shown]", context, section)
        img_data, mime = self._resize_image(image_bytes)
        base64_image = base64.b64encode(img_data).decode("utf-8")
        return self._create_completion(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}},
                    ],
                }
            ],
            vision=True,
        )

    def extract_questions_from_image(self, image_bytes: bytes, context: str = "") -> list[dict]:
        prompt = (
            "Extract the visible practice questions from the screenshot and return ONLY valid JSON.\n"
            'Schema: {"questions":[{"id":"1","prompt":"...","choices":["..."],"notes":"..."}]}\n'
            "Rules: do not answer the questions, do not include markdown, do not invent hidden text, "
            "and preserve numbering if it exists."
        )
        if context:
            prompt += f"\n\nContext:\n{context}"

        img_data, mime = self._resize_image(image_bytes)
        base64_image = base64.b64encode(img_data).decode("utf-8")
        raw = self._create_completion(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}},
                    ],
                }
            ],
            vision=True,
        )
        return self._parse_extracted_questions(raw)

    def _create_completion(self, messages: list[dict], vision: bool = False) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **self._extra_args(vision=vision),
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            return f"API Error: {exc}"

    def _extra_args(self, vision: bool = False) -> dict:
        extra_args = {
            "max_tokens": 1024,   # suficiente para examen; menos = mas rapido
            "temperature": 0.1,   # deterministico: mejor precision en preguntas
            "top_p": 0.90,
        }
        # Solo habilitar thinking en modelos de reasoning explicitos
        is_reasoning = "reasoning" in self.model.lower() or "thinking" in self.model.lower()
        if not vision and is_reasoning:
            extra_args["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 4096,
            }
        return extra_args

    def _get_user_rules(self) -> str:
        now = time.monotonic()
        if now - self._rules_cache_ts > _RULES_CACHE_TTL:
            self._rules_cache = self._load_user_rules()
            self._rules_cache_ts = now
        return self._rules_cache

    def _build_prompt(self, question: str, context: str, section: str = "general") -> str:
        master_prompt = (
            "Eres un EXPERTO DE ELITE en Examenes de Ingles Academico (TOEFL, IELTS, Cambridge, Pearson). "
            "Tu mision es proporcionar la respuesta 100% correcta analizando sistematicamente la imagen, el audio transcrito y el historial.\n\n"
            "METODOLOGIA DE ANALISIS OBLIGATORIA (CHAIN OF THOUGHT):\n"
            "ANTES de dar cualquier respuesta final, DEBES incluir un bloque de analisis paso a paso llamado '[ANALISIS]'.\n"
            "En este bloque debes verificar ESTRICTAMENTE las siguientes MICRO-REGLAS:\n"
            "- REGLA DE WH-QUESTIONS: Si es una conversacion, verifica la RESPUESTA para elegir la pregunta. (Lugar = Where, Tiempo/Hora = When, Persona = Who, Razon = Why, Actividad = What). PROHIBIDO fallar esta correlacion.\n"
            "- REGLA DE COMPARATIVOS/SUPERLATIVOS: Revisa las palabras que rodean el espacio. Si inmediatamente despues dice 'than', ESTAS OBLIGADO a usar comparativo (-er o more). Si antes dice 'the', ESTAS OBLIGADO a usar superlativo (-est o most). Recuerda: 1 silaba (safe) usa -er/-est, NUNCA 'more safe'.\n"
            "- Concordancia Sujeto-Verbo y tiempos verbales segun contexto.\n"
            "- CHECKLIST DE WRITING: Si es una seccion de escritura, HAZ UN CHECKLIST VISIBLE contando si usaste TODOS los conectores (and, but, because) y todos los tiempos/verbos exigidos antes de dar el texto final.\n\n"
            "INSTRUCCIONES ESPECIFICAS:\n"
            "1. INSTRUCCION DEL USUARIO: Prioriza las peticiones directas del usuario por sobre todo lo demas.\n"
            "2. PREGUNTAS VISIBLES: Resuelve TODAS las preguntas visibles en la imagen una por una.\n"
            "3. PREGUNTAS DE COMPLETAR / DROPDOWNS (CASILLAS CERRADAS):\n"
            "   - Si ves '[choose]' sin opciones visibles, sugiere las 3 palabras gramaticalmente mas probables.\n"
            "   - Si el menu esta ABIERTO, elige EXACTAMENTE de esa lista.\n"
            "   - Revisa opciones ya seleccionadas por el usuario y evalualas.\n"
            "4. SECCIONES DE ESCRITURA (WRITING): Genera el texto perfecto. Ejecuta tu checklist interno y asegura que TODAS las cruces rojas (❌) pasen a verdes (✅).\n"
            "5. CRUCE DE DATOS: Si es un Listening, busca en [RECENT AUDIO]. Si es Reading, basate en la imagen.\n\n"
            "REGLAS DE FORMATO (USAR SIEMPRE ESTA ESTRUCTURA):\n"
            "- Responde SIEMPRE en espanol (excepto el ingles del examen).\n"
            "Para CADA pregunta, usa ESTRICTAMENTE este formato:\n"
            "[ANALISIS]\n"
            "1. Regla gramatical clave: ...\n"
            "2. Descarte de trampas: ...\n"
            "✅ RESPUESTA FINAL: [Tu respuesta] - [Breve conclusion]\n\n"
            "Ejemplo Multi-opcion:\n"
            "[ANALISIS]\n"
            "El sujeto es 'He' (3ra persona) y hay un 'since 2010', requiere Present Perfect.\n"
            "✅ RESPUESTA FINAL: B - has worked\n\n"
            "Tienes memoria activa: Recuerdas el historial reciente. Usalo si la imagen actual no tiene toda la informacion."
        )

        base = master_prompt
        user_rules = self._get_user_rules()
        if user_rules:
            base += f"\n\n[REGLAS ADICIONALES DEL USUARIO - PRIORIDAD MAXIMA]:\n{user_rules}"

        base += "\n\n"
        if context:
            base += "=== CONTEXTO DISPONIBLE (AUDIO Y CHAT) ===\n"
            base += context + "\n\n"

        base += f"--- SOLICITUD ACTUAL ---\nPREGUNTA O INDICACION: {question}"
        return base

    def _parse_extracted_questions(self, raw: str) -> list[dict]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned).rstrip("`").strip()

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            return []

        if isinstance(payload, list):
            questions = payload
        elif isinstance(payload, dict):
            questions = payload.get("questions", [])
        else:
            return []

        if not isinstance(questions, list):
            return []

        normalized: list[dict] = []
        for item in questions:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "id": str(item.get("id", "")).strip(),
                    "prompt": str(item.get("prompt", "")).strip(),
                    "choices": [str(choice).strip() for choice in item.get("choices", []) if str(choice).strip()],
                    "notes": str(item.get("notes", "")).strip(),
                }
            )
        return normalized


def is_error_response(text: str) -> bool:
    return text.startswith("API Error:")
