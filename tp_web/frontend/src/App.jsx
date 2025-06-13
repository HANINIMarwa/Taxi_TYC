import React, { useState } from "react";
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [output, setOutput] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);
  const [fareAmount, setFareAmount] = useState("");
  const [tripDistance, setTripDistance] = useState("");

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    setOutput(data);
    setPlotUrl(null);
  };

  const runStep = async (step) => {
    const response = await fetch(`/run/${step}`, {
      method: "POST",
    });

    if (step === "plot") {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setPlotUrl(url);
      setOutput(null);
    } else {
      const data = await response.json();
      setOutput(data);
      setPlotUrl(null);
    }
  };

  const predictFare = async () => {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fare_amount: parseFloat(fareAmount),
        trip_distance: parseFloat(tripDistance),
      }),
    });

    const data = await response.json();
    setOutput(data);
    setPlotUrl(null);
  };

  return (
    <div className="overlay">
      <h1 className="title">🚖 Taxi Data Cleaner</h1>

      <div className="top-bar">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="file-input"
        />
        <button className="upload-btn" onClick={uploadFile}>Upload CSV</button>
      </div>

      <div className="top-bar">
        <input
          type="number"
          placeholder="Enter Fare Amount"
          value={fareAmount}
          onChange={(e) => setFareAmount(e.target.value)}
          className="file-input"
        />
        <input
          type="number"
          placeholder="Enter Trip Distance"
          value={tripDistance}
          onChange={(e) => setTripDistance(e.target.value)}
          className="file-input"
        />
        <button className="upload-btn" onClick={predictFare}>Predict</button>
      </div>

      <div className="btn-group">
        <button onClick={() => runStep("ingest")}>🗂️ Ingest</button>
        <button onClick={() => runStep("clean")}>🧹 Clean</button>
        <button onClick={() => runStep("aggregate")}>📊 Aggregate</button>
        <button onClick={() => runStep("plot")}>📈 Visualize</button>
      </div>

      {output && (
        <pre className="output-container">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}

      {plotUrl && (
        <div className="plot-container">
          <iframe className="plot-iframe" src={plotUrl} title="Visualization"></iframe>
        </div>
      )}
    </div>
  );
}

export default App;
