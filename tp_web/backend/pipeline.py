# pipeline.py
import pandas as pd
import plotly.express as px
import os
import uuid
from datetime import datetime

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def run_pipeline_step(step, filepath, cache):
    try:
        if step == "ingest":
            df = pd.read_csv(filepath)
            if df.empty:
                return {"error": "CSV file is empty."}
            cache["raw_df"] = df
            return {
                "message": "File ingested",
                "columns": df.columns.tolist(),
                "rows": df.head(10).to_dict(orient="records")
            }

        elif step == "clean":
            df = cache.get("raw_df")
            if df is None:
                return {"error": "No data to clean. Please ingest first."}

            required_columns = ["pickup_datetime", "fare_amount"]
            if not all(col in df.columns for col in required_columns):
                return {"error": f"Missing required columns: {', '.join(required_columns)}"}

            df_cleaned = df.dropna(subset=required_columns)
            df_cleaned = df_cleaned[df_cleaned["fare_amount"] > 0]

            if df_cleaned.empty:
                return {"error": "No rows remain after cleaning."}

            cache["clean_df"] = df_cleaned
            return {
                "message": "Data cleaned",
                "columns": df_cleaned.columns.tolist(),
                "rows": df_cleaned.head(10).to_dict(orient="records")
            }

        elif step == "aggregate":
            df = cache.get("clean_df")
            if df is None:
                return {"error": "No data to aggregate. Please clean data first."}

            df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors='coerce')
            df = df.dropna(subset=["pickup_datetime"])

            df["hour"] = df["pickup_datetime"].dt.hour
            df["weekday"] = df["pickup_datetime"].dt.day_name()

            agg = df.groupby(["weekday", "hour"])["fare_amount"].mean().reset_index()

            # Optional: Order weekdays
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            agg["weekday"] = pd.Categorical(agg["weekday"], categories=weekday_order, ordered=True)
            agg = agg.sort_values(["weekday", "hour"])

            cache["agg"] = agg
            return {
                "message": "Data aggregated",
                "columns": agg.columns.tolist(),
                "rows": agg.head(10).to_dict(orient="records")
            }

        elif step == "plot":
            agg = cache.get("agg")
            if agg is None:
                return {"error": "No aggregated data to plot. Please aggregate first."}

            fig = px.line(
                agg,
                x="hour",
                y="fare_amount",
                color="weekday",
                title="Average Fare per Hour and Weekday"
            )

            plot_filename = f"plot_{uuid.uuid4().hex}.html"
            plot_path = os.path.join(TEMP_DIR, plot_filename)
            fig.write_html(plot_path, include_plotlyjs='cdn')

            return {
                "message": "Plot generated successfully",
                "plot_url": f"/temp/{plot_filename}"
            }

        return {"error": f"Unknown step '{step}'"}

    except Exception as e:
        return {"error": f"Error in step '{step}': {str(e)}"}
