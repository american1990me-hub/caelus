export interface SessionInfo {
  session_id: string;
  path: string;
}

export interface Gate5Turn {
  turn_index: number;
  Gamma: number;
  C_self: number;
  DeltaM_repair: number;
  meta: any;
}

export interface Gate5Response {
  session_id: string;
  turns: Gate5Turn[];
}

export interface CACEMetrics {
  session_id: string;
  layers: any[];
  summaries: any[];
  policy_updates: any[];
}

const API_BASE = import.meta.env.VITE_PHASELOOM_API || "http://localhost:8000";

export async function fetchSessions(): Promise<SessionInfo[]> {
  const res = await fetch(`${API_BASE}/api/sessions`);
  if (!res.ok) throw new Error("Failed to fetch sessions");
  return await res.json();
}

export async function fetchGate5(sessionId: string): Promise<Gate5Response> {
  const res = await fetch(`${API_BASE}/api/metrics/gate5/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch Gate5 metrics");
  return await res.json();
}

export async function fetchCACE(sessionId: string): Promise<CACEMetrics> {
  const res = await fetch(`${API_BASE}/api/metrics/cace/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch CACE metrics");
  return await res.json();
}
