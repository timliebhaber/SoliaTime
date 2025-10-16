import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.services.settings import ensure_app_dirs
from src.models.db import get_connection
from src.models.repository import Repository
from src.services.timer_manager import TimerManager
from src.ui.main_window import MainWindow


def main() -> int:
    ensure_app_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("Timely Time Tracking")
    app.setOrganizationName("Timely")

    conn = get_connection()
    repo = Repository(conn)
    timer = TimerManager(repo)

    window = MainWindow(repository=repo, timer_manager=timer)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


