import React from 'react';

interface CitationGraphProps {
  graphData: {
    nodes: any[];
    edges: any[];
  };
}

export default function CitationGraph({ graphData }: CitationGraphProps) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold text-white mb-4">Citation Graph</h3>
      <div className="h-64 flex items-center justify-center border border-gray-700 rounded bg-gray-900">
        {graphData?.nodes?.length > 0 ? (
          <div className="text-blue-400">
            {/* Real implementation would use react-force-graph or cytoscape */}
            [Graph Visualization: {graphData.nodes.length} nodes, {graphData.edges.length} edges]
          </div>
        ) : (
          <p className="text-gray-500 italic">No citations found to map.</p>
        )}
      </div>
    </div>
  );
}
