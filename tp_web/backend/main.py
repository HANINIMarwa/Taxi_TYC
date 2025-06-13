from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

from predictor import predict_fare, predict_distance

app = FastAPI()

# Setup CORS to allow your frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ['http://localhost:3000']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
TEMP_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

cache = {}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        cache.clear()
        cache["filepath"] = file_path

        return {"message": "File uploaded successfully", "filename": unique_filename}
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": f"Upload failed: {str(e)}"})

@app.get("/step/{step}")
async def process_step(step: str):
    try:
        filepath = cache.get("filepath")
        if not filepath or not os.path.exists(filepath):
            return JSONResponse(status_code=400, content={"error": "No uploaded file"})

        if step == "ingest":
            df = pd.read_csv(filepath)
            cache["df"] = df
            return {
                "columns": df.columns.tolist(),
                "rows": df.head(10).to_dict(orient="records"),
                "stats": {"row_count": len(df), "columns": len(df.columns)}
            }

        elif step == "clean":
            df = cache.get("df")
            if df is None:
                return {"error": "Please ingest first"}

            df_cleaned = df.dropna()
            cache["cleaned_df"] = df_cleaned
            return {
                "columns": df_cleaned.columns.tolist(),
                "rows": df_cleaned.head(10).to_dict(orient="records"),
                "stats": {"remaining_rows": len(df_cleaned)}
            }

        elif step == "aggregate":
            df = cache.get("cleaned_df")
            if df is None:
                return {"error": "Please run the 'clean' step first"}

            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            if not numeric_columns:
                return {"error": "No numeric columns to aggregate"}

            agg = df[numeric_columns].sum().reset_index(name='total')
            cache["agg"] = agg
            return {
                "columns": agg.columns.tolist(),
                "rows": agg.head(10).to_dict(orient="records")
            }

        elif step == "plot":
            agg = cache.get("agg")
            if agg is None:
                return {"error": "Please run the 'aggregate' step first"}

            fig = px.bar(
                agg, x=agg.columns[0], y=agg.columns[1],
                title="Aggregated Data Plot"
            )
            plot_filename = f"plot_{int(datetime.now().timestamp())}.html"
            plot_path = os.path.join(TEMP_DIR, plot_filename)
            fig.write_html(plot_path, include_plotlyjs='cdn')

            return {"plot_url": f"/temp/{plot_filename}", "message": "Plot generated"}

        return JSONResponse(status_code=400, content={"error": f"Unknown step: {step}"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Step failed: {str(e)}"})

# Prediction models

class FareRequest(BaseModel):
    trip_distance: float

class DistanceRequest(BaseModel):
    fare_amount: float

@app.post("/predict/fare")
async def get_predicted_fare(data: FareRequest):
    try:
        fare = predict_fare(data.trip_distance)
        return {"predicted_fare": fare}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/predict/distance")
async def get_predicted_distance(data: DistanceRequest):
    try:
        distance = predict_distance(data.fare_amount)
        return {"predicted_distance": distance}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
