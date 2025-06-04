import React, { useState, useRef, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const SignToText = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [sentence, setSentence] = useState("");
  const [currentGesture, setCurrentGesture] = useState("");
  const [error, setError] = useState("");
  const lastAddedTimeRef = useRef(0);
  const gestureCooldown = 2000;

  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      } catch (err) {
        setError("Error accessing camera: " + err.message);
      }
    }
    startCamera();
    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const captureAndPredict = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");
      try {
        const response = await fetch("http://10.91.53.106:5000/predict", {
          method: "POST",
          body: formData,
        });
        const data = await response.json();
        if (data.prediction) {
          setCurrentGesture(data.prediction);
          const currentTime = Date.now();
          if (currentTime - lastAddedTimeRef.current >= gestureCooldown) {
            if (data.prediction === "space") {
              setSentence((prev) => prev.trim() + " ");
            } else if (data.prediction === "BACKSPACE") {
              setSentence((prev) => prev.slice(0, -1));
            } else {
              setSentence((prev) => prev + data.prediction);
            }
            lastAddedTimeRef.current = currentTime;
          }
        }
      } catch (err) {
        setError("Error sending image to backend: " + err.message);
      }
    }, "image/jpeg");
  };

  useEffect(() => {
    const intervalId = setInterval(captureAndPredict, 2000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div
      className="d-flex flex-column min-vh-80 chat-background w-100"
      style={{
        backgroundColor: "#e6e6e6",
        backgroundImage: 'url("https://www.transparenttextures.com/patterns/inspiration-geometry.png")',
        backgroundRepeat: "repeat",
        backgroundSize: "contain",
      }}
    >
      {/* Content wrapper with flex-grow to fill remaining space */}
      <div className="container-fluid text-center mt-5 mb-5 flex-grow-1 d-flex flex-column">
        <h1 className="mb-4 text-primary">Sign to Text Converter</h1>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="d-flex justify-content-center mb-4">
          <div className="border border-primary rounded shadow-lg p-3 bg-light w-50">
            <video
              ref={videoRef}
              className="rounded border border-dark"
              style={{ width: "100%", maxWidth: "100%" }}
              autoPlay
              muted
            ></video>
          </div>
        </div>

        <canvas ref={canvasRef} style={{ display: "none" }}></canvas>

        <div className="row mt-4">
          <div className="col-md-6 offset-md-3">
            <div className="card shadow">
              <div className="card-body">
                <h3 className="card-title text-secondary">Recognized Sentence:</h3>
                <p className="card-text text-dark fs-5">{sentence || "Waiting for input..."}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4">
          <h4 className="text-success">
            Current Gesture: <span className="fw-bold">{currentGesture || "Detecting..."}</span>
          </h4>
        </div>

        {/* Button container with reduced gap and responsiveness */}
        <div className="mt-4 d-flex justify-content-center gap-2 flex-wrap">
          <button
            className="btn btn-warning btn-lg px-4"
            onClick={() => setSentence((prev) => prev.slice(0, -1))}
          >
            <i className="fas fa-backspace me-2"></i> Backspace
          </button>
          <button className="btn btn-danger btn-lg px-4" onClick={() => setSentence("")}>
            <i className="fas fa-trash me-2"></i> Clear
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignToText;
