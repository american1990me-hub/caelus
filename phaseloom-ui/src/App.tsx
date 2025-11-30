
import React, { useState } from "react";
import { SessionList } from "./components/SessionList";
import { SessionDashboard } from "./components/SessionDashboard";
import DenseLines3D from "./components/DenseLines3D";

const App: React.FC = () => {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  return (
    <div
      style={{
        background: "#222",
        color: "#fff",
        display: "flex",
        fontFamily: "sans-serif",
        height: "100vh",
        padding: "1rem",
      }}
    >
      <SessionList
        selectedSessionId={selectedSessionId}
        onSelect={setSelectedSessionId}
      />
      <div style={{ flex: 1, paddingLeft: "1rem" }}>
        {selectedSessionId ? (
          <SessionDashboard sessionId={selectedSessionId} />
        ) : (
          // The 3D density plot is now the default view
          <DenseLines3D />
        )}
      </div>
    </div>
  );
};

export default App;
