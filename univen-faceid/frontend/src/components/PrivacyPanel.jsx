import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function PrivacyPanel() {
  const [people, setPeople] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const res = await fetch(`${API_URL}/people`);
      const data = await res.json();
      if (!res.ok) throw new Error("Could not load enrolled people");
      setPeople(data);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const remove = async (id) => {
    try {
      const res = await fetch(`${API_URL}/people/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Could not delete this record");
      setPeople((prev) => prev.filter((p) => p.id !== id));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div>
      <h2>Privacy &amp; Your Data</h2>
      <div className="consent-box">
        <p>
          Univen FaceID stores your name, age, and a numeric face embedding —
          not raw photos. Under South Africa's POPIA, you may request that
          your record be permanently deleted at any time. Deleting a record
          below removes it immediately and cannot be undone.
        </p>
      </div>

      <h3 style={{ marginTop: 16 }}>Enrolled people</h3>
      {error && <p className="error">{error}</p>}
      <ul className="people-list">
        {people.map((p) => (
          <li key={p.id}>
            <span>
              {p.name} ({p.age})
            </span>
            <button onClick={() => remove(p.id)}>Delete my data</button>
          </li>
        ))}
        {people.length === 0 && <li>No one is enrolled yet.</li>}
      </ul>
    </div>
  );
}
