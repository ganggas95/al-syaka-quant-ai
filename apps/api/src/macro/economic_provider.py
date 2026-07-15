"""Economic Event Provider — Menambahkan konteks fundamental ke macro bias.

Menyediakan data event ekonomi terjadwal (FOMC, NFP, CPI, suku bunga)
dan menilai dampaknya terhadap bias makro. Event kalender bersifat
deterministik berdasarkan aturan jadwal yang diketahui (misal NFP
selalu Jumat pertama tiap bulan).
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class EconomicEventType(Enum):
    """Tipe event ekonomi dengan tingkat dampak."""
    FOMC = ("FOMC Meeting", "HIGH")
    NFP = ("Non-Farm Payrolls", "HIGH")
    CPI = ("Consumer Price Index", "HIGH")
    INTEREST_RATE = ("Interest Rate Decision", "HIGH")
    GDP = ("GDP Release", "MEDIUM")
    RETAIL_SALES = ("Retail Sales", "MEDIUM")
    UNEMPLOYMENT = ("Unemployment Rate", "MEDIUM")
    MANUFACTURING_PMI = ("Manufacturing PMI", "MEDIUM")
    SERVICES_PMI = ("Services PMI", "MEDIUM")
    CENTRAL_BANK_SPEECH = ("Central Bank Speech", "LOW")

    def __init__(self, display_name: str, impact: str):
        self.display_name = display_name
        self.impact = impact


@dataclass
class EconomicEvent:
    """Represents a scheduled economic event."""
    event_type: EconomicEventType
    date: date
    country: str = "US"
    description: str = ""
    impact: str = "HIGH"

    def __post_init__(self):
        self.impact = self.event_type.impact

    @property
    def days_until(self) -> int:
        """Days until this event occurs (0 = today)."""
        delta = self.date - date.today()
        return max(0, delta.days)

    @property
    def is_upcoming(self, window_days: int = 7) -> bool:
        """Check if event is within the next N days."""
        return 0 <= self.days_until <= window_days


class EconomicEventProvider:
    """Provider for scheduled economic events and their market impact.

    Maintains a calendar of recurring events computed dynamically
    based on known scheduling patterns (e.g. FOMC ~8x/year, NFP
    on first Friday, etc.).
    """

    # FOMC meeting months (typically 8 per year)
    FOMC_MONTHS = [1, 3, 5, 6, 7, 9, 11, 12]

    # Central bank rate decision frequency (months)
    ECB_MONTHS = [1, 3, 4, 6, 7, 9, 10, 12]
    BOE_MONTHS = [2, 5, 8, 11]
    BOJ_MONTHS = [1, 3, 4, 6, 7, 9, 10, 12]

    def __init__(self, look_ahead_days: int = 14):
        """Initialize provider with look-ahead window.

        Args:
            look_ahead_days: How many days ahead to check for events.
        """
        self.look_ahead_days = look_ahead_days

    def get_upcoming_events(
        self, from_date: Optional[date] = None,
    ) -> list[EconomicEvent]:
        """Get all upcoming events within the look-ahead window."""
        today = from_date or date.today()
        end_date = today + timedelta(days=self.look_ahead_days)
        events: list[EconomicEvent] = []

        for month_offset in range(3):
            year = today.year
            month = today.month + month_offset
            while month > 12:
                month -= 12
                year += 1

            events.extend(self._get_fomc_events(year, month))
            events.extend(self._get_nfp_events(year, month))
            events.extend(self._get_cpi_events(year, month))
            events.extend(self._get_rate_decision_events(year, month))

        return [
            e for e in events
            if today <= e.date <= end_date
        ]

    def get_event_risk_score(
        self, from_date: Optional[date] = None,
    ) -> dict:
        """Calculate event risk score (0-100) based on upcoming events.

        Higher score means more upcoming high-impact events,
        suggesting more uncertainty.
        """
        events = self.get_upcoming_events(from_date)
        if not events:
            return {
                "event_risk_score": 0,
                "high_impact_count": 0,
                "medium_impact_count": 0,
                "upcoming_events": [],
                "has_major_event_soon": False,
            }

        high_count = sum(
            1 for e in events if e.impact == "HIGH"
        )
        medium_count = sum(
            1 for e in events if e.impact == "MEDIUM"
        )
        has_soon = any(
            e.impact == "HIGH" and e.days_until <= 3
            for e in events
        )

        # Score: each HIGH event within 3 days = 25, within 7 = 15
        # Each MEDIUM event within 3 days = 10
        score = 0
        for e in events:
            if e.impact == "HIGH":
                if e.days_until <= 3:
                    score += 25
                elif e.days_until <= 7:
                    score += 15
                else:
                    score += 10
            elif e.impact == "MEDIUM":
                if e.days_until <= 3:
                    score += 10
                elif e.days_until <= 7:
                    score += 5

        return {
            "event_risk_score": min(100, score),
            "high_impact_count": high_count,
            "medium_impact_count": medium_count,
            "upcoming_events": [
                {
                    "name": e.event_type.display_name,
                    "date": e.date.isoformat(),
                    "days_until": e.days_until,
                    "impact": e.impact,
                    "country": e.country,
                }
                for e in sorted(
                    events, key=lambda x: x.date,
                )
            ],
            "has_major_event_soon": has_soon,
        }

    def get_bullish_factors(
        self, from_date: Optional[date] = None,
    ) -> list[str]:
        """Get fundamental factors suggesting bullish macro bias.

        Currently returns empty list — this would be populated
        with actual economic data feeds in production (e.g.
        Fed dovish signals, better-than-expected data).
        """
        return []

    def get_bearish_factors(
        self, from_date: Optional[date] = None,
    ) -> list[str]:
        """Get fundamental factors suggesting bearish macro bias.

        Currently returns empty list — this would be populated
        with actual economic data feeds in production.
        """
        return []

    def _get_fomc_events(
        self, year: int, month: int,
    ) -> list[EconomicEvent]:
        """Get FOMC meeting dates for a given month.

        FOMC meetings are typically scheduled on Tuesday-Wednesday
        in specific months. We use the 2nd full week approximation.
        """
        if month not in self.FOMC_MONTHS:
            return []

        # Approximate: 2nd Wednesday of the month
        cal = calendar.monthcalendar(year, month)
        if len(cal) < 2:
            return []
        second_wed = None
        for week in cal:
            if week[calendar.WEDNESDAY] != 0:
                if second_wed is None:
                    second_wed = week[calendar.WEDNESDAY]
                else:
                    second_wed = week[calendar.WEDNESDAY]
                    break
        if second_wed is None:
            return []

        return [EconomicEvent(
            event_type=EconomicEventType.FOMC,
            date=date(year, month, second_wed),
            country="US",
            description="FOMC monetary policy decision",
        )]

    def _get_nfp_events(
        self, year: int, month: int,
    ) -> list[EconomicEvent]:
        """Get NFP (Non-Farm Payrolls) release date.

        NFP is released on the first Friday of each month.
        """
        cal = calendar.monthcalendar(year, month)
        first_friday = None
        for week in cal:
            if week[calendar.FRIDAY] != 0:
                first_friday = week[calendar.FRIDAY]
                break
        if first_friday is None:
            return []

        return [EconomicEvent(
            event_type=EconomicEventType.NFP,
            date=date(year, month, first_friday),
            country="US",
            description="US employment situation report",
        )]

    def _get_cpi_events(
        self, year: int, month: int,
    ) -> list[EconomicEvent]:
        """Get CPI release date (approximate: 2nd week of month).

        BLS typically releases CPI in the 2nd week.
        We approximate as the Wednesday of the 2nd full week.
        """
        cal = calendar.monthcalendar(year, month)
        if len(cal) < 2:
            return []
        second_wed = None
        for week in cal[1:2]:
            if week[calendar.WEDNESDAY] != 0:
                second_wed = week[calendar.WEDNESDAY]
                break
        if second_wed is None:
            return []

        return [EconomicEvent(
            event_type=EconomicEventType.CPI,
            date=date(year, month, second_wed),
            country="US",
            description="US consumer price index",
        )]

    def _get_rate_decision_events(
        self, year: int, month: int,
    ) -> list[EconomicEvent]:
        """Get central bank rate decision dates (ECB, BOE, BOJ).

        Approximate as 2nd Thursday of the month for ECB/BOJ,
        1st Thursday for BOE.
        """
        events = []
        cal = calendar.monthcalendar(year, month)

        # ECB: 2nd Thursday of the month
        if month in self.ECB_MONTHS:
            second_thu = None
            for week in cal:
                if week[calendar.THURSDAY] != 0:
                    if second_thu is None:
                        second_thu = week[calendar.THURSDAY]
                    else:
                        second_thu = week[calendar.THURSDAY]
                        break
            if second_thu:
                events.append(EconomicEvent(
                    event_type=EconomicEventType.INTEREST_RATE,
                    date=date(year, month, second_thu),
                    country="EU",
                    description="ECB interest rate decision",
                ))

        # BOE: 1st Thursday of the month
        if month in self.BOE_MONTHS:
            first_thu = None
            for week in cal:
                if week[calendar.THURSDAY] != 0:
                    first_thu = week[calendar.THURSDAY]
                    break
            if first_thu:
                events.append(EconomicEvent(
                    event_type=EconomicEventType.INTEREST_RATE,
                    date=date(year, month, first_thu),
                    country="UK",
                    description="BOE interest rate decision",
                ))

        # BOJ: 2nd Thursday of the month
        if month in self.BOJ_MONTHS:
            second_thu = None
            for week in cal:
                if week[calendar.THURSDAY] != 0:
                    if second_thu is None:
                        second_thu = week[calendar.THURSDAY]
                    else:
                        second_thu = week[calendar.THURSDAY]
                        break
            if second_thu:
                events.append(EconomicEvent(
                    event_type=EconomicEventType.INTEREST_RATE,
                    date=date(year, month, second_thu),
                    country="JP",
                    description="BOJ interest rate decision",
                ))

        return events
