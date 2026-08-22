"use client";

import React from 'react';
import dynamic from 'next/dynamic';

// Dynamically import with ssr:false — @xyflow/react uses ResizeObserver and
// other DOM APIs that are not available during Next.js server-side pre-render.
const CircuitCanvas = dynamic(
  () => import('@/components/circuit/CircuitCanvas'),
  {
    ssr: false,
    loading: () => (
      <div style={{ width: '100%', height: '600px', border: '1px solid #E2E8F0', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94A3B8', fontSize: '14px' }}>
        Loading circuit designer...
      </div>
    ),
  }
);

export default function CircuitDesignerPage() {
  return (
    <div style={{ padding: '24px', fontFamily: 'Inter, sans-serif' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>Circuit Designer</h1>
      <p style={{ color: '#64748B', marginBottom: '24px' }}>
        Interactive electronics design environment. This canvas represents the canonical internal circuit graph.
      </p>
      
      <CircuitCanvas />
    </div>
  );
}
