"use client";

import React, { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCircuitStore } from '@/store/useCircuitStore';

// Custom Node for a generic Circuit Component
const ComponentNode = ({ data, isConnectable }: any) => {
  return (
    <div style={{
      padding: '10px',
      border: '2px solid #2563EB',
      borderRadius: '8px',
      background: 'white',
      minWidth: '100px',
      textAlign: 'center',
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
    }}>
      <div style={{ fontSize: '10px', color: '#64748B', fontWeight: 'bold' }}>{data.component_id}</div>
      <div style={{ fontSize: '14px', fontWeight: 'bold', margin: '4px 0' }}>{data.label}</div>
      <div style={{ fontSize: '12px', color: '#059669' }}>{data.value}</div>
      
      {/* 
        This is a simplified visual representation.
        In a real ECAD tool, handles would be mapped dynamically based on the component's pins.
      */}
      <div style={{ position: 'absolute', top: '50%', left: '-5px', width: '10px', height: '10px', background: '#2563EB', borderRadius: '50%', transform: 'translateY(-50%)' }} />
      <div style={{ position: 'absolute', top: '50%', right: '-5px', width: '10px', height: '10px', background: '#2563EB', borderRadius: '50%', transform: 'translateY(-50%)' }} />
    </div>
  );
};

export default function CircuitCanvas() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    setNodes,
    setEdges,
  } = useCircuitStore();

  const nodeTypes = useMemo(() => ({ component: ComponentNode }), []);

  // Mock initial load (this would normally come from the AI/backend)
  const loadMockCircuit = useCallback(() => {
    setNodes([
      {
        id: 'MCU_1',
        type: 'component',
        position: { x: 100, y: 100 },
        data: { label: 'ESP32 DevKit', value: 'ESP32-WROOM-32', component_id: 'U1' },
      },
      {
        id: 'SENSOR_1',
        type: 'component',
        position: { x: 400, y: 100 },
        data: { label: 'BME280 Sensor', value: 'BME280', component_id: 'U2' },
      }
    ]);
    setEdges([
      { id: 'e1-2', source: 'MCU_1', target: 'SENSOR_1', label: 'I2C_SDA', animated: true, style: { stroke: '#2563EB' } }
    ]);
  }, [setNodes, setEdges]);

  return (
    <div style={{ width: '100%', height: '600px', border: '1px solid #E2E8F0', borderRadius: '12px', overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background gap={20} color="#CBD5E1" />
        <Controls />
        <MiniMap />
        
        <Panel position="top-left">
          <div style={{ background: 'white', padding: '12px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>Circuit Designer (Phase 1)</h3>
            <button 
              onClick={loadMockCircuit}
              style={{ background: '#2563EB', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}
            >
              Load Mock Circuit
            </button>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
