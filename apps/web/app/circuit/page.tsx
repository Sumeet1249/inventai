"use client";

import React from 'react';
import dynamic from 'next/dynamic';
import Navbar from '@/components/ui/Navbar';
import DotGridBackground from '@/components/ui/DotGridBackground';

// Dynamically import with ssr:false — @xyflow/react uses ResizeObserver and
// other DOM APIs that are not available during Next.js server-side pre-render.
const CircuitCanvas = dynamic(
  () => import('@/components/circuit/CircuitCanvas'),
  {
    ssr: false,
    loading: () => (
      <div style={{ width: '100%', height: '600px', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(255,255,255,0.5)', fontSize: '14px', backdropFilter: 'blur(12px)' }}>
        Loading circuit designer...
      </div>
    ),
  }
);

export default function CircuitDesignerPage() {
  return (
    <div style={{ background: '#000', minHeight: '100vh', color: '#fff', fontFamily: '"Google Sans"' }}>
      <DotGridBackground />
      <Navbar variant="dark" showLogo={true} topOffset="4vh" />
      
      <div style={{ padding: '120px 24px 60px', position: 'relative', zIndex: 10 }}>
        <h1 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '8px', color: '#fff' }}>Circuit Designer</h1>
        <p style={{ color: 'rgba(255,255,255,0.6)', marginBottom: '24px' }}>
          Interactive electronics design environment. This canvas represents the canonical internal circuit graph.
        </p>
        
        <CircuitCanvas />
      </div>
    </div>
  );
}
