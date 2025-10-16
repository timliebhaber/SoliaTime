# Timely Time Tracking

Windows desktop time tracker built with PySide6. Profiles, start/stop toggle, history, CSV export, tray, and dark mode.

## Dev

1. Install Python 3.10+
2. Install deps:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python -m src.app
   ```

## Build (Windows .exe)

```bash
pyinstaller --onefile --noconsole --icon src/ui/resources/app.ico --name Timely src/app.py
```

Outputs `dist/Timely.exe`.
Time Tracking Software
