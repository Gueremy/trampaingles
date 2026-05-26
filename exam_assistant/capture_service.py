from __future__ import annotations

import mss
import mss.tools


def capture_full_screen_png(monitor_index: int = 1) -> bytes:
    with mss.MSS() as sct:
        if len(sct.monitors) > monitor_index:
            monitor = sct.monitors[monitor_index]
        elif len(sct.monitors) > 1:
            monitor = sct.monitors[1]
        else:
            monitor = sct.monitors[0]
        screenshot = sct.grab(monitor)
        return mss.tools.to_png(screenshot.rgb, screenshot.size)


def get_dpi_scale() -> float:
    try:
        import ctypes
        awareness = ctypes.c_int()
        ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
        dpi = ctypes.windll.user32.GetDpiForSystem()
        return dpi / 96.0
    except Exception:
        return 1.0


def capture_region_png(coords: tuple[int, int, int, int], dpi_scale: float = 1.0) -> bytes:
    x1, y1, x2, y2 = coords
    s = dpi_scale
    monitor = {"top": int(y1 * s), "left": int(x1 * s), "width": int((x2 - x1) * s), "height": int((y2 - y1) * s)}
    with mss.MSS() as sct:
        screenshot = sct.grab(monitor)
        return mss.tools.to_png(screenshot.rgb, screenshot.size)
