import { useState } from "react";

export default function ConsentNotice({ onAccept }) {
  const [checked, setChecked] = useState(false);

  return (
    <div className="consent-box">
      <h3>Before we scan your face</h3>
      <p>
        Univen FaceID will capture three images of your face (front, left,
        right) and convert them into a numeric representation ("embedding")
        used to recognize you later. This is treated as special personal
        information under South Africa's POPIA.
      </p>
      <ul>
        <li>We store the embedding, not your raw photos.</li>
        <li>Your name and age are stored alongside the embedding.</li>
        <li>You can request deletion of your data at any time (see the Privacy tab).</li>
        <li>Your face data is only used to recognize you within this system.</li>
      </ul>
      <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => setChecked(e.target.checked)}
        />
        I understand and consent to my face being captured and stored.
      </label>
      <button disabled={!checked} onClick={onAccept} style={{ marginTop: 12 }}>
        Continue
      </button>
    </div>
  );
}
