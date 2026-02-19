import os
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

CSV_PATH = "courses.csv"

# Try to load CSV safely
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    csv_error = None
else:
    df = pd.DataFrame()  # empty dataframe
    csv_error = f"CSV file '{CSV_PATH}' not found."


# Optional: make sure expected columns exist (adjust names to match your CSV exactly)
EXPECTED_COLS = [
    "Title",
    "Instuctor",  # or "Instructor" if that's what your CSV uses
    "Location",
    "Cost",
    "learning_objectives",
    "provided_materals",
    "skills_developed",
    "course_description",
    "class_ID",
]
missing = [c for c in EXPECTED_COLS if c not in df.columns]
if missing:
    print(f"Warning: missing columns in CSV: {missing}")

# Precompute dropdown options
LOCATIONS = sorted([x for x in df.get("Location", pd.Series(dtype=str)).dropna().unique()])
# If Cost is numeric-ish, this helps filtering. If it's messy strings, leave it as-is.
if "Cost" in df.columns:
    df["Cost_num"] = pd.to_numeric(df["Cost"], errors="coerce")
else:
    df["Cost_num"] = pd.NA


def filter_df(data: pd.DataFrame, q: str, location: str, max_cost: str) -> pd.DataFrame:
    filtered = data

    # Text search across several columns
    if q:
        q_lower = q.strip().lower()
        search_cols = [
            "Title",
            "Instuctor",
            "Location",
            "learning_objectives",
            "skills_developed",
            "course_description",
        ]
        existing_cols = [c for c in search_cols if c in filtered.columns]

        # Create a boolean mask: row matches if ANY column contains the query
        mask = False
        for col in existing_cols:
            mask = mask | filtered[col].fillna("").astype(str).str.lower().str.contains(q_lower, na=False)

        filtered = filtered[mask]

    # Location filter
    if location and location != "ALL" and "Location" in filtered.columns:
        filtered = filtered[filtered["Location"].fillna("").astype(str) == location]

    # Max cost filter (numeric)
    if max_cost:
        try:
            max_cost_val = float(max_cost)
            filtered = filtered[filtered["Cost_num"].notna() & (filtered["Cost_num"] <= max_cost_val)]
        except ValueError:
            pass  # ignore invalid max_cost input

    return filtered

@app.route("/", methods=["GET"])
def index():
    if csv_error:
        return render_template(
            "index.html",
            results=[],
            total=0,
            csv_error=csv_error,
        )

    q = request.args.get("q", "").strip()

    filtered = df

    if q:
        filtered = df[df["Title"].str.contains(q, case=False, na=False)]

    results = filtered.to_dict(orient="records")

    return render_template(
        "index.html",
        results=results,
        total=len(results),
        csv_error=None,
    )

if __name__ == "__main__":
    app.run(debug=True)
