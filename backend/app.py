from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from services import (
    ChangePointService,
    DataPaths,
    DateParser,
    EventService,
    PriceService,
    ValidationError,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

PRICES_PATH = DATA_DIR / "brent_prices.csv"
ALT_PRICES_PATH = DATA_DIR / "BrentOilPrices.csv"
EVENTS_PATH = DATA_DIR / "events.csv"
CHANGE_POINTS_PATH = DATA_DIR / "change_points.json"

PATHS = DataPaths(
    prices=PRICES_PATH,
    alt_prices=ALT_PRICES_PATH,
    events=EVENTS_PATH,
    change_points=CHANGE_POINTS_PATH,
)

DATE_PARSER = DateParser()
PRICE_SERVICE = PriceService(PATHS, DATE_PARSER)
EVENT_SERVICE = EventService(PATHS, DATE_PARSER)
CHANGE_POINT_SERVICE = ChangePointService(PATHS, DATE_PARSER)

app = Flask(__name__)
CORS(app)


@app.errorhandler(ValidationError)
def handle_validation_error(exc: ValidationError):
    return jsonify({"error": exc.message}), exc.status_code


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Backend is running.",
            "endpoints": [
                "/api/health",
                "/api/prices",
                "/api/events",
                "/api/change-points",
            ],
        }
    )


@app.get("/api/prices")
def prices():
    payload = PRICE_SERVICE.get_prices(
        start_raw=request.args.get("start"),
        end_raw=request.args.get("end"),
    )
    return jsonify(payload)


@app.get("/api/events")
def events():
    return jsonify(EVENT_SERVICE.get_events())


@app.get("/api/change-points")
def change_points():
    return jsonify(CHANGE_POINT_SERVICE.get_change_points())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
