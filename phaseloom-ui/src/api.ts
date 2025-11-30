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

export interface CACEMetrics {
  layers: any[];
  policy_updates: any[];
}

// Correctly defined Gate5Metrics interface
export interface Gate5Metrics {
  image_url: string;
  summary: {
    gamma_final: number;
    c_self_final: number;
  };
  turns: Gate5Turn[];
}

export interface SessionReport {
  summary: {
    session_id: string;
    total_payloads: number;
    num_nodes: number;
    num_edges: number;
    num_sessions: number;
    num_turns: number;
  };
  image_url: string;
  gate5: Gate5Metrics; // Using the new Gate5Metrics interface
  cace: CACEMetrics;
}

const API_BASE = '/api';

// Function to start a new Caelus session
export async function startCaelusSession(): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/caelus/start`, {
    method: 'POST',
  });

  const text = await response.text();
  try {
    const data = JSON.parse(text);
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to start Caelus session');
    }
    return data;
  } catch (e) {
    // Re-throw with more context
    throw new Error(`Failed to parse JSON response from server. Status: ${response.status}. Response: ${text}`);
  }
}


// Updated listSessions function signature
export async function listSessions(): Promise<SessionInfo[]> {
  const response = await fetch(`${API_BASE}/sessions`);
  if (!response.ok) {
    throw new Error('Failed to fetch sessions');
  }
  return response.json();
}

// Added getSessionReport function
export async function getSessionReport(sessionId: string): Promise<SessionReport> {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/report`);
  if (!response.ok) {
    throw new Error(`Failed to fetch report for session ${sessionId}`);
  }
  return response.json();
}
