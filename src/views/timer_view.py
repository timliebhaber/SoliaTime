"""Timer view with controls and entries table."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.ui.components import CircularProgress
from src.ui.dialogs import EntryDialog
from src.utils.formatters import format_duration, format_timestamp

if TYPE_CHECKING:
    from src.viewmodels import TimerViewModel


class TimerView(QWidget):
    """Timer view with controls and entries table.
    
    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "TimerViewModel", parent: QWidget | None = None) -> None:
        """Initialize timer view.
        
        Args:
            viewmodel: Timer ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Build the UI components."""
        layout = QVBoxLayout(self)
        
        # Top controls
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
        
        # Entries table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Profile", "Start", "End", "Duration", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        # Delete shortcut
        delete_action = QAction("Delete Selected", self, shortcut=QKeySequence(Qt.Key_Delete))
        delete_action.setShortcutContext(Qt.WidgetShortcut)
        delete_action.triggered.connect(self._on_delete_selected)
        self.table.addAction(delete_action)
        
        layout.addLayout(top)
        layout.addWidget(self.table, 1)

    def _connect_signals(self) -> None:
        """Connect UI and ViewModel signals."""
        # UI → ViewModel
        self.toggle_btn.clicked.connect(self._on_toggle_clicked)
        self.table.itemDoubleClicked.connect(self._on_edit_entry)
        
        # ViewModel → UI
        self.viewmodel.timer_state_changed.connect(self._update_timer_state)
        self.viewmodel.elapsed_updated.connect(self._update_elapsed)
        self.viewmodel.progress_updated.connect(self._update_progress)
        self.viewmodel.entries_changed.connect(self._update_entries_table)
    
    # UI event handlers
    
    def _on_toggle_clicked(self) -> None:
        """Handle toggle button click."""
        note = self.note_edit.text().strip()
        self.viewmodel.toggle_timer(note)
        if not self.viewmodel.is_running:
            self.note_edit.clear()
    
    def _on_edit_entry(self) -> None:
        """Handle entry double-click to edit."""
        row = self.table.currentRow()
        if row < 0:
            return
        
        entry = self.viewmodel.get_entry_by_index(row)
        if not entry:
            return
        
        dlg = EntryDialog(self, note=entry.get("note", ""), tags=entry.get("tags", ""))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            note, tags = dlg.get_values()
            self.viewmodel.update_entry_note_tags(int(entry["id"]), note, tags)
    
    def _on_delete_selected(self) -> None:
        """Handle deletion of selected entries."""
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()})
        if not rows:
            return
        
        count = len(rows)
        reply = QMessageBox.question(
            self,
            "Delete entries",
            f"Delete {count} selected entr{'y' if count == 1 else 'ies'}?",
        )
        if reply != QMessageBox.Yes:
            return
        
        # Get entry IDs
        entry_ids = []
        for row in rows:
            entry = self.viewmodel.get_entry_by_index(row)
            if entry:
                entry_ids.append(int(entry["id"]))
        
        if entry_ids:
            self.viewmodel.delete_entries(entry_ids)
    
    def _show_context_menu(self, pos) -> None:
        """Show context menu for entries table."""
        menu = QMenu(self)
        edit_act = menu.addAction("Edit Note…")
        del_act = menu.addAction("Delete Selected")
        
        act = menu.exec(self.table.viewport().mapToGlobal(pos))
        if act == edit_act:
            self._on_edit_entry()
        elif act == del_act:
            self._on_delete_selected()
    
    # ViewModel update handlers
    
    def _update_timer_state(self, is_running: bool) -> None:
        """Update UI based on timer state.
        
        Args:
            is_running: Whether timer is running
        """
        self.toggle_btn.setText("Stop" if is_running else "Start")
    
    def _update_elapsed(self, seconds: int) -> None:
        """Update elapsed time display.
        
        Args:
            seconds: Elapsed seconds
        """
        self.elapsed_label.setText(format_duration(seconds))
    
    def _update_progress(self, elapsed_seconds: int, target_seconds: int | None) -> None:
        """Update progress display.
        
        Args:
            elapsed_seconds: Total elapsed seconds today
            target_seconds: Target seconds or None
        """
        self.progress.set_values(elapsed_seconds, target_seconds)
        right = format_duration(target_seconds) if target_seconds else "—"
        self.et_label.setText(f"{format_duration(elapsed_seconds)} / {right}")
    
    def _update_entries_table(self, entries: list) -> None:
        """Update entries table with new data.
        
        Args:
            entries: List of entry dicts
        """
        self.table.setRowCount(0)
        now = int(time.time())
        
        for entry in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            start_ts = int(entry["start_ts"]) if entry.get("start_ts") is not None else None
            end_ts = int(entry["end_ts"]) if entry.get("end_ts") is not None else None
            dur = (end_ts or now) - (start_ts or now) if start_ts else 0
            
            self.table.setItem(row, 0, QTableWidgetItem(str(entry.get("profile_name", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(format_timestamp(start_ts or 0)))
            self.table.setItem(row, 2, QTableWidgetItem(format_timestamp(end_ts) if end_ts else "—"))
            self.table.setItem(row, 3, QTableWidgetItem(format_duration(dur)))
            self.table.setItem(row, 4, QTableWidgetItem(str(entry.get("note", ""))))

