"""Dashboard ViewModel - navigation and message log."""
from __future__ import annotations

from calendar import month_abbr
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from src.services.state_service import StateService


class DashboardViewModel(QObject):
    """ViewModel for the dashboard view.

    Handles navigation, dashboard message log, calendar events, and invoice chart data.
    """

    # Navigation signals (middle tiles removed)
    navigate_to_timer = Signal()
    navigate_to_profiles = Signal()
    navigate_to_vat_calculator = Signal()

    # Notify view when messages change
    messages_updated = Signal()
    invoice_data_updated = Signal()
    calendar_events_updated = Signal()

    def __init__(self, state_service: "StateService | None" = None) -> None:
        """Initialize dashboard ViewModel.

        Args:
            state_service: Optional state service for repository access (invoice data).
        """
        super().__init__()
        self._state_service = state_service
        self._messages: list[dict[str, Any]] = []
        self.add_message("SoliaTime initialized successfully", "info")

    def get_messages(self) -> list[dict[str, Any]]:
        """Return a copy of the message history for display.

        Returns:
            List of dicts with keys: text, timestamp, message_type
        """
        return list(self._messages)

    def add_message(self, text: str, message_type: str = "info") -> None:
        """Append a message to the log and notify the view.

        Args:
            text: Message content
            message_type: Optional type (info, warning, error, success)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._messages.append({
            "text": text,
            "timestamp": timestamp,
            "message_type": message_type,
        })
        self.messages_updated.emit()

    def request_navigate_to_timer(self) -> None:
        """Request navigation to timer view."""
        self.navigate_to_timer.emit()

    def request_navigate_to_profiles(self) -> None:
        """Request navigation to profiles view."""
        self.navigate_to_profiles.emit()

    def request_navigate_to_vat_calculator(self) -> None:
        """Request navigation to VAT calculator view."""
        self.navigate_to_vat_calculator.emit()

    def get_calendar_events(self) -> dict[str, str]:
        """Return calendar day annotations with project deadlines.

        Returns:
            Dict mapping YYYY-MM-DD to annotation text (project names with deadlines on that day).
        """
        if not self._state_service:
            return {}
        
        repo = self._state_service.repository
        projects = repo.list_projects()
        events: dict[str, list[str]] = {}
        
        for proj in projects:
            deadline_ts = proj["deadline_ts"]
            if deadline_ts:
                deadline_date = datetime.utcfromtimestamp(deadline_ts).date().isoformat()
                if deadline_date not in events:
                    events[deadline_date] = []
                events[deadline_date].append(proj["name"])
        
        # Format: join multiple project names with newline
        return {date_str: "\n".join(names) for date_str, names in events.items()}

    def get_invoice_chart_data(self) -> list[tuple[str, float, int]]:
        """Return last 12 months of invoice amounts for the chart.

        Amounts are computed from time entries on invoiced projects (invoice_sent or invoice_paid)
        using project service rate. Grouped by month of entry end_ts.

        Returns:
            List of (month_abbr, amount_euros, year) e.g. [("Jan", 150.0, 2026), ...]
        """
        if not self._state_service:
            return self._empty_chart_months()

        repo = self._state_service.repository
        projects = repo.list_projects()
        invoiced = [p for p in projects if p["invoice_sent"] or p["invoice_paid"]]
        if not invoiced:
            return self._empty_chart_months()

        # Build amounts by month (YYYY-MM -> euros)
        month_totals: dict[str, float] = {}
        now = datetime.now()
        for m in range(12):
            d = now - timedelta(days=30 * m)
            key = d.strftime("%Y-%m")
            month_totals[key] = 0.0

        for proj in invoiced:
            rate_cents = proj["rate_cents"] or 0
            if rate_cents <= 0:
                continue
            entries = repo.list_entries(project_id=proj["id"])
            for e in entries:
                start_ts = e["start_ts"]
                end_ts = e["end_ts"]
                if end_ts is None:
                    continue
                duration_sec = end_ts - start_ts
                amount_euros = duration_sec * rate_cents / 3600 / 100
                month_key = datetime.utcfromtimestamp(end_ts).strftime("%Y-%m")
                if month_key in month_totals:
                    month_totals[month_key] += amount_euros

        # Last 12 months in chronological order (oldest first)
        result: list[tuple[str, float, int]] = []
        for i in range(11, -1, -1):
            d = now - timedelta(days=30 * i)
            key = d.strftime("%Y-%m")
            year = d.year
            month_num = d.month
            label = month_abbr[month_num]
            result.append((label, month_totals.get(key, 0.0), year))
        return result

    def _empty_chart_months(self) -> list[tuple[str, float, int]]:
        """Return 12 month labels with zero amounts when no data."""
        result: list[tuple[str, float, int]] = []
        now = datetime.now()
        for i in range(11, -1, -1):
            d = now - timedelta(days=30 * i)
            result.append((month_abbr[d.month], 0.0, d.year))
        return result

