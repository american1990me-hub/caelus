import React from 'react';

interface Props {
  gate5Data: {
    image_url: string;
    summary: {
      gamma_final: number;
      c_self_final: number;
    };
  };
}

export const Gate5Panel: React.FC<Props> = ({ gate5Data }) => {
  if (!gate5Data || !gate5Data.image_url) return <div>No Gate 5 data for this session.</div>;

  const { image_url, summary } = gate5Data;

  return (
    <div style={{ border: '1px solid #444', padding: '1rem', borderRadius: '8px' }}>
      <h2>Gate 5 Metrics</h2>
      <img src={image_url} alt="Gate 5 Metrics" style={{ maxWidth: '100%', height: 'auto' }} />
      <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
        <div>
          <strong>Γ_final</strong>
          <div>{summary.gamma_final.toFixed(3)}</div>
        </div>
        <div>
          <strong>C_self (last)</strong>
          <div>{summary.c_self_final.toFixed(3)}</div>
        </div>
      </div>
    </div>
  );
};
