"""
Build script — generates exam_assistant.exe using PyInstaller
Run this on your Windows machine: python build.py
"""
import subprocess
import sys
import os
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def build():
    print("📦 Installing dependencies...")
    deps = [
        "keyboard",
        "mss",
        "openai",
        "pyperclip",
        "pystray",
        "pillow",
        "faster-whisper",
        "soundcard",
        "numpy",
        "pyinstaller"
    ]
    subprocess.run([sys.executable, "-m", "pip", "install"] + deps, check=True)

    print("\n🔨 Building .exe...")
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",                    # No console window
        "--name", "ExamAssistant",
        "--icon", "NONE",
        "--hidden-import", "openai",
        "--hidden-import", "faster_whisper",
        "--hidden-import", "soundcard",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--hidden-import", "mss",
        "--hidden-import", "keyboard",
        "--hidden-import", "pyperclip",
        "--collect-all", "faster_whisper",
        "--collect-all", "openai",
        "main.py"
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        exe_path = Path("dist") / "ExamAssistant.exe"
        print(f"\n✅ Build complete! → {exe_path.absolute()}")
        print("\nNext steps:")
        print("1. Copy ExamAssistant.exe to a folder")
        print("2. Create config.env in the same folder:")
        print("   OPENROUTER_API_KEY=your_key_here")
        print("   AI_MODEL=your_model_here")
        print("   AI_BASE_URL=https://openrouter.ai/api/v1")
        print("3. Run ExamAssistant.exe")
        print("\nHotkeys:")
        print("   Alt+F = Full screen + question")
        print("   Alt+S = Screenshot region")
        print("   Alt+I = Manual question")
        print("   Alt+T = Selected text")
        print("   Alt+A = Toggle audio capture")
        print("   Alt+C = Clear context")
        print("   Alt+Q = Quit")
    else:
        print("❌ Build failed. Check errors above.")

if __name__ == "__main__":
    build()
