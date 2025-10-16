import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from src.services.settings import ensure_app_dirs
from src.models.db import get_connection
from src.models.repository import Repository
from src.services.timer_manager import TimerManager
from src.ui.main_window import MainWindow


def main() -> int:
    ensure_app_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("Solia Time Tracking")
    app.setOrganizationName("Solia")

    # Set window icon (dev and PyInstaller runtimes)
    try:
        # Resolve base path for dev and PyInstaller (_MEIPASS)
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        candidates = [
            base / "ui" / "resources" / "App.ico",
            base / "ui" / "resources" / "app.ico",
            base / "ui" / "resources" / "App.png",
        ]
        for icon_path in candidates:
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                break
    except Exception:
        pass

    conn = get_connection()
    repo = Repository(conn)
    timer = TimerManager(repo)

    window = MainWindow(repository=repo, timer_manager=timer)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


