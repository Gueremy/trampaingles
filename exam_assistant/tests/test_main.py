import unittest
from unittest.mock import MagicMock, patch

import main


class MainHelpersTests(unittest.TestCase):
    def test_extract_answer_letter_from_checkmark_format(self):
        self.assertEqual(main.extract_answer_letter("✅ B"), "b")

    def test_extract_answer_letter_from_parenthesis_format(self):
        self.assertEqual(main.extract_answer_letter("C) option"), "c")

    def test_extract_answer_letter_returns_none_for_invalid_text(self):
        self.assertIsNone(main.extract_answer_letter("no answer"))

    def test_parse_analysis_request_defaults_to_single(self):
        req = main.parse_analysis_request("translate this")
        self.assertEqual(req.mode, "single")
        self.assertEqual(req.prompt, "translate this")

    def test_parse_analysis_request_supports_all_command(self):
        req = main.parse_analysis_request("/all answer every visible item")
        self.assertEqual(req.mode, "all")
        self.assertIn("every visible item", req.prompt)

    def test_parse_analysis_request_supports_followup_command(self):
        req = main.parse_analysis_request("/followup continue with previous context")
        self.assertEqual(req.mode, "followup")

    def test_build_mode_prompt_changes_by_mode(self):
        all_prompt = main.build_mode_prompt(main.AnalysisRequest("all", "go"))
        single_prompt = main.build_mode_prompt(main.AnalysisRequest("single", "go"))
        self.assertIn("every fully visible", all_prompt)
        self.assertIn("answer only one question", single_prompt)

    def test_build_answer_request_formats_question_payload(self):
        request = main.build_answer_request(
            {"id": "12", "prompt": "Choose the right answer", "choices": ["A", "B"], "notes": "note"},
            mode="single",
        )
        self.assertEqual(request.mode, "single")
        self.assertIn("Question 12", request.prompt)
        self.assertIn("Choices:", request.prompt)
        self.assertIn("note", request.prompt)


class ExamAssistantBehaviorTests(unittest.TestCase):
    def make_app(self):
        cfg = MagicMock(api_key="k", base_url="u", model="m")
        with patch("main.AppConfig.from_file", return_value=cfg), patch("main.AIClient"), patch("main.ContextManager"), patch(
            "main.AudioTranscriptionService"
        ):
            return main.ExamAssistant()

    def test_notify_enqueues_message(self):
        app = self.make_app()
        app.notify("hello")
        self.assertEqual(app._response_queue.get_nowait()["msg"], "hello")

    def test_check_start_processing_blocks_when_busy(self):
        app = self.make_app()
        app._processing = True
        self.assertFalse(app._check_start_processing())
        queued = app._response_queue.get_nowait()
        self.assertEqual(queued["type"], "notify")

    @patch("main.time.sleep", return_value=None)
    @patch("main.kb.send")
    def test_auto_type_answer_sends_detected_letter(self, mock_send, _mock_sleep):
        import time as _time
        app = self.make_app()
        app.last_answer = "✅ D"
        with patch.object(app, "notify"):
            app.auto_type_answer()
        _time.sleep(0.1)
        mock_send.assert_called_once_with("d")

    def test_auto_type_answer_notifies_when_missing(self):
        app = self.make_app()
        app.last_answer = "nothing here"
        with patch.object(app, "notify") as notify:
            app.auto_type_answer()
        notify.assert_called()

    def test_toggle_audio_updates_flag(self):
        app = self.make_app()
        app.audio.active = False
        app.toggle_audio()
        app.audio.start.assert_called_once()
        self.assertTrue(app.audio_active)
        app.audio.active = True
        app.toggle_audio()
        app.audio.stop.assert_called_once()
        self.assertFalse(app.audio_active)

    def test_shutdown_stops_audio_and_clears_tray(self):
        app = self.make_app()
        app._tray_icon = MagicMock()
        app._ui_ref = MagicMock()
        app.shutdown()
        app.audio.stop.assert_called_once()
        app._ui_ref.after.assert_called()
        self.assertFalse(app.running)

    def test_run_ai_worker_emits_error_task_on_exception(self):
        app = self.make_app()
        app._run_ai_worker(lambda: (_ for _ in ()).throw(RuntimeError("boom")), "load")
        import time as _time

        _time.sleep(0.05)
        seen = []
        while not app._response_queue.empty():
            seen.append(app._response_queue.get_nowait()["type"])
        self.assertIn("show_loading", seen)
        self.assertIn("error", seen)

    def test_on_audio_transcript_adds_context_entry(self):
        app = self.make_app()
        app._on_audio_transcript("hello audio")
        app.context.add.assert_called_once_with("audio", "hello audio", "system-audio")


if __name__ == "__main__":
    unittest.main()
