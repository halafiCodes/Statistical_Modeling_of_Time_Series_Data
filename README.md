# Week 11: Change Point Analysis & Dashboard

This project covers Tasks 1–3: documentation and planning, Bayesian change point analysis, and an interactive dashboard.

## 1) Task 1 Deliverables
- Task 1 report: docs/Task1_Report.md
- Event dataset: data/events.csv

## 2) Task 2 Notebook
Notebook: notebooks/Task2_ChangePoint_Analysis.ipynb

### Required dataset
Place the Brent prices file at:
- data/brent_prices.csv
- data/BrentOilPrices.csv

Expected columns:
- Date
- Price

## 3) Task 3 Dashboard
### Backend (Flask)
Location: backend/

### Frontend (React + Vite)
Location: frontend/

## Setup
### Backend
1. Create and activate a virtual environment.
2. Install dependencies from backend/requirements.txt.
3. Run the Flask app.

### Frontend
1. Install dependencies in frontend/.
2. Run the dev server.

## Notes
- The dashboard reads data from the Flask API.
- Update data/change_points.json with notebook outputs.
 