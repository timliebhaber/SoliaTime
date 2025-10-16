from __future__ import annotations

import time
from typing import Optional
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QByteArray
from PySide6.QtGui import QAction, QKeySequence
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
        self.setWindowTitle("Timely Time Tracking")

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
        side.addWidget(QLabel("Profiles"))
        side.addWidget(self.profiles_list)
        side.addWidget(self.add_profile_btn)

        # Main area
        main = QVBoxLayout()
        top = QHBoxLayout()
        self.toggle_btn = QPushButton("Start")
        self.elapsed_label = QLabel("00:00:00")
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Note (optional)")
        top.addWidget(self.toggle_btn)
        top.addWidget(self.elapsed_label)
        top.addWidget(self.note_edit, 1)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Profile", "Start", "End", "Duration", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
        self.profiles_list.itemSelectionChanged.connect(self._on_profile_selected)
        self.timer.active_entry_changed.connect(lambda _: self._sync_toggle())
        self.table.itemDoubleClicked.connect(self._on_edit_entry_note)

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
        pid = self.repo.create_profile(name, None)
        self._populate_profiles(select_id=pid)

    def _on_profile_selected(self) -> None:
        self._sync_toggle()
        self._refresh_entries()

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

    def _set_cell(self, row: int, col: int, text: str) -> None:
        self.table.setItem(row, col, QTableWidgetItem(str(text)))

    def _update_elapsed(self) -> None:
        active = self.timer.get_active_entry()
        if not active:
            self.elapsed_label.setText("00:00:00")
            return
        start_s = int(active["start_ts"])  # type: ignore[index]
        dur = int(time.time()) - start_s
        self.elapsed_label.setText(self._fmt_dur(dur))

    @staticmethod
    def _fmt_dur(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

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
        del_act = menu.addAction("Delete Entry")
        act = menu.exec(self.table.viewport().mapToGlobal(pos))
        if act == edit_act:
            self._on_edit_entry_note()
        elif act == del_act:
            row = self.table.currentRow()
            if row >= 0:
                entry = self.repo.list_entries(profile_id=self._current_profile_id())[row]
                self.repo.delete_entry(int(entry["id"]))
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
        self.close()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        # Save window state
        self.settings.geometry = bytes(self.saveGeometry())
        self.settings.window_state = bytes(self.saveState())
        self.settings_store.save(self.settings)
        # Close to tray
        if hasattr(self, "tray") and self.tray and self.tray.isVisible():
            self.hide()
            event.ignore()
            return
        # Prompt if running
        if self.timer.get_active_entry() is not None:
            if QMessageBox.question(self, "Timer running", "A timer is running. Exit? This will not stop the timer.") != QMessageBox.Yes:
                event.ignore()
                return
        super().closeEvent(event)


