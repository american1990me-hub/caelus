
import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

const DenseLines3D = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch the aggregated data for the 3D plot
    fetch('/reports/density_map.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(setData)
      .catch(err => {
        console.error("Failed to fetch density map:", err);
        setError(err.message);
      });
  }, []);

  if (error) {
    return <div className="text-red-500">Failed to load 3D graph: {error}</div>;
  }

  if (!data) {
    return <div>Loading 3D Density Graph...</div>;
  }

  // The data from density_map.json is already in the format Plotly expects
  const plotData = [data];

  return (
    <div className="w-full h-96 bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-bold text-white mb-2">Trajectory Density (3D View)</h3>
      <Plot
        data={plotData}
        layout={{
          autosize: true,
          title: 'System Complexity Landscape',
          scene: {
            xaxis: { title: 'Time (Ticks)' },
            yaxis: { title: 'Complexity (C)' },
            zaxis: { title: 'Density' },
          },
          margin: { l: 0, r: 0, b: 0, t: 40 },
          paper_bgcolor: '#1f2937', // gray-800
          font: { color: '#ffffff' }
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default DenseLines3D;
