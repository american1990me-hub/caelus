
import React, { useState, useEffect } from 'react';
import { fetchSessionReport, SessionReport } from '../api';
import { Gate5Panel } from './Gate5Panel';
import { CACEPanel } from './CACEPanel';
import { SessionReportPanel } from './SessionReportPanel';

interface Props {
  sessionId: string;
}

export const SessionDashboard: React.FC<Props> = ({ sessionId }) => {
  const [report, setReport] = useState<SessionReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!sessionId) return;

    const getReport = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const reportData = await fetchSessionReport(sessionId);
        setReport(reportData);
      } catch (err) {
        setError('Failed to load session report.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    getReport();
  }, [sessionId]);

  if (isLoading) {
    return <div>Loading session report...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  if (!report) {
    return <div>No report data available.</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
      <SessionReportPanel report={report} />
      <div style={{ display: 'flex', gap: '1rem' }}>
        <div style={{ flex: 1 }}>
          <Gate5Panel gate5Data={report.gate5} />
        </div>
        <div style={{ flex: 1 }}>
          <CACEPanel caceData={report.cace} />
        </div>
      </div>
    </div>
  );
};
