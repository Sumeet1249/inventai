'use client';

import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';

const CytoscapeComponent = dynamic(() => import('react-cytoscapejs'), { ssr: false });

export default function GraphViewer({ graphData }: { graphData: any }) {
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [layoutName, setLayoutName] = useState('cose');

  const elements = React.useMemo(() => {
    if (!graphData) return [];
    let els: any[] = [];
    if (graphData.nodes) els = els.concat(graphData.nodes);
    if (graphData.edges) els = els.concat(graphData.edges);
    return els;
  }, [graphData]);

  const style = [
    {
      selector: 'node',
      style: {
        'background-color': '#3b82f6',
        'label': 'data(label)',
        'color': '#fff',
        'font-size': '12px',
        'text-halign': 'center',
        'text-valign': 'center',
        'width': 40,
        'height': 40,
      }
    },
    {
      selector: 'node:selected',
      style: {
        'border-width': 4,
        'border-color': '#fbbf24'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#4b5563',
        'target-arrow-color': '#4b5563',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '10px',
        'color': '#9ca3af',
        'text-rotation': 'autorotate'
      }
    }
  ];

  const handleNodeClick = useCallback((event: any) => {
    setSelectedNode(event.target.data());
  }, []);

  return (
    <div className="w-full h-96 flex bg-gray-900 rounded-lg overflow-hidden border border-gray-700 relative">
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-2">
        <div className="bg-black/50 px-2 py-1 text-xs text-blue-400 font-mono rounded">
          Nodes: {graphData?.nodes?.length || 0} | Edges: {graphData?.edges?.length || 0}
        </div>
        <select 
          className="bg-gray-800 text-xs text-white p-1 rounded border border-gray-600 outline-none"
          value={layoutName}
          onChange={e => setLayoutName(e.target.value)}
        >
          <option value="cose">CoSE (Force-directed)</option>
          <option value="grid">Grid</option>
          <option value="circle">Circle</option>
          <option value="concentric">Concentric</option>
          <option value="breadthfirst">Hierarchical</option>
        </select>
      </div>

      <div className="flex-1 relative">
        <CytoscapeComponent 
          elements={elements} 
          stylesheet={style as any}
          style={{ width: '100%', height: '100%' }} 
          layout={{ name: layoutName, animate: true }}
          cy={(cy: any) => {
            cy.on('tap', 'node', handleNodeClick);
            cy.on('tap', (event: any) => {
              if (event.target === cy) setSelectedNode(null);
            });
          }}
        />
      </div>

      {selectedNode && (
        <div className="w-64 bg-gray-800 border-l border-gray-700 p-4 overflow-y-auto">
          <h3 className="text-lg font-bold text-white mb-2 border-b border-gray-700 pb-2">Node Details</h3>
          <div className="space-y-2">
            {Object.entries(selectedNode).map(([key, value]) => (
              <div key={key}>
                <span className="text-xs text-gray-400 uppercase font-semibold">{key}</span>
                <p className="text-sm text-gray-200 break-words">{String(value)}</p>
              </div>
            ))}
          </div>
          <button 
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-1.5 rounded transition"
            onClick={() => {/* Would trigger expand neighbors */}}
          >
            Expand Neighbors
          </button>
        </div>
      )}
    </div>
  );
}
