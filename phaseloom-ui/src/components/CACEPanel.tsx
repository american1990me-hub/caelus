import React from 'react';
import { CACEMetrics } from '../api';

interface Props {
  caceData: CACEMetrics;
}

export const CACEPanel: React.FC<Props> = ({ caceData }) => {
  const metrics = caceData;

  if (!metrics) return <div>Loading CACE metrics...</div>;

  return (
    <div style={{ border: '1px solid #444', padding: '1rem', borderRadius: '8px' }}>
      <h2>CACE Layers & Policy</h2>
      <h3>Layer Residuals</h3>
      <table style={{ width: '100%', fontSize: '0.85rem' }}>
        <thead>
          <tr>
            <th>Layer</th>
            <th>c_in</th>
            <th>c_out</th>
            <th>R_c</th>
            <th>Approx FLOPs</th>
          </tr>
        </thead>
        <tbody>
          {metrics.layers.map((layer, idx) => {
            const coh = layer.coherence || {};
            const res = layer.residual || {};
            const approx = layer.approx || {};
            return (
              <tr key={idx}>
                <td>{layer.layer_id || layer.label}</td>
                <td>{coh.c_in?.toFixed?.(3) ?? '-'}</td>
                <td>{coh.c_out?.toFixed?.(3) ?? '-'}</td>
                <td>{res.R_c?.toFixed?.(3) ?? '-'}</td>
                <td>{approx.approx_fraction_flops?.toFixed?.(2) ?? '-'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <h3 style={{ marginTop: '1rem' }}>Policy Updates</h3>
      <ul>
        {metrics.policy_updates.map((p, idx) => (
          <li key={idx}>
            Eldritch {JSON.stringify(p.eldritch_state)} → rank_max={p.rank_max},
            τ_high={p.tau_high}, τ_mid={p.tau_mid}
          </li>
        ))}
      </ul>
    </div>
  );
};
