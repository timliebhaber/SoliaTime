from __future__ import annotations

import time
import sys
from typing import Optional
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QByteArray, QSize
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QStyle,
)
class CircularProgress(QWidget):
    """Non-interactive circular progress displaying elapsed vs target seconds."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._elapsed_seconds: int = 0
        self._target_seconds: int | None = None
        self._size = 64
        self.setMinimumSize(self._size, self._size)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(self._size, self._size)

    def set_values(self, elapsed_seconds: int, target_seconds: int | None) -> None:
        self._elapsed_seconds = max(0, int(elapsed_seconds))
        self._target_seconds = int(target_seconds) if target_seconds is not None else None
        self.update()

    def _ratio(self) -> float:
        if not self._target_seconds or self._target_seconds <= 0:
            return 0.0
        return max(0.0, min(1.0, float(self._elapsed_seconds) / float(self._target_seconds)))

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(4, 4, -4, -4)
        base_pen = QPen(self.palette().mid().color(), 6)
        painter.setPen(base_pen)
        painter.drawEllipse(rect)

        ratio = self._ratio()
        if ratio > 0:
            # Use highlight color for progress arc
            progress_pen = QPen(self.palette().highlight().color(), 6)
            painter.setPen(progress_pen)
            # Start at 90 deg (top) and go clockwise negative angle
            start_angle = 90 * 16
            span_angle = int(-360 * 16 * ratio)
            painter.drawArc(rect, start_angle, span_angle)


from src.models.repository import Repository
from src.services.timer_manager import TimerManager
from src.services.settings import SettingsStore, AppSettings
from src.ui.dialogs import ProfileDialog, EntryDialog
from src.services.exporter import export_csv, export_json


class MainWindow(QMainWindow):
    def __init__(self, repository: Repository, timer_manager: TimerManager) -> None:
        super().__init__()
        self.repo = repository
        self.timer = timer_manager
        self.setWindowTitle("Solia Time Tracking")
        # Ensure the main window explicitly sets its icon for the title bar
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
            candidates = [
                base / "ui" / "resources" / "App.ico",
                base / "ui" / "resources" / "app.ico",
                base / "ui" / "resources" / "App.png",
            ]
            for p in candidates:
                if p.exists():
                    self.setWindowIcon(QIcon(str(p)))
                    break
        except Exception:
            pass

        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()

        self._build_ui()
        self._connect()
        self._populate_profiles()
        self._refresh_entries()

        self._tick = QTimer(self)
        self._tick.setInterval(500)
        self._tick.timeout.connect(self._update_elapsed)
        self._tick.start()

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Profiles sidebar
        side = QVBoxLayout()
        self.profiles_list = QListWidget()
        self.add_profile_btn = QPushButton("Add Profile")
        self.edit_profile_btn = QPushButton("Edit Target…")
        side.addWidget(QLabel("Profiles"))
        side.addWidget(self.profiles_list)
        side.addWidget(self.add_profile_btn)
        side.addWidget(self.edit_profile_btn)
        # Profiles context menu
        self.profiles_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.profiles_list.customContextMenuRequested.connect(self._profiles_context_menu)

        # Main area
        main = QVBoxLayout()
        top = QHBoxLayout()
        self.toggle_btn = QPushButton("Start")
        self.elapsed_label = QLabel("00:00:00")
        self.progress = CircularProgress(self)
        self.et_label = QLabel("— / —")
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Note (optional)")
        top.addWidget(self.toggle_btn)
        top.addWidget(self.elapsed_label)
        top.addWidget(self.progress)
        top.addWidget(self.et_label)
        top.addWidget(self.note_edit, 1)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Profile", "Start", "End", "Duration", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Allow selecting multiple rows for bulk operations
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        main.addLayout(top)
        main.addWidget(self.table, 1)

        layout.addLayout(side, 1)
        layout.addLayout(main, 3)

        # Menu actions minimal
        export_csv_act = QAction("Export CSV", self)
        export_csv_act.triggered.connect(self._export_csv)
        export_json_act = QAction("Export JSON", self)
        export_json_act.triggered.connect(self._export_json)
        self.menuBar().addAction(export_csv_act)
        self.menuBar().addAction(export_json_act)

        # Theme toggle
        self.dark_mode_act = QAction("Dark Mode", self, checkable=True)
        self.dark_mode_act.setChecked((self.settings.theme or "dark") == "dark")
        self.dark_mode_act.triggered.connect(self._apply_theme_from_action)
        self.menuBar().addAction(self.dark_mode_act)

        # Apply theme and restore window state
        self._apply_theme(self.settings.theme)
        if self.settings.geometry:
            self.restoreGeometry(QByteArray(self.settings.geometry))
        if self.settings.window_state:
            self.restoreState(QByteArray(self.settings.window_state))
        # System tray
        self._setup_tray()

    def _connect(self) -> None:
        self.toggle_btn.clicked.connect(self._on_toggle)
        self.add_profile_btn.clicked.connect(self._on_add_profile)
        self.edit_profile_btn.clicked.connect(self._on_edit_profile_target)
        self.profiles_list.itemSelectionChanged.connect(self._on_profile_selected)
        self.timer.active_entry_changed.connect(lambda _: self._sync_toggle())
        self.table.itemDoubleClicked.connect(self._on_edit_entry_note)
        # Delete key for deleting selected profile (list-scoped)
        del_profile_act = QAction("Delete Profile", self, shortcut=QKeySequence(Qt.Key_Delete), triggered=self._on_delete_selected_profile)
        del_profile_act.setShortcutContext(Qt.WidgetShortcut)
        self.profiles_list.addAction(del_profile_act)
        # Delete shortcut for selected entries (table-scoped)
        delete_action = QAction("Delete Selected", self, shortcut=QKeySequence(Qt.Key_Delete), triggered=self._on_delete_selected)
        delete_action.setShortcutContext(Qt.WidgetShortcut)
        self.table.addAction(delete_action)

        # Shortcuts
        toggle_action = QAction("Toggle Timer", self, shortcut=QKeySequence(Qt.Key_Space), triggered=self._on_toggle)
        new_profile_action = QAction("New Profile", self, shortcut=QKeySequence("Ctrl+N"), triggered=self._on_add_profile)
        self.addAction(toggle_action)
        self.addAction(new_profile_action)

    def _current_profile_id(self) -> Optional[int]:
        item = self.profiles_list.currentItem()
        if not item:
            return None
        return int(item.data(Qt.UserRole))

    def _on_add_profile(self) -> None:
        dlg = ProfileDialog(self, title="Create Profile")
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = dlg.get_name()
        if not name:
            return
        target = dlg.get_target_seconds()
        pid = self.repo.create_profile(name, None, target)
        self._populate_profiles(select_id=pid)

    def _on_edit_profile_target(self) -> None:
        pid = self._current_profile_id()
        if pid is None:
            QMessageBox.information(self, "Select profile", "Please select a profile first.")
            return
        prof = self.repo.get_profile(pid)
        current_target = int(prof["target_seconds"]) if prof and prof["target_seconds"] is not None else None
        dlg = ProfileDialog(self, title="Edit Profile Target", name=prof["name"] if prof else "", target_seconds=current_target)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        # Name may be edited in dialog; update if changed
        new_name = dlg.get_name()
        if prof and new_name and new_name != prof["name"]:
            self.repo.rename_profile(pid, new_name)
        target_seconds = dlg.get_target_seconds()
        self.repo.set_profile_target_seconds(pid, target_seconds if target_seconds is not None else None)
        self._populate_profiles(select_id=pid)

    def _on_profile_selected(self) -> None:
        self._sync_toggle()
        self._refresh_entries()
        self._update_progress()

    def _on_toggle(self) -> None:
        pid = self._current_profile_id()
        if pid is None:
            QMessageBox.information(self, "Select profile", "Please select or create a profile first.")
            return
        active = self.timer.get_active_entry()
        if active:
            self.timer.stop()
        else:
            self.timer.start(pid, note=self.note_edit.text().strip())
        self._sync_toggle()
        self._refresh_entries()

    def _sync_toggle(self) -> None:
        active = self.timer.get_active_entry()
        self.toggle_btn.setText("Stop" if active else "Start")
        if hasattr(self, "tray") and self.tray:
            self.tray.setToolTip("Running" if active else "Stopped")

    def _populate_profiles(self, select_id: Optional[int] = None) -> None:
        self.profiles_list.clear()
        profiles = self.repo.list_profiles()
        for row in profiles:
            from PySide6.QtWidgets import QListWidgetItem

            it = QListWidgetItem(row["name"])  # type: ignore[index]
            it.setData(Qt.UserRole, int(row["id"]))
            self.profiles_list.addItem(it)
            if select_id is not None and row["id"] == select_id:
                self.profiles_list.setCurrentItem(it)
        if self.profiles_list.currentRow() == -1 and self.profiles_list.count() > 0:
            self.profiles_list.setCurrentRow(0)
        # Persist last profile
        cur = self._current_profile_id()
        if cur is not None:
            self.settings.last_profile_id = cur
            self.settings_store.save(self.settings)

    def _refresh_entries(self) -> None:
        rows = self.repo.list_entries(profile_id=self._current_profile_id())
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            start_s = int(r["start_ts"]) if r["start_ts"] is not None else None
            end_s = int(r["end_ts"]) if r["end_ts"] is not None else None
            dur = (end_s or int(time.time())) - (start_s or int(time.time())) if start_s else 0
            self._set_cell(row, 0, r["profile_name"])
            self._set_cell(row, 1, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_s or 0)))
            self._set_cell(row, 2, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_s)) if end_s else "—")
            self._set_cell(row, 3, self._fmt_dur(dur))
            self._set_cell(row, 4, r["note"] or "")

        # context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._entries_context_menu)
        self._update_progress()

    def _set_cell(self, row: int, col: int, text: str) -> None:
        self.table.setItem(row, col, QTableWidgetItem(str(text)))

    def _update_elapsed(self) -> None:
        active = self.timer.get_active_entry()
        if not active:
            self.elapsed_label.setText("00:00:00")
            self._update_progress()
            return
        start_s = int(active["start_ts"])  # type: ignore[index]
        dur = int(time.time()) - start_s
        self.elapsed_label.setText(self._fmt_dur(dur))
        self._update_progress()

    @staticmethod
    def _fmt_dur(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _compute_elapsed_today_seconds(self, profile_id: Optional[int]) -> int:
        if profile_id is None:
            return 0
        now = int(time.time())
        lt = time.localtime(now)
        midnight = int(time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, lt.tm_wday, lt.tm_yday, lt.tm_isdst)))
        total = 0
        rows = self.repo.list_entries(profile_id=profile_id)
        for r in rows:
            start_ts = int(r["start_ts"]) if r["start_ts"] is not None else None
            end_ts = int(r["end_ts"]) if r["end_ts"] is not None else now
            if start_ts is None:
                continue
            start = max(start_ts, midnight)
            end = min(end_ts, now)
            if end > start:
                total += end - start
        return total

    def _update_progress(self) -> None:
        pid = self._current_profile_id()
        elapsed = self._compute_elapsed_today_seconds(pid)
        target: Optional[int] = None
        if pid is not None:
            prof = self.repo.get_profile(pid)
            if prof and prof["target_seconds"] is not None:
                target = int(prof["target_seconds"])  # type: ignore[index]
        self.progress.set_values(elapsed, target)
        right = self._fmt_dur(target) if target else "—"
        self.et_label.setText(f"{self._fmt_dur(elapsed)} / {right}")

    def _prompt_text(self, title: str, label: str) -> Optional[str]:
        from PySide6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(self, title, label)
        return text.strip() if ok and text.strip() else None

    def _export_csv(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "timely_export.csv", "CSV Files (*.csv)")
        if not path:
            return
        export_csv(self.repo, Path(path), profile_id=self._current_profile_id())

    def _export_json(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON", "timely_export.json", "JSON Files (*.json)")
        if not path:
            return
        export_json(self.repo, Path(path), profile_id=self._current_profile_id())

    def _on_edit_entry_note(self) -> None:
        item = self.table.currentRow()
        if item < 0:
            return
        entry_row = self.repo.list_entries(profile_id=self._current_profile_id())[item]
        dlg = EntryDialog(self, note=entry_row["note"] or "", tags=entry_row["tags"] or "")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            note, tags = dlg.get_values()
            self.repo.update_entry_note_tags(int(entry_row["id"]), note, tags)
            self._refresh_entries()

    def _entries_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        edit_act = menu.addAction("Edit Note…")
        del_act = menu.addAction("Delete Selected")
        act = menu.exec(self.table.viewport().mapToGlobal(pos))
        if act == edit_act:
            self._on_edit_entry_note()
        elif act == del_act:
            self._on_delete_selected()

    def _profiles_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu
        item = self.profiles_list.itemAt(pos)
        if item is None:
            return
        menu = QMenu(self)
        del_act = menu.addAction("Delete Profile")
        act = menu.exec(self.profiles_list.viewport().mapToGlobal(pos))
        if act == del_act:
            self._on_delete_selected_profile()

    def _on_delete_selected_profile(self) -> None:
        item = self.profiles_list.currentItem()
        if item is None:
            return
        profile_id = int(item.data(Qt.UserRole))
        # If timer is running for this profile, prompt to stop
        active = self.timer.get_active_entry()
        if active is not None and int(active["profile_id"]) == profile_id:
            if QMessageBox.question(self, "Timer running", "Timer is running for this profile. Stop and delete?") != QMessageBox.Yes:
                return
            self.timer.stop()
        # Confirm cascade
        if QMessageBox.question(self, "Delete profile", "Delete this profile and all its time entries?") != QMessageBox.Yes:
            return
        self.repo.delete_profile(profile_id)
        self._populate_profiles()
        self._refresh_entries()

    def _on_delete_selected(self) -> None:
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()})
        if not rows:
            return
        count = len(rows)
        if QMessageBox.question(self, "Delete entries", f"Delete {count} selected entr{'y' if count == 1 else 'ies'}?") != QMessageBox.Yes:
            return
        # Resolve entry IDs corresponding to current filter (profile)
        entries = self.repo.list_entries(profile_id=self._current_profile_id())
        ids = [int(entries[r]["id"]) for r in rows if 0 <= r < len(entries)]
        # Perform deletion
        if len(ids) == 1:
            self.repo.delete_entry(ids[0])
        else:
            self.repo.delete_entries(ids)
        self._refresh_entries()

    def _apply_theme_from_action(self) -> None:
        theme = "dark" if self.dark_mode_act.isChecked() else "light"
        self._apply_theme(theme)
        self.settings.theme = theme
        self.settings_store.save(self.settings)

    def _apply_theme(self, theme: str | None) -> None:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return
        app.setStyle("Fusion")
        if (theme or "dark") == "dark":
            from PySide6.QtGui import QPalette, QColor
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
        else:
            app.setPalette(app.style().standardPalette())

    def _setup_tray(self) -> None:
        from PySide6.QtWidgets import QSystemTrayIcon, QMenu
        self.tray = QSystemTrayIcon(self)
        # Align tray icon with window icon if available
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
            candidates = [
                base / "ui" / "resources" / "App.ico",
                base / "ui" / "resources" / "app.ico",
                base / "ui" / "resources" / "App.png",
            ]
            icon_to_use: Optional[QIcon] = None
            for p in candidates:
                if p.exists():
                    icon_to_use = QIcon(str(p))
                    break
            if icon_to_use is not None:
                self.tray.setIcon(icon_to_use)
            else:
                self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        except Exception:
            self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray.setToolTip("Stopped")
        menu = QMenu()
        toggle = menu.addAction("Start/Stop")
        show = menu.addAction("Show")
        quit_act = menu.addAction("Quit")
        toggle.triggered.connect(self._on_toggle)
        show.triggered.connect(self.showNormal)
        quit_act.triggered.connect(self._on_quit_requested)
        self.tray.setContextMenu(menu)
        self.tray.setVisible(True)

    def _on_quit_requested(self) -> None:
        if self.timer.get_active_entry() is not None:
            if QMessageBox.question(self, "Timer running", "A timer is running. Quit anyway?") != QMessageBox.Yes:
                return
        # Ensure clean shutdown
        try:
            self._tick.stop()
        except Exception:
            pass
        try:
            if hasattr(self, "tray") and self.tray:
                self.tray.setVisible(False)
                self.tray.hide()
                self.tray.deleteLater()
        except Exception:
            pass
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            app.quit()
        else:
            self.close()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        # Save window state
        self.settings.geometry = bytes(self.saveGeometry())
        self.settings.window_state = bytes(self.saveState())
        self.settings_store.save(self.settings)
        # Prompt if running
        if self.timer.get_active_entry() is not None:
            if QMessageBox.question(self, "Timer running", "A timer is running. Exit? This will not stop the timer.") != QMessageBox.Yes:
                event.ignore()
                return
        # Stop timers and clean up tray so process can exit
        try:
            self._tick.stop()
        except Exception:
            pass
        try:
            if hasattr(self, "tray") and self.tray:
                self.tray.setVisible(False)
                self.tray.hide()
                self.tray.deleteLater()
        except Exception:
            pass
        super().closeEvent(event)


