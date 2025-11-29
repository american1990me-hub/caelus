import React, { useEffect, useState } from "react";
import { fetchGate5, Gate5Turn } from "../api";
import { DenseLinesCanvas } from "./DenseLinesCanvas";

interface Props {
  sessionId: string;
}

export const Gate5Panel: React.FC<Props> = ({ sessionId }) => {
  const [turns, setTurns] = useState<Gate5Turn[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGate5(sessionId)
      .then((data) => setTurns(data.turns || []))
      .catch((err) => setError(err.message));
  }, [sessionId]);

  if (error) return <div>Error loading Gate5 metrics: {error}</div>;
  if (!turns.length) return <div>No Gate 5 data for this session.</div>;

  const gammaSeries = [{
    // t = turn index, y = Gamma
    // DenseLines expects TimeSeries
    t: 0,
    y: turns[0].Gamma,
  }];

  const series = [
    turns.map((t) => ({ t: t.turn_index, y: t.Gamma })),
    turns.map((t) => ({ t: t.turn_index, y: t.C_self })),
  ];

  const last = turns[turns.length - 1];

  return (
    <div style={{ border: "1px solid #444", padding: "1rem", borderRadius: "8px" }}>
      <h2>Gate 5 Metrics</h2>
      <DenseLinesCanvas seriesList={series} />
      <div style={{ display: "flex", gap: "1rem", marginTop: "0.5rem" }}>
        <div>
          <strong>Γ_final</strong>
          <div>{last.Gamma.toFixed(3)}</div>
        </div>
        <div>
          <strong>C_self (last)</strong>
          <div>{last.C_self.toFixed(3)}</div>
        </div>
        <div>
          <strong>ΔM(last)</strong>
          <div>{last.DeltaM_repair.toFixed(3)}</div>
        </div>
      </div>
    </div>
  );
};
