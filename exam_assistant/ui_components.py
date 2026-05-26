from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class UITheme:
    shell: str = "#08111f"
    panel: str = "#10233d"
    panel_alt: str = "#0c1a2e"
    accent: str = "#6ff7c8"
    accent_warm: str = "#ffd166"
    text: str = "#edf6ff"
    muted: str = "#8aa1bd"
    border: str = "#21486f"
    danger: str = "#ff6b6b"


THEME = UITheme()


def estimate_response_window(text: str, expanded: bool = False) -> tuple[int, int]:
    lines = max(10, min(30 if not expanded else 48, text.count("\n") + (len(text) // 72) + 6))
    width = 560 if not expanded else 920
    height = 280 if not expanded else 640
    return width, max(height, lines * 18)


def anchor_bottom_left(screen_width: int, screen_height: int, width: int, height: int, padding: int = 24) -> str:
    return f"{width}x{height}+{padding}+{screen_height - height - padding - 24}"


class RegionSelector:
    def __init__(self, parent, callback: Callable[[tuple[int, int, int, int] | None], None]):
        self.callback = callback
        self.start_x = self.start_y = 0
        self.rect = None
        self._called = False

        self.root = tk.Toplevel(parent)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#04101a")
        self.root.overrideredirect(True)

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="#04101a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self._on_close)

        sw = self.root.winfo_screenwidth()
        self.canvas.create_rectangle(40, 24, sw - 40, 72, fill=THEME.panel_alt, outline=THEME.border, width=2)
        self.canvas.create_text(
            sw // 2,
            48,
            text="Drag to scan a region • Release to capture • ESC to cancel",
            fill=THEME.text,
            font=("Segoe UI Semibold", 14),
        )

    def _on_close(self, _event=None):
        if not self._called:
            self._called = True
            self.callback(None)
        self.root.destroy()

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)

    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            event.x,
            event.y,
            outline=THEME.accent,
            width=3,
            fill=THEME.accent,
            stipple="gray25",
        )

    def on_release(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        if not self._called:
            self._called = True
            self.callback((x1, y1, x2, y2) if x2 - x1 > 10 and y2 - y1 > 10 else None)
        self.root.destroy()


class ResponseOverlay:
    def __init__(self, parent, text: str, source: str = ""):
        self.source = source
        self.text = text
        self.expanded = False

        self.root = tk.Toplevel(parent)
        self.root.title("Exam Assistant")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=THEME.shell)
        self.root.resizable(True, True)
        self.root.minsize(520, 260)

        self._build_shell()
        self._populate_text()
        self._apply_geometry()
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

    def _build_shell(self):
        self.frame = tk.Frame(self.root, bg=THEME.shell, padx=2, pady=2)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.panel = tk.Frame(self.frame, bg=THEME.panel, highlightbackground=THEME.border, highlightthickness=1)
        self.panel.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self.panel, bg=THEME.panel_alt, padx=14, pady=10)
        header.pack(fill=tk.X)

        title_wrap = tk.Frame(header, bg=THEME.panel_alt)
        title_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(title_wrap, text="Exam Assistant", bg=THEME.panel_alt, fg=THEME.text, font=("Bahnschrift SemiBold", 14)).pack(anchor="w")
        subtitle = self.source or "Live answer"
        tk.Label(title_wrap, text=subtitle, bg=THEME.panel_alt, fg=THEME.muted, font=("Segoe UI", 9)).pack(anchor="w")

        controls = tk.Frame(header, bg=THEME.panel_alt)
        controls.pack(side=tk.RIGHT)
        self.expand_btn = self._chip_button(controls, "Expand", self._toggle_expand, THEME.accent_warm)
        self.expand_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.copy_btn = self._chip_button(controls, "Copy", lambda: self._copy(self.text), THEME.accent)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.close_btn = self._chip_button(controls, "Close", self.root.destroy, THEME.danger)
        self.close_btn.pack(side=tk.LEFT)

        content = tk.Frame(self.panel, bg=THEME.panel, padx=16, pady=14)
        content.pack(fill=tk.BOTH, expand=True)
        self.text_widget = tk.Text(
            content,
            bg=THEME.panel,
            fg=THEME.text,
            insertbackground=THEME.accent,
            selectbackground="#1d4d6b",
            relief=tk.FLAT,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            padx=4,
            pady=4,
            undo=False,
        )
        scrollbar = tk.Scrollbar(content, command=self.text_widget.yview, troughcolor=THEME.panel_alt, bg=THEME.panel_alt, activebackground=THEME.border)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        footer = tk.Frame(self.panel, bg=THEME.panel_alt, padx=14, pady=8)
        footer.pack(fill=tk.X)
        tk.Label(
            footer,
            text="Tip: drag the window or use Expand for long analyses",
            bg=THEME.panel_alt,
            fg=THEME.muted,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

    def _chip_button(self, parent, label: str, command: Callable[[], None], accent: str):
        button = tk.Label(
            parent,
            text=label,
            bg=THEME.panel,
            fg=accent,
            font=("Consolas", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=4,
            highlightbackground=accent,
            highlightthickness=1,
        )
        button.bind("<Button-1>", lambda _event: command())
        return button

    def _populate_text(self):
        self.text_widget.delete("1.0", tk.END)
        
        self.text_widget.tag_config("analysis", foreground=THEME.muted, font=("Segoe UI", 10))
        self.text_widget.tag_config("answer", foreground=THEME.accent, font=("Segoe UI", 12, "bold"))
        
        self.text_widget.insert(tk.END, self.text)
        
        start_idx = "1.0"
        while True:
            pos = self.text_widget.search(r"\[AN[AÁ]LISIS\]", start_idx, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end_pos = self.text_widget.search(r"(?i)(✅.*RESPUESTA FINAL|RESPUESTA FINAL|Respuesta Final)", pos, stopindex=tk.END, regexp=True)
            if not end_pos:
                self.text_widget.tag_add("analysis", pos, tk.END)
                break
            self.text_widget.tag_add("analysis", pos, end_pos)
            next_pos = self.text_widget.search(r"\[AN[AÁ]LISIS\]", end_pos + "+1c", stopindex=tk.END, regexp=True)
            if next_pos:
                self.text_widget.tag_add("answer", end_pos, next_pos)
                start_idx = next_pos
            else:
                self.text_widget.tag_add("answer", end_pos, tk.END)
                break

        self.text_widget.configure(state=tk.DISABLED)

    def _copy(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def _toggle_expand(self):
        self.expanded = not self.expanded
        self.expand_btn.configure(text="Compact" if self.expanded else "Expand")
        self._apply_geometry()

    def _apply_geometry(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        width, height = estimate_response_window(self.text, self.expanded)
        self.root.geometry(anchor_bottom_left(sw, sh, width, height))


class StreamingResponseOverlay:
    """Response overlay that accepts incremental text chunks."""

    def __init__(self, parent, source: str = ""):
        self.source = source
        self._full_text = ""
        self.expanded = False

        self.root = tk.Toplevel(parent)
        self.root.title("Exam Assistant")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=THEME.shell)
        self.root.resizable(True, True)
        self.root.minsize(520, 260)

        self._build_shell()
        self._apply_geometry("")
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

    def _build_shell(self):
        self.frame = tk.Frame(self.root, bg=THEME.shell, padx=2, pady=2)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.panel = tk.Frame(self.frame, bg=THEME.panel, highlightbackground=THEME.border, highlightthickness=1)
        self.panel.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self.panel, bg=THEME.panel_alt, padx=14, pady=10)
        header.pack(fill=tk.X)
        title_wrap = tk.Frame(header, bg=THEME.panel_alt)
        title_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(title_wrap, text="Exam Assistant", bg=THEME.panel_alt, fg=THEME.text, font=("Bahnschrift SemiBold", 14)).pack(anchor="w")
        subtitle = self.source or "Live answer"
        tk.Label(title_wrap, text=subtitle, bg=THEME.panel_alt, fg=THEME.muted, font=("Segoe UI", 9)).pack(anchor="w")

        controls = tk.Frame(header, bg=THEME.panel_alt)
        controls.pack(side=tk.RIGHT)
        close_btn = tk.Label(controls, text="Close", bg=THEME.panel, fg=THEME.danger, font=("Consolas", 9, "bold"), cursor="hand2", padx=10, pady=4, highlightbackground=THEME.danger, highlightthickness=1)
        close_btn.bind("<Button-1>", lambda _e: self.root.destroy())
        close_btn.pack(side=tk.LEFT)

        content = tk.Frame(self.panel, bg=THEME.panel, padx=16, pady=14)
        content.pack(fill=tk.BOTH, expand=True)
        self.text_widget = tk.Text(content, bg=THEME.panel, fg=THEME.text, insertbackground=THEME.accent, selectbackground="#1d4d6b", relief=tk.FLAT, wrap=tk.WORD, font=("Segoe UI", 11), padx=4, pady=4, undo=False)
        scrollbar = tk.Scrollbar(content, command=self.text_widget.yview, troughcolor=THEME.panel_alt, bg=THEME.panel_alt, activebackground=THEME.border)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def append(self, chunk: str) -> None:
        self._full_text += chunk
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, chunk)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)

    def _apply_geometry(self, text: str):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        width, height = estimate_response_window(text or " " * 40)
        self.root.geometry(anchor_bottom_left(sw, sh, width, height))


def _win_screen_size() -> tuple[int, int]:
    try:
        import ctypes
        u = ctypes.windll.user32
        u.SetProcessDPIAware()
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080


class CompactResponseOverlay:
    """Minimal semi-transparent text panel near bottom-right. Alt+R or click to toggle."""

    def __init__(self, parent, text: str, on_close: "Callable[[], None] | None" = None):
        sw, sh = _win_screen_size()
        self._on_close = on_close

        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.92)
        self.root.configure(bg=THEME.shell)

        panel = tk.Frame(self.root, bg=THEME.panel, highlightbackground=THEME.border, highlightthickness=1, padx=12, pady=10)
        panel.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(
            panel,
            bg=THEME.panel,
            fg=THEME.text,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            wrap=tk.WORD,
            width=42,
            height=min(18, max(4, text.count("\n") + len(text) // 72 + 2)),
            padx=4,
            pady=4,
            insertbackground=THEME.accent,
        )
        sb = tk.Scrollbar(panel, command=txt.yview, troughcolor=THEME.panel_alt, bg=THEME.panel_alt, width=6)
        txt.configure(yscrollcommand=sb.set)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        txt.tag_config("analysis", foreground=THEME.muted, font=("Segoe UI", 9))
        txt.tag_config("answer", foreground=THEME.accent, font=("Segoe UI", 11, "bold"))
        
        txt.insert(tk.END, text)
        
        start_idx = "1.0"
        while True:
            pos = txt.search(r"\[AN[AÁ]LISIS\]", start_idx, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end_pos = txt.search(r"(?i)(✅.*RESPUESTA FINAL|RESPUESTA FINAL|Respuesta Final)", pos, stopindex=tk.END, regexp=True)
            if not end_pos:
                txt.tag_add("analysis", pos, tk.END)
                break
            txt.tag_add("analysis", pos, end_pos)
            next_pos = txt.search(r"\[AN[AÁ]LISIS\]", end_pos + "+1c", stopindex=tk.END, regexp=True)
            if next_pos:
                txt.tag_add("answer", end_pos, next_pos)
                start_idx = next_pos
            else:
                txt.tag_add("answer", end_pos, tk.END)
                break

        txt.configure(state=tk.DISABLED)

        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        self.root.geometry(f"+8+{sh - h - 72}")

        self.root.bind("<Escape>", lambda _e: self.close())
        txt.bind("<Button-3>", lambda _e: self.close())
        
        self._drag_data = {"x": 0, "y": 0}
        panel.bind("<ButtonPress-1>", self._start_drag)
        panel.bind("<B1-Motion>", self._on_drag)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() - self._drag_data["x"] + event.x
        y = self.root.winfo_y() - self._drag_data["y"] + event.y
        self.root.geometry(f"+{x}+{y}")

    def close(self):
        if self._on_close:
            self._on_close()
        try:
            self.root.destroy()
        except Exception:
            pass

    def is_open(self) -> bool:
        try:
            return bool(self.root.winfo_exists())
        except Exception:
            return False


class CompactInputOverlay:
    """Slim single-line input near bottom-right. Enter submits, Escape cancels."""

    def __init__(self, parent, callback: "Callable[[str | None], None]"):
        sw, sh = _win_screen_size()
        self._callback = callback
        self._called = False

        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.root.configure(bg=THEME.shell)

        panel = tk.Frame(self.root, bg=THEME.panel, highlightbackground=THEME.accent, highlightthickness=1, padx=8, pady=6)
        panel.pack(fill=tk.BOTH, expand=True)

        self._entry = tk.Entry(
            panel,
            bg=THEME.panel,
            fg=THEME.text,
            insertbackground=THEME.accent,
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            width=34,
        )
        self._entry.pack(fill=tk.X)
        self._entry.focus_set()

        self.root.bind("<Return>", lambda _e: self._submit())
        self.root.bind("<Escape>", lambda _e: self._cancel())

        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        self.root.geometry(f"+8+{sh - h - 72}")
        
        self._drag_data = {"x": 0, "y": 0}
        panel.bind("<ButtonPress-1>", self._start_drag)
        panel.bind("<B1-Motion>", self._on_drag)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() - self._drag_data["x"] + event.x
        y = self.root.winfo_y() - self._drag_data["y"] + event.y
        self.root.geometry(f"+{x}+{y}")

    def _submit(self):
        if not self._called:
            self._called = True
            text = self._entry.get().strip()
            self._callback(text or None)
        self.root.destroy()

    def _cancel(self):
        if not self._called:
            self._called = True
            self._callback(None)
        self.root.destroy()


class StatusLights:
    """Persistent bottom-right two-dot indicator: processing (left) and ready (right)."""

    @staticmethod
    def _screen_size() -> tuple[int, int]:
        try:
            import ctypes
            u = ctypes.windll.user32
            u.SetProcessDPIAware()
            return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
        except Exception:
            pass
        return 1920, 1080

    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.88)
        self.root.configure(bg=THEME.shell)

        W, H = 48, 20
        sw, sh = self._screen_size()
        x = 8
        y = sh - H - 48
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        frame = tk.Frame(self.root, bg=THEME.shell, padx=4, pady=3)
        frame.pack(fill=tk.BOTH, expand=True)

        self._c1 = tk.Canvas(frame, width=10, height=10, bg=THEME.shell, highlightthickness=0)
        self._c1.pack(side=tk.LEFT, padx=(0, 4))
        self._c2 = tk.Canvas(frame, width=10, height=10, bg=THEME.shell, highlightthickness=0)
        self._c2.pack(side=tk.LEFT)

        self._dot1 = self._c1.create_oval(1, 1, 9, 9, fill="#3a3a4a", outline="")
        self._dot2 = self._c2.create_oval(1, 1, 9, 9, fill="#3a3a4a", outline="")
        print(f"[LIGHTS] placed at +{x}+{y} (screen {sw}x{sh})")

        self._pulse_step = 0
        self._pulsing = False
        self._on_click: Callable[[], None] = lambda: None

        self.root.bind("<Button-1>", lambda _e: self._on_click())
        frame.bind("<Button-1>", lambda _e: self._on_click())
        self._c1.bind("<Button-1>", lambda _e: self._on_click())
        self._c2.bind("<Button-1>", lambda _e: self._on_click())

    def set_click_handler(self, fn: Callable[[], None]) -> None:
        self._on_click = fn

    def set_processing(self, active: bool) -> None:
        self._pulsing = active
        if not active:
            self._c1.itemconfig(self._dot1, fill="#3a3a4a")
        else:
            self._pulse_step = 0
            self._pulse()

    def _pulse(self) -> None:
        if not self._pulsing:
            return
        colors = ["#e07a00", "#f5a623", "#ffb74d", "#f5a623"]
        color = colors[self._pulse_step % len(colors)]
        self._c1.itemconfig(self._dot1, fill=color)
        self._pulse_step += 1
        if self.root.winfo_exists():
            self.root.after(300, self._pulse)

    def set_ready(self, ready: bool) -> None:
        color = "#6ff7c8" if ready else "#3a3a4a"
        self._c2.itemconfig(self._dot2, fill=color)


class LoadingOverlay:
    def __init__(self, parent, message="Analyzing..."):
        self.message = message
        self.frame_index = 0
        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg=THEME.shell)

        shell = tk.Frame(self.root, bg=THEME.shell, padx=2, pady=2)
        shell.pack()
        panel = tk.Frame(shell, bg=THEME.panel_alt, padx=18, pady=14, highlightbackground=THEME.border, highlightthickness=1)
        panel.pack()
        self.label = tk.Label(panel, text=message, bg=THEME.panel_alt, fg=THEME.text, font=("Bahnschrift SemiBold", 11))
        self.label.pack()
        self.hint = tk.Label(panel, text="Scanning screen and context", bg=THEME.panel_alt, fg=THEME.muted, font=("Segoe UI", 9))
        self.hint.pack(pady=(4, 0))

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        self.root.geometry(anchor_bottom_left(sw, sh, width, height))
        self._pulse()

    def _pulse(self):
        dots = "." * (self.frame_index % 4)
        self.label.configure(text=f"{self.message}{dots}")
        self.frame_index += 1
        if self.root.winfo_exists():
            self.root.after(450, self._pulse)

    def close(self):
        try:
            self.root.destroy()
        except Exception:
            pass


class AskQuestionPopup:
    def __init__(
        self,
        parent,
        callback: Callable[[str | None], None],
        title: str = "Manual Prompt",
        hint: str = "Use /all, /one or /followup before your instruction",
    ):
        self.callback = callback
        self._called = False
        self.root = tk.Toplevel(parent)
        self.root.title("Ask AI")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=THEME.shell)
        self.root.resizable(True, True)
        self.root.minsize(460, 180)

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        width, height = 560, 220
        self.root.geometry(f"{width}x{height}+{(sw - width) // 2}+{(sh - height) // 2}")

        shell = tk.Frame(self.root, bg=THEME.shell, padx=2, pady=2)
        shell.pack(fill=tk.BOTH, expand=True)
        panel = tk.Frame(shell, bg=THEME.panel, highlightbackground=THEME.border, highlightthickness=1)
        panel.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(panel, bg=THEME.panel_alt, padx=16, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text=title, bg=THEME.panel_alt, fg=THEME.text, font=("Bahnschrift SemiBold", 14)).pack(anchor="w")
        tk.Label(header, text=hint, bg=THEME.panel_alt, fg=THEME.muted, font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(panel, bg=THEME.panel, padx=16, pady=14)
        body.pack(fill=tk.BOTH, expand=True)
        self.entry = tk.Text(
            body,
            bg=THEME.panel,
            fg=THEME.text,
            insertbackground=THEME.accent,
            relief=tk.FLAT,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            height=4,
        )
        self.entry.pack(fill=tk.BOTH, expand=True)
        self.entry.focus_set()

        footer = tk.Frame(panel, bg=THEME.panel_alt, padx=16, pady=10)
        footer.pack(fill=tk.X)
        self.send_btn = self._chip_button(footer, "Send", self._submit, THEME.accent)
        self.send_btn.pack(side=tk.RIGHT)
        self.cancel_btn = self._chip_button(footer, "Cancel", self._on_close, THEME.danger)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))
        tk.Label(footer, text="Ctrl+Enter sends • Esc cancels", bg=THEME.panel_alt, fg=THEME.muted, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.root.bind("<Escape>", self._on_close)
        self.root.bind("<Control-Return>", lambda _event: self._submit())

    def _chip_button(self, parent, label: str, command: Callable[[], None], accent: str):
        button = tk.Label(
            parent,
            text=label,
            bg=THEME.panel,
            fg=accent,
            font=("Consolas", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=4,
            highlightbackground=accent,
            highlightthickness=1,
        )
        button.bind("<Button-1>", lambda _event: command())
        return button

    def _on_close(self, _event=None):
        if not self._called:
            self._called = True
            self.callback(None)
        self.root.destroy()

    def _submit(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not self._called:
            self._called = True
            self.callback(text or None)
        self.root.destroy()


def show_notification(parent, message: str):
    root = tk.Toplevel(parent)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.96)
    root.configure(bg=THEME.shell)
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    shell = tk.Frame(root, bg=THEME.shell, padx=2, pady=2)
    shell.pack()
    panel = tk.Frame(shell, bg=THEME.panel_alt, padx=16, pady=10, highlightbackground=THEME.border, highlightthickness=1)
    panel.pack()
    tk.Label(panel, text=message, bg=THEME.panel_alt, fg=THEME.text, font=("Segoe UI Semibold", 10)).pack()

    root.update_idletasks()
    width, height = root.winfo_reqwidth(), root.winfo_reqheight()
    root.geometry(anchor_bottom_left(sw, sh, width, height))
    root.after(2600, root.destroy)


def show_setup_error():
    root = tk.Tk()
    root.title("Setup Required")
    root.geometry("460x240")
    root.configure(bg=THEME.shell)

    shell = tk.Frame(root, bg=THEME.shell, padx=2, pady=2)
    shell.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
    panel = tk.Frame(shell, bg=THEME.panel, highlightbackground=THEME.border, highlightthickness=1)
    panel.pack(fill=tk.BOTH, expand=True)
    tk.Label(panel, text="API key missing", bg=THEME.panel, fg=THEME.danger, font=("Bahnschrift SemiBold", 16)).pack(pady=(24, 10))
    tk.Label(panel, text="Create config.env with:\nOPENROUTER_API_KEY=...", bg=THEME.panel, fg=THEME.text, font=("Segoe UI", 11)).pack()
    tk.Button(panel, text="Close", command=root.destroy, width=12, bg=THEME.accent, fg="#00161b", relief=tk.FLAT).pack(pady=24)
    root.mainloop()


def create_tray_icon(app):
    try:
        import pystray
        from PIL import Image, ImageDraw, ImageFont

        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle([6, 6, 58, 58], radius=18, fill=THEME.panel)
        draw.ellipse([12, 12, 52, 52], fill=THEME.accent)
        draw.text((22, 20), "A", fill="#08202a", font=ImageFont.load_default())

        def on_quit(icon, _item):
            icon.stop()
            app.shutdown()

        def on_clear_context(_icon, _item):
            app.context.clear()
            app.notify("Global memory cleared")

        def on_status(_icon, _item):
            app.notify(f"Context: {app.context.count()} | Audio: {'ON' if app.audio_active else 'OFF'}")

        menu = pystray.Menu(
            pystray.MenuItem("Status", on_status),
            pystray.MenuItem("Clear memory", on_clear_context),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit),
        )
        icon = pystray.Icon("exam_ai", image, "AI Exam Assistant", menu)
        app._tray_icon = icon
        icon.run()
    except Exception as exc:
        print(f"Tray icon error: {exc}")
