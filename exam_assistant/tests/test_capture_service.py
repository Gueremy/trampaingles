import unittest
from unittest.mock import MagicMock, patch

import capture_service


class CaptureServiceTests(unittest.TestCase):
    @patch("capture_service.mss.tools.to_png", return_value=b"png")
    @patch("capture_service.mss.MSS")
    def test_capture_full_screen_png_uses_primary_monitor(self, mock_mss, _mock_to_png):
        screenshot = MagicMock(rgb=b"rgb", size=(10, 10))
        sct = MagicMock()
        sct.monitors = [None, {"top": 0, "left": 0, "width": 10, "height": 10}]
        sct.grab.return_value = screenshot
        mock_mss.return_value.__enter__.return_value = sct
        result = capture_service.capture_full_screen_png()
        self.assertEqual(result, b"png")
        sct.grab.assert_called_once_with(sct.monitors[1])

    @patch("capture_service.mss.tools.to_png", return_value=b"png")
    @patch("capture_service.mss.MSS")
    def test_capture_region_png_builds_monitor_rect(self, mock_mss, _mock_to_png):
        screenshot = MagicMock(rgb=b"rgb", size=(10, 10))
        sct = MagicMock()
        sct.grab.return_value = screenshot
        mock_mss.return_value.__enter__.return_value = sct
        capture_service.capture_region_png((1, 2, 6, 9))
        sct.grab.assert_called_once_with({"top": 2, "left": 1, "width": 5, "height": 7})


if __name__ == "__main__":
    unittest.main()
