from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    def __init__(self, message: str, *, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@dataclass(frozen=True)
class DataPaths:
    prices: Path
    alt_prices: Path
    events: Path
    change_points: Path


class DateParser:
    def parse(self, value: str | None) -> date | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None

        # Fast path: ISO-like values (YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS)
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
        except ValueError:
            pass

        for fmt in (
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%d-%b-%y",
            "%d-%b-%Y",
        ):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None


class CsvTable:
    def __init__(self, path: Path):
        self.path = path

    def read_rows(self) -> list[dict[str, str]]:
        try:
            with self.path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                return [dict(row) for row in reader]
        except (OSError, csv.Error) as exc:
            raise ValidationError(f"Failed to read CSV: {exc}") from exc


class PriceService:
    def __init__(self, paths: DataPaths, date_parser: DateParser):
        self.paths = paths
        self.date_parser = date_parser

    def _select_prices_path(self) -> Path:
        return self.paths.prices if self.paths.prices.exists() else self.paths.alt_prices

    def parse_query_dates(self, start_raw: str | None, end_raw: str | None) -> tuple[date | None, date | None]:
        start = self._parse_query_date("start", start_raw)
        end = self._parse_query_date("end", end_raw)
        if start and end and start > end:
            raise ValidationError("Invalid date range: start must be <= end.")
        return start, end

    def _parse_query_date(self, name: str, raw: str | None) -> date | None:
        if raw is None:
            return None
        text = str(raw).strip()
        if not text:
            return None
        parsed = self.date_parser.parse(text)
        if parsed is None:
            raise ValidationError(
                f"Invalid '{name}' date '{text}'. Use YYYY-MM-DD (recommended)."
            )
        return parsed

    def get_prices(self, *, start_raw: str | None, end_raw: str | None) -> list[dict[str, Any]]:
        prices_path = self._select_prices_path()
        if not prices_path.exists():
            raise ValidationError("brent_prices.csv or BrentOilPrices.csv not found", status_code=404)

        rows = CsvTable(prices_path).read_rows()
        if not rows:
            return []

        if "Date" not in rows[0] or "Price" not in rows[0]:
            raise ValidationError("Expected columns: Date, Price")

        start, end = self.parse_query_dates(start_raw, end_raw)

        payload: list[dict[str, Any]] = []
        invalid_date = 0
        invalid_price = 0

        for row in rows:
            row_date = self.date_parser.parse(row.get("Date"))
            if row_date is None:
                invalid_date += 1
                continue

            try:
                price_text = (row.get("Price") or "").replace(",", "").strip()
                price = float(price_text)
            except ValueError:
                invalid_price += 1
                continue

            if start and row_date < start:
                continue
            if end and row_date > end:
                continue

            payload.append({"date": row_date.isoformat(), "price": price})

        payload.sort(key=lambda item: item["date"])

        if not payload and (invalid_date or invalid_price):
            raise ValidationError(
                "No valid price rows found after parsing. "
                f"Invalid dates: {invalid_date}, invalid prices: {invalid_price}."
            )

        return payload


class EventService:
    def __init__(self, paths: DataPaths, date_parser: DateParser):
        self.paths = paths
        self.date_parser = date_parser

    def get_events(self) -> list[dict[str, Any]]:
        if not self.paths.events.exists():
            raise ValidationError("events.csv not found", status_code=404)

        rows = CsvTable(self.paths.events).read_rows()
        if not rows:
            return []

        if "date" not in rows[0] or "event" not in rows[0]:
            raise ValidationError("Expected columns: date, event")

        has_category = "category" in rows[0]
        payload: list[dict[str, Any]] = []
        invalid_date = 0
        invalid_event = 0

        for row in rows:
            row_date = self.date_parser.parse(row.get("date"))
            if row_date is None:
                invalid_date += 1
                continue

            event = (row.get("event") or "").strip()
            if not event:
                invalid_event += 1
                continue

            payload.append(
                {
                    "date": row_date.isoformat(),
                    "event": event,
                    "category": (row.get("category") or None) if has_category else None,
                }
            )

        payload.sort(key=lambda item: item["date"])

        if not payload and (invalid_date or invalid_event):
            raise ValidationError(
                "No valid event rows found after parsing. "
                f"Invalid dates: {invalid_date}, invalid events: {invalid_event}."
            )

        return payload


class ChangePointService:
    def __init__(self, paths: DataPaths, date_parser: DateParser):
        self.paths = paths
        self.date_parser = date_parser

    def get_change_points(self) -> dict[str, Any]:
        if not self.paths.change_points.exists():
            raise ValidationError("change_points.json not found", status_code=404)

        try:
            with self.paths.change_points.open("r", encoding="utf-8") as handle:
                payload: Any = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"Failed to read change_points.json: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValidationError("change_points.json must be a JSON object")

        cps = payload.get("change_points")
        if cps is None:
            raise ValidationError("change_points.json missing required key: change_points")
        if not isinstance(cps, list):
            raise ValidationError("change_points must be a list")

        normalized: list[dict[str, Any]] = []
        for idx, cp in enumerate(cps):
            if not isinstance(cp, dict):
                raise ValidationError(f"change_points[{idx}] must be an object")

            cp_date_raw = cp.get("date")
            cp_date = self.date_parser.parse(str(cp_date_raw) if cp_date_raw is not None else None)
            if cp_date is None:
                raise ValidationError(f"change_points[{idx}].date is required and must be a valid date")

            normalized_item: dict[str, Any] = {"date": cp_date.isoformat()}
            for key in ("mean_before", "mean_after", "impact_pct", "notes"):
                if key in cp:
                    normalized_item[key] = cp[key]
            normalized.append(normalized_item)

        out = dict(payload)
        out["change_points"] = normalized
        return out
