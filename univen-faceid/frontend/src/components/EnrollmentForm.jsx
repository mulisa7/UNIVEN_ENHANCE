import { useRef, useState } from "react";

import ConsentNotice from "./ConsentNotice";

const STEPS = [
  { key: "front", prompt: "Look straight at the camera" },
  { key: "left", prompt: "Turn your face slightly LEFT" },
  { key: "right", prompt: "Turn your face slightly RIGHT" },
];

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function EnrollmentForm() {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [step, setStep] = useState(0);
  const [images, setImages] = useState([]);
  const [showConsent, setShowConsent] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const requestStart = () => {
    if (!name.trim()) return setError("Name is required");
    if (!age || parseInt(age, 10) <= 0) {
      return setError("Age must be a positive integer");
    }
    setError("");
    setSuccess("");
    setImages([]);
    setStep(0);
    setShowConsent(true);
  };

  const startCamera = async () => {
    setShowConsent(false);
    setIsCapturing(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (e) {
      setError("Could not access camera: " + e.message);
      setIsCapturing(false);
    }
  };

  const stopCamera = () => {
    videoRef.current?.srcObject?.getTracks().forEach((t) => t.stop());
    setIsCapturing(false);
  };

  const capture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      const newImages = [...images, blob];
      setImages(newImages);
      if (newImages.length === 3) {
        stopCamera();
        submit(newImages);
      } else {
        setStep((s) => s + 1);
      }
    }, "image/jpeg");
  };

  const submit = async (capturedImages) => {
    const formData = new FormData();
    formData.append("name", name.trim());
    formData.append("age", age);
    capturedImages.forEach((blob, i) => {
      formData.append("images", blob, `${STEPS[i].key}.jpg`);
    });

    try {
      const res = await fetch(`${API_URL}/enroll`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Enrollment failed");
      setSuccess(data.message);
      setImages([]);
    } catch (e) {
      setError(e.message);
    }
  };

  if (showConsent) {
    return <ConsentNotice onAccept={startCamera} />;
  }

  return (
    <div>
      <h2>Enroll Face</h2>
      <input
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        disabled={isCapturing}
      />
      <input
        placeholder="Age"
        type="number"
        value={age}
        onChange={(e) => setAge(e.target.value)}
        disabled={isCapturing}
      />

      {!isCapturing ? (
        <button onClick={requestStart}>Start Enrollment</button>
      ) : (
        <div>
          <p>
            <b>Step {step + 1}/3:</b> {STEPS[step].prompt}
          </p>
          <video ref={videoRef} autoPlay playsInline />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          <button onClick={capture}>Capture {STEPS[step].key}</button>
          <div>Progress: {images.length}/3 captured</div>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {success && <p className="success">{success}</p>}
    </div>
  );
}
