import { useState } from "react";

import EnrollmentForm from "./components/EnrollmentForm";
import LiveRecognition from "./components/LiveRecognition";
import PrivacyPanel from "./components/PrivacyPanel";

const TABS = [
  { key: "enroll", label: "Enroll", Component: EnrollmentForm },
  { key: "recognize", label: "Live Recognition", Component: LiveRecognition },
  { key: "privacy", label: "Privacy", Component: PrivacyPanel },
];

export default function App() {
  const [active, setActive] = useState("enroll");
  const ActiveComponent = TABS.find((t) => t.key === active).Component;

  return (
    <div className="app">
      <h1>Univen FaceID</h1>
      <div className="subtitle">Face enrollment &amp; recognition</div>

      <div className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`tab ${active === t.key ? "active" : ""}`}
            onClick={() => setActive(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <ActiveComponent />
    </div>
  );
}
