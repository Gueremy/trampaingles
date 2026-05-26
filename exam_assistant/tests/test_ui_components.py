import unittest

from ui_components import THEME, anchor_bottom_right, estimate_response_window


class UIComponentsTests(unittest.TestCase):
    def test_estimate_response_window_expanded_is_larger(self):
        compact = estimate_response_window("hello\nworld", expanded=False)
        expanded = estimate_response_window("hello\nworld", expanded=True)
        self.assertGreater(expanded[0], compact[0])
        self.assertGreater(expanded[1], compact[1])

    def test_estimate_response_window_grows_for_long_text(self):
        short = estimate_response_window("short")
        long = estimate_response_window("x" * 800)
        self.assertGreaterEqual(long[1], short[1])

    def test_anchor_bottom_right_keeps_padding(self):
        geometry = anchor_bottom_right(1920, 1080, 600, 300, padding=24)
        self.assertEqual(geometry, "600x300+1296+732")

    def test_theme_uses_distinct_palette(self):
        self.assertNotEqual(THEME.shell, THEME.panel)
        self.assertTrue(THEME.accent.startswith("#"))

    def test_expanded_window_has_known_width(self):
        width, _height = estimate_response_window("abc", expanded=True)
        self.assertEqual(width, 920)

    def test_compact_window_has_known_width(self):
        width, _height = estimate_response_window("abc", expanded=False)
        self.assertEqual(width, 560)


if __name__ == "__main__":
    unittest.main()
