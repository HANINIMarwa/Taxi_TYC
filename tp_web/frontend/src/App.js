import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [output, setOutput] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);
  const [tripDistance, setTripDistance] = useState("");
  const [fareAmount, setFareAmount] = useState("");
  const [predictedFare, setPredictedFare] = useState(null);
  const [predictedDistance, setPredictedDistance] = useState(null);

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post("http://localhost:8000/upload", formData);
      alert(res.data.message);
      setOutput(null);
      setPlotUrl(null);
    } catch (err) {
      alert("Upload failed: " + err.message);
    }
  };

  const runStep = async (step) => {
    try {
      const res = await axios.get(`http://localhost:8000/step/${step}`);
      if (res.data.plot_url) {
        setPlotUrl(`http://localhost:8000${res.data.plot_url}`);
        setOutput(null);
      } else {
        setOutput(res.data);
        setPlotUrl(null);
      }
    } catch (err) {
      alert("Step failed: " + err.message);
    }
  };

  const predictFare = async () => {
    if (!tripDistance) {
      alert("Enter trip distance to predict fare");
      return;
    }
    try {
      const res = await axios.post("http://localhost:8000/predict/fare", {
        trip_distance: parseFloat(tripDistance),
      });
      setPredictedFare(res.data.predicted_fare);
    } catch (err) {
      alert("Prediction failed: " + err.message);
    }
  };

  const predictDistance = async () => {
    if (!fareAmount) {
      alert("Enter fare amount to predict distance");
      return;
    }
    try {
      const res = await axios.post("http://localhost:8000/predict/distance", {
        fare_amount: parseFloat(fareAmount),
      });
      setPredictedDistance(res.data.predicted_distance);
    } catch (err) {
      alert("Prediction failed: " + err.message);
    }
  };

  return (
    <div className="app-container">
      <h1 className="title">🚕 NYC Taxi Pipeline</h1>

      {/* Upload and Processing Container */}
      <div className="black-container">
        <div className="input-group">
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            accept=".csv"
          />
          <button onClick={uploadFile}>Upload CSV</button>
        </div>

        <div className="btn-group">
          <button onClick={() => runStep("ingest")}>Ingest</button>
          <button onClick={() => runStep("clean")}>Clean</button>
          <button onClick={() => runStep("aggregate")}>Aggregate</button>
          <button onClick={() => runStep("plot")}>Visualize</button>
        </div>

        {output && (
          <div className="output">
            <pre>{JSON.stringify(output, null, 2)}</pre>
          </div>
        )}

        {plotUrl && (
          <div className="plot-container">
            <iframe src={plotUrl} title="Visualization" />
          </div>
        )}
      </div>

      {/* Prediction Container */}
      <div className="black-container">
        <div className="prediction-area">
          <div className="predictor">
            <h3>Predict Fare from Distance</h3>
            <input
              type="number"
              placeholder="Distance (miles)"
              value={tripDistance}
              onChange={(e) => setTripDistance(e.target.value)}
            />
            <button onClick={predictFare}>Predict</button>
            {predictedFare && (
              <div className="prediction-result">
                ${predictedFare.toFixed(2)}
              </div>
            )}
          </div>

          <div className="predictor">
            <h3>Predict Distance from Fare</h3>
            <input
              type="number"
              placeholder="Fare ($)"
              value={fareAmount}
              onChange={(e) => setFareAmount(e.target.value)}
            />
            <button onClick={predictDistance}>Predict</button>
            {predictedDistance && (
              <div className="prediction-result">
                {predictedDistance.toFixed(2)} miles
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;