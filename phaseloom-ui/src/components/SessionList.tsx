import React, { useEffect, useState } from "react";
import { fetchSessions, SessionInfo } from "../api";

interface Props {
  selectedSessionId: string | null;
  onSelect: (id: string) => void;
}

export const SessionList: React.FC<Props> = ({ selectedSessionId, onSelect }) => {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSessions()
      .then(setSessions)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div>Error loading sessions: {error}</div>;
  if (!sessions.length) return <div>No sessions found.</div>;

  return (
    <div style={{ borderRight: "1px solid #444", paddingRight: "1rem" }}>
      <h2>Sessions</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {sessions.map((s) => (
          <li key={s.session_id}>
            <button
              style={{
                background: s.session_id === selectedSessionId ? "#555" : "transparent",
                color: "#fff",
                border: "none",
                cursor: "pointer",
                padding: "0.25rem 0.5rem",
                textAlign: "left",
                width: "100%",
              }}
              onClick={() => onSelect(s.session_id)}
            >
              {s.session_id}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
