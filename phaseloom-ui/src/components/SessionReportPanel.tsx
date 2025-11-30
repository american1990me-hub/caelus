import React from 'react';
import { SessionReport } from '../api';

interface Props {
  report: SessionReport;
}

export const SessionReportPanel: React.FC<Props> = ({ report }) => {
  return (
    <div>
      <h2>Session Report for {report.summary.session_id}</h2>
      <div>
        <h3>Summary</h3>
        <ul>
          <li>Total Payloads: {report.summary.total_payloads}</li>
          <li>Nodes: {report.summary.num_nodes}</li>
          <li>Edges: {report.summary.num_edges}</li>
          <li>Sessions: {report.summary.num_sessions}</li>
          <li>Turns: {report.summary.num_turns}</li>
        </ul>
      </div>
      <div>
        <h3>Conversation Graph</h3>
        <img src={report.image_url} alt="Session Conversation Graph" style={{ maxWidth: '100%', height: 'auto' }} />
      </div>
    </div>
  );
};
