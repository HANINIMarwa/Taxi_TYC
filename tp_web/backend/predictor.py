import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

fare_model = joblib.load(os.path.join(BASE_DIR, "taxi_fare_model.pkl"))
distance_model = joblib.load(os.path.join(BASE_DIR, "taxi_distance_model.pkl"))

print("Fare model type:", type(fare_model))
print("Distance model type:", type(distance_model))


def predict_fare(trip_distance: float) -> float:
    return float(fare_model.predict([[trip_distance]])[0])

def predict_distance(fare_amount: float) -> float:
    return float(distance_model.predict([[fare_amount]])[0])
