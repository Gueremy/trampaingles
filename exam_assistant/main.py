from __future__ import annotations

import queue
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

import keyboard as kb
import pyperclip

from ai_client import AIClient
from audio_service import AudioTranscriptionService
from capture_service import capture_full_screen_png, capture_region_png, get_dpi_scale
from config import AppConfig, RULES_FILE
from context_manager import ContextManager
from ui_components import (
    AskQuestionPopup,
    CompactInputOverlay,
    CompactResponseOverlay,
    LoadingOverlay,
    RegionSelector,
    ResponseOverlay,
    StatusLights,
    StreamingResponseOverlay,
    create_tray_icon,
    show_notification,
    show_setup_error,
)


def extract_answer_letter(text: str) -> str | None:
    match = re.search(r"✅\s*([A-Ea-e])", text) or re.search(r"\b([A-Ea-e])\)", text)
    return match.group(1).lower() if match else None


@dataclass(frozen=True)
class AnalysisRequest:
    mode: str
    prompt: str


def parse_analysis_request(text: str | None, default_mode: str = "single") -> AnalysisRequest:
    normalized = (text or "").strip()
    if not normalized:
        default_prompt = "Resuelve la pregunta visible en la imagen. Si hay multiples preguntas, resuelvelas TODAS."
        if default_mode == "all":
            default_prompt = "Resuelve TODAS las preguntas visibles en la pantalla de forma detallada."
        return AnalysisRequest(default_mode, default_prompt)

    lowered = normalized.lower()
    prefixes = {
        "/all": "all",
        "/one": "single",
        "/single": "single",
        "/followup": "followup",
    }
    for prefix, mode in prefixes.items():
        if lowered.startswith(prefix):
            payload = normalized[len(prefix) :].strip()
            if not payload:
                payload = (
                    "Analyze every visible practice question and answer all of them."
                    if mode == "all"
                    else "Analyze the visible practice question."
                )
            return AnalysisRequest(mode, payload)

    return AnalysisRequest(default_mode, normalized)


def build_mode_prompt(request: AnalysisRequest) -> str:
    if request.mode == "all":
        return (
            f"INSTRUCCION DEL USUARIO: {request.prompt}\n\n"
            "REGLA: Resuelve TODAS las preguntas visibles en la imagen. Usa una lista numerada."
        )
    if request.mode == "followup":
        return (
            f"INSTRUCCION DEL USUARIO: {request.prompt}\n\n"
            "REGLA: Usa el historial de chat y audio para continuar el ejercicio."
        )
    return (
        f"INSTRUCCION: {request.prompt}\n\n"
        "NOTA: Presta especial atencion a las transcripciones de audio (Listening) en el contexto si la pregunta es sobre lo que se habla. "
        "Si ves multiples preguntas en la imagen, resuelvelas todas. "
        "Si la instruccion es una pregunta libre, respondela directamente basandote en la imagen o el audio."
    )


def format_extracted_questions(questions: list[dict]) -> str:
    if not questions:
        return ""
    lines = ["=== EXTRACTED PRACTICE QUESTIONS ==="]
    for question in questions:
        qid = question.get("id") or "?"
        lines.append(f"[{qid}] {question.get('prompt', '')}")
        for choice in question.get("choices", [])[:5]:
            lines.append(f" - {choice}")
        notes = question.get("notes", "")
        if notes:
            lines.append(f"   Notes: {notes}")
    return "\n".join(lines)


def build_answer_request(question: dict, mode: str = "single") -> AnalysisRequest:
    prompt_parts = []
    qid = question.get("id") or "?"
    prompt_parts.append(f"Question {qid}: {question.get('prompt', '')}")
    choices = question.get("choices", [])
    if choices:
        prompt_parts.append("Choices:")
        prompt_parts.extend([f"- {choice}" for choice in choices])
    notes = question.get("notes", "")
    if notes:
        prompt_parts.append(f"Notes: {notes}")
    return AnalysisRequest(mode=mode, prompt="\n".join(prompt_parts))


class ExamAssistant:
    def __init__(self):
        cfg = AppConfig.from_file()
        if not cfg.api_key:
            show_setup_error()
            raise SystemExit(1)

        self.ai = AIClient(cfg.api_key, base_url=cfg.base_url, model=cfg.model)
        self.context = ContextManager()
        self.audio = AudioTranscriptionService(self._on_audio_transcript, self.notify)

        self.running = True
        self.audio_active = False
        self.last_answer = ""
        self._processing = False
        self._action_queue: queue.Queue[dict] = queue.Queue()
        self._response_queue: queue.Queue[dict] = queue.Queue()
        self._active_loading: LoadingOverlay | None = None
        self._active_streaming: StreamingResponseOverlay | None = None
        self._status_lights: StatusLights | None = None
        self._active_compact: CompactResponseOverlay | None = None
        self._last_image_bytes: bytes | None = None  # ultima imagen capturada para contexto Alt+I
        self._tray_icon = None
        self._ui_ref: tk.Tk | None = None
        self._dpi_scale = get_dpi_scale()
        self._monitor_index = cfg.monitor_index
        self._pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="ai_worker")

        print("AI Exam Assistant started")

    def _on_audio_transcript(self, transcript: str) -> None:
        self.context.add("audio", transcript, "system-audio")

    def shutdown(self):
        self.running = False
        self.audio.stop()
        self.audio_active = False
        self._pool.shutdown(wait=False, cancel_futures=True)
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
        if self._ui_ref:
            try:
                self._ui_ref.after(0, self._ui_ref.destroy)
            except Exception:
                pass

    def _process_queue(self):
        try:
            while True:
                action = self._action_queue.get_nowait()
                action_type = action.get("action")
                if action_type == "full_screen":
                    self._handle_full_screen_action()
                elif action_type == "screenshot":
                    self._handle_screenshot_action()
                elif action_type == "text":
                    self._handle_text_action()
                elif action_type == "manual":
                    self._handle_manual_action()
                elif action_type == "toggle_answer":
                    if self._active_compact and self._active_compact.is_open():
                        self._active_compact.close()
                        self._active_compact = None
                    elif self.last_answer and self._ui_ref:
                        self._active_compact = CompactResponseOverlay(
                            self._ui_ref, self.last_answer,
                            on_close=lambda: setattr(self, "_active_compact", None),
                        )
        except queue.Empty:
            pass

        try:
            while True:
                task = self._response_queue.get_nowait()
                task_type = task.get("type")
                if task_type == "notify":
                    show_notification(self._ui_ref, task["msg"])
                elif task_type == "answer":
                    self._close_loading_gui()
                    if self._status_lights:
                        self._status_lights.set_ready(True)
                elif task_type == "error":
                    self._close_loading_gui()
                    if self._status_lights:
                        self._status_lights.set_processing(False)
                    show_notification(self._ui_ref, f"Error: {task['msg']}")
                elif task_type == "show_loading":
                    self._close_loading_gui()
                    self._active_loading = LoadingOverlay(self._ui_ref, task["msg"])
                elif task_type == "close_loading":
                    self._close_loading_gui()
                elif task_type == "stream_start":
                    self._close_loading_gui()
                    self._active_streaming = StreamingResponseOverlay(self._ui_ref, task["source"])
                elif task_type == "stream_chunk":
                    if self._active_streaming and self._active_streaming.root.winfo_exists():
                        self._active_streaming.append(task["content"])
                elif task_type == "stream_done":
                    self._active_streaming = None
                    if self._status_lights:
                        self._status_lights.set_ready(True)
                elif task_type == "lights_processing":
                    if self._status_lights:
                        self._status_lights.set_processing(task["value"])
                elif task_type == "lights_ready":
                    if self._status_lights:
                        self._status_lights.set_ready(task["value"])
        except queue.Empty:
            pass

        if self.running and self._ui_ref:
            self._ui_ref.after(50, self._process_queue)

    def _close_loading_gui(self):
        if self._active_loading:
            self._active_loading.close()
            self._active_loading = None

    def notify(self, message: str):
        self._response_queue.put({"type": "notify", "msg": message})

    def _check_start_processing(self) -> bool:
        if self._processing:
            print(f"[GUARD] BLOCKED — _processing still True")
            self.notify("A previous request is still processing")
            return False
        self._processing = True
        print(f"[GUARD] OK — _processing set True")
        return True

    def _run_ai_worker(self, worker, loading_msg: str, show_loading: bool = False):
        def wrapped():
            if show_loading and loading_msg:
                self._response_queue.put({"type": "show_loading", "msg": loading_msg})
            self._response_queue.put({"type": "lights_processing", "value": True})
            self._response_queue.put({"type": "lights_ready", "value": False})
            try:
                worker()
            except Exception as exc:
                print(f"[WORKER] EXCEPTION: {exc}")
                self._response_queue.put({"type": "error", "msg": str(exc)})
            finally:
                print(f"[WORKER] finally: _processing={self._processing} -> False")
                self._processing = False
                self._response_queue.put({"type": "lights_processing", "value": False})

        threading.Thread(target=wrapped, daemon=True).start()

    def _copy_answer(self, answer: str):
        try:
            pyperclip.copy(answer)
        except Exception:
            pass

    def _handle_full_screen_action(self):
        if not self._check_start_processing():
            return
        try:
            img_bytes = capture_full_screen_png(self._monitor_index)
        except Exception as exc:
            self._processing = False
            self.notify(f"Screen capture failed: {exc}")
            return

        def worker():
            print(f"[WORKER] full_screen start | processing={self._processing}")
            ctx = self.context.get_structured_context("single")
            answer = self.ai.ask_image(img_bytes, ctx)
            print(f"[WORKER] ask_image returned {len(answer)} chars")
            if answer:  # solo guarda si hubo respuesta valida
                self._last_image_bytes = img_bytes
            self.context.add("user", "[Full Screen] auto-analyze", "full-screen")
            self.context.add("assistant", answer, "ai")
            self.last_answer = answer
            self._copy_answer(answer)
            self._response_queue.put({"type": "answer", "content": answer, "source": "Analysis"})

        self._run_ai_worker(worker, "Analyzing screen...", show_loading=False)

    def _handle_screenshot_action(self):
        if not self._check_start_processing():
            return
        self.notify("Select a screen region")

        def on_region_selected(coords):
            if coords is None:
                self._processing = False
                self.notify("Selection cancelled")
                return

            def on_region_prompt(text: str | None):
                request = parse_analysis_request(text, default_mode="single")

                def worker():
                    img_bytes = capture_region_png(coords, self._dpi_scale)
                    self._last_image_bytes = img_bytes  # guarda para Alt+I
                    ctx = self.context.get_structured_context(request.mode)
                    extracted = self.ai.extract_questions_from_image(img_bytes, ctx)
                    if request.mode == "all":
                        if not extracted:
                            extracted = [{"id": "1", "prompt": request.prompt, "choices": [], "notes": ""}]
                        snapshot = format_extracted_questions(extracted)
                        answer_ctx = self.context.get_structured_context("single")

                        def _answer_item(item):
                            answer_request = build_answer_request(item, mode="single")
                            return (item.get("id") or "?", self.ai.ask_text(build_mode_prompt(answer_request), f"{answer_ctx}\n\n{snapshot}", "general"))

                        futures = {self._pool.submit(_answer_item, item): item for item in extracted}
                        results: dict[str, str] = {}
                        for fut in as_completed(futures):
                            try:
                                qid, ans = fut.result()
                                results[qid] = f"[{qid}] {ans}"
                            except Exception as exc:
                                item = futures[fut]
                                results[item.get("id") or "?"] = f"[{item.get('id') or '?'}] Error: {exc}"
                        answers = [results[item.get("id") or "?"] for item in extracted if (item.get("id") or "?") in results]

                        final_answer = "\n\n".join(answers)
                        self.context.add("user", f"[Screenshot region][{request.mode}] {request.prompt}", "screenshot")
                        self.context.add("assistant", final_answer, "ai")
                        self.last_answer = final_answer
                        self._copy_answer(final_answer)
                        self._response_queue.put({"type": "answer", "content": final_answer, "source": "Screenshot"})
                        return

                    if extracted:
                        first_question = extracted[0]
                        answer_request = build_answer_request(first_question, mode=request.mode)
                        prompt_ctx = f"{build_mode_prompt(answer_request)}\n\nCONTEXT:\n{ctx}\n\n{format_extracted_questions(extracted)}"
                        stream = self.ai.stream_text(prompt_ctx, "", "general")
                    else:
                        prompt_ctx = f"{build_mode_prompt(request)}\n\nCONTEXT:\n{ctx}"
                        answer = self.ai.ask_image(img_bytes, prompt_ctx, "general")
                        self.context.add("user", f"[Screenshot region][{request.mode}] {request.prompt}", "screenshot")
                        self.context.add("assistant", answer, "ai")
                        self.last_answer = answer
                        self._copy_answer(answer)
                        self._response_queue.put({"type": "answer", "content": answer, "source": "Screenshot"})
                        return

                    self._processing = False
                    self._response_queue.put({"type": "stream_start", "source": "Screenshot"})
                    answer = ""
                    for chunk in stream:
                        answer += chunk
                        self._response_queue.put({"type": "stream_chunk", "content": chunk})
                    self._response_queue.put({"type": "stream_done", "content": answer})
                    self.context.add("user", f"[Screenshot region][{request.mode}] {request.prompt}", "screenshot")
                    self.context.add("assistant", answer, "ai")
                    self.last_answer = answer
                    self._copy_answer(answer)

                loading = "Reasoning..." if "reasoning" in self.ai.model.lower() else "Analyzing region..."
                self._run_ai_worker(worker, loading)

            AskQuestionPopup(
                self._ui_ref,
                on_region_prompt,
                title="Region Scan Command",
                hint="Use /all for every question in the selected area, /one for a single question, /followup to use saved context",
            )

        RegionSelector(self._ui_ref, on_region_selected)

    def _handle_text_action(self):
        if not self._check_start_processing():
            return

        def worker():
            original = ""
            try:
                original = pyperclip.paste()
            except Exception:
                pass

            # Esperar a que Alt se suelte completamente antes de enviar Ctrl+C
            # (Alt+T presionado puede cancelar la seleccion en muchas apps)
            time.sleep(0.15)
            kb.send("ctrl+c")

            deadline = time.monotonic() + 1.5  # aumentado de 0.5s a 1.5s
            selected = original
            while time.monotonic() < deadline:
                time.sleep(0.05)
                try:
                    candidate = pyperclip.paste()
                except Exception:
                    continue
                if candidate != original:
                    selected = candidate
                    break

            if not selected or selected == original or len(selected.strip()) < 10:
                self.notify("No se detecto texto seleccionado — selecciona texto y presiona Alt+T")
                return

            request = parse_analysis_request(selected.strip(), default_mode="single")
            ctx = self.context.get_structured_context(request.mode)
            answer = self.ai.ask_text(build_mode_prompt(request), ctx, "general")
            self._processing = False
            self._response_queue.put({"type": "answer", "content": answer, "source": "Text"})
            self.context.add("user", selected[:200], "text-selection")
            self.context.add("assistant", answer[:500], "ai")
            self.last_answer = answer
            self._copy_answer(answer)

        loading = "Reasoning..." if "reasoning" in self.ai.model.lower() else "Analyzing text..."
        self._run_ai_worker(worker, loading)

    def _handle_manual_action(self):
        if not self._check_start_processing():
            return

        def on_manual_submitted(text: str | None):
            request = parse_analysis_request(text, default_mode="single")

            def worker():
                ctx = self.context.get_structured_context(request.mode)
                # Si hay imagen previa y no es followup de texto puro, la adjuntamos
                if self._last_image_bytes and request.mode != "followup":
                    print(f"[MANUAL] usando imagen previa ({len(self._last_image_bytes)}B) como contexto visual")
                    answer = self.ai.ask_image_with_question(
                        self._last_image_bytes,
                        build_mode_prompt(request),
                        ctx,
                        "general",
                    )
                else:
                    answer = self.ai.ask_text(build_mode_prompt(request), ctx, "general")
                self._processing = False
                self._response_queue.put({"type": "answer", "content": answer, "source": "Chat"})
                self.context.add("user", f"[{request.mode}] {request.prompt}", "manual-input")
                self.context.add("assistant", answer, "ai")
                self.last_answer = answer
                self._copy_answer(answer)

            loading = "Reasoning..." if "reasoning" in self.ai.model.lower() else "Processing question..."
            self._run_ai_worker(worker, loading)

        CompactInputOverlay(self._ui_ref, on_manual_submitted)

    def _show_last_answer(self):
        self._action_queue.put({"action": "toggle_answer"})

    def capture_full_screen(self):
        self._action_queue.put({"action": "full_screen"})

    def capture_screenshot(self):
        self._action_queue.put({"action": "screenshot"})

    def capture_text(self):
        self._action_queue.put({"action": "text"})

    def ask_manual_question(self):
        self._action_queue.put({"action": "manual"})

    def auto_type_answer(self):
        if not self.last_answer:
            self.notify("No previous answer was stored")
            return
        letter = extract_answer_letter(self.last_answer)
        if not letter:
            self.notify("No clear A-E option was detected")
            return
        self.notify(f"Typing answer: {letter.upper()}")
        threading.Thread(target=lambda: (time.sleep(0.4), kb.send(letter)), daemon=True).start()

    def toggle_audio(self):
        if self.audio.active:
            self.audio.stop()
            self.audio_active = False
        else:
            self.audio.start()
            self.audio_active = True

    def open_rules(self):
        if not RULES_FILE.exists():
            RULES_FILE.write_text(
                "# REGLAS PERSONALIZADAS PARA TU IA\n"
                "# Escribe aqui indicaciones especificas que quieres que la IA siga SIEMPRE.\n"
                "# Ejemplo: 'Siempre responde de forma muy concisa'\n",
                encoding="utf-8",
            )
        try:
            subprocess.Popen(["notepad.exe", str(RULES_FILE)])
        except OSError:
            pass

    def start(self):
        kb.add_hotkey("alt+s", self.capture_screenshot, suppress=True)
        kb.add_hotkey("alt+f", self.capture_full_screen, suppress=True)
        kb.add_hotkey("alt+a", self.toggle_audio, suppress=True)
        kb.add_hotkey("alt+t", self.capture_text, suppress=True)
        kb.add_hotkey("alt+i", self.ask_manual_question, suppress=True)
        kb.add_hotkey("alt+v", self.auto_type_answer, suppress=True)
        kb.add_hotkey("alt+r", self._show_last_answer, suppress=True)
        kb.add_hotkey("alt+c", lambda: self.notify("Clearing memory") or self.context.clear(), suppress=True)
        kb.add_hotkey("alt+h", self.open_rules, suppress=True)
        kb.add_hotkey("alt+q", self.shutdown, suppress=True)

        threading.Thread(target=create_tray_icon, args=(self,), daemon=True).start()

        self._ui_ref = tk.Tk()
        self._ui_ref.withdraw()

        self._status_lights = StatusLights(self._ui_ref)
        self._status_lights.set_click_handler(self._show_last_answer)

        self._process_queue()

        print("Assistant active")
        print("Alt+F = Full screen | Alt+S = Region")
        print("Alt+T = Selected text | Alt+I = Manual question")
        print("Alt+V = Auto type | Alt+A = Audio | Alt+R = Show last answer")
        self.notify("System ready. Press Alt+F")

        try:
            self._ui_ref.mainloop()
        except KeyboardInterrupt:
            self.shutdown()


if __name__ == "__main__":
    app = ExamAssistant()
    app.start()
