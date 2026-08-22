import React from 'react';

export default function CitationGraph({ graphData }: { graphData: any }) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h3 className="text-lg font-bold text-white mb-2">Citation Graph</h3>
      <p className="text-gray-400 text-sm">Visualizer loading...</p>
    </div>
  );
}
