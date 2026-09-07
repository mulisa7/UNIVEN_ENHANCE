import { useEffect, useRef, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const FRAME_INTERVAL_MS = 1500;

export default function LiveRecognition() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const intervalRef = useRef(null);

  const start = async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      setRunning(true);
    } catch (e) {
      setError("Could not access camera: " + e.message);
    }
  };

  const stop = () => {
    videoRef.current?.srcObject?.getTracks().forEach((t) => t.stop());
    setRunning(false);
    setResult(null);
  };

  const drawOverlay = () => {
    const video = videoRef.current;
    const overlay = overlayRef.current;
    if (!video || !overlay || !video.videoWidth) return;
    overlay.width = video.videoWidth;
    overlay.height = video.videoHeight;
    const ctx = overlay.getContext("2d");
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    // A real bounding box would come from the backend's detection step;
    // this frames the whole frame as a lightweight visual placeholder
    // whenever a match/no-match result is available.
    if (result) {
      ctx.strokeStyle = result.matched ? "#276749" : "#c53030";
      ctx.lineWidth = 4;
      ctx.strokeRect(10, 10, overlay.width - 20, overlay.height - 20);
    }
  };

  const captureAndRecognize = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !video.videoWidth) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");
      try {
        const res = await fetch(`${API_URL}/recognize`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        setResult(data);
      } catch (e) {
        setError("Recognition request failed: " + e.message);
      }
    }, "image/jpeg");
  };

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(captureAndRecognize, FRAME_INTERVAL_MS);
    }
    return () => clearInterval(intervalRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  useEffect(() => {
    drawOverlay();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result]);

  return (
    <div>
      <h2>Live Recognition</h2>
      {!running ? (
        <button onClick={start}>Start Camera</button>
      ) : (
        <button className="secondary" onClick={stop}>
          Stop Camera
        </button>
      )}

      <div className="camera-wrap" style={{ marginTop: 12 }}>
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={overlayRef} className="overlay-canvas" />
      </div>
      <canvas ref={canvasRef} style={{ display: "none" }} />

      {result && (
        <div className={`result-card ${result.matched ? "matched" : "unknown"}`}>
          {result.matched ? (
            <>
              <div style={{ fontSize: "1.2rem", fontWeight: 600 }}>
                {result.person.name}
              </div>
              <div>Age: {result.person.age}</div>
              <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>
                Confidence: {(result.confidence * 100).toFixed(1)}%
              </div>
            </>
          ) : (
            <div>Unknown — not enrolled.</div>
          )}
        </div>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
}
