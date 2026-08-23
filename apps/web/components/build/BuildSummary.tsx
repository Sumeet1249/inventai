'use client';

import React from 'react';

interface BuildSummaryProps {
  bom: any;
  onStart: () => void;
  loading: boolean;
}

export const BuildSummary: React.FC<BuildSummaryProps> = ({ bom, onStart, loading }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#0F172A', marginBottom: '8px' }}>
          Your Design Is Ready to Build
        </h3>
        <p style={{ fontSize: '13px', color: '#64748B', margin: 0 }}>
          We've analyzed your circuit, PCB, and CAD and identified all required components. Let's find the best
          products to bring your design to life.
        </p>
      </div>

      {/* Stats Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '16px',
        }}
      >
        <div
          style={{
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            borderRadius: '10px',
            padding: '16px',
          }}
        >
          <div style={{ fontSize: '11px', color: '#15803D', fontWeight: '700', textTransform: 'uppercase' }}>
            Total Components
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#15803D', marginTop: '4px' }}>
            {bom.total_components}
          </div>
        </div>

        <div
          style={{
            background: 'rgba(37, 99, 235, 0.1)',
            border: '1px solid rgba(37, 99, 235, 0.3)',
            borderRadius: '10px',
            padding: '16px',
          }}
        >
          <div style={{ fontSize: '11px', color: '#1D4ED8', fontWeight: '700', textTransform: 'uppercase' }}>
            Required
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#1D4ED8', marginTop: '4px' }}>
            {bom.required_count}
          </div>
        </div>

        <div
          style={{
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '10px',
            padding: '16px',
          }}
        >
          <div style={{ fontSize: '11px', color: '#B45309', fontWeight: '700', textTransform: 'uppercase' }}>
            Optional
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#B45309', marginTop: '4px' }}>
            {bom.optional_count}
          </div>
        </div>
      </div>

      {/* Component List */}
      <div>
        <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A', marginBottom: '12px' }}>
          Core Components Found
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
          {bom.items.slice(0, 6).map((item: any, i: number) => (
            <div
              key={i}
              style={{
                background: 'rgba(59, 130, 246, 0.05)',
                border: '1px solid rgba(147, 197, 253, 0.2)',
                borderRadius: '8px',
                padding: '10px 12px',
                fontSize: '12px',
              }}
            >
              <div style={{ fontWeight: '600', color: '#0F172A' }}>✓ {item.component.name}</div>
              <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
                {item.component.category} • Qty: {item.component.quantity}
              </div>
            </div>
          ))}
        </div>

        {bom.total_components > 6 && (
          <div style={{ fontSize: '12px', color: '#64748B', marginTop: '8px' }}>
            + {bom.total_components - 6} more components
          </div>
        )}
      </div>

      {/* Next Steps */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%)',
          border: '1px solid rgba(147, 197, 253, 0.3)',
          borderRadius: '10px',
          padding: '16px',
        }}
      >
        <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A', margin: '0 0 8px 0' }}>
          💡 Next Step
        </h4>
        <p style={{ fontSize: '12px', color: '#64748B', margin: '0 0 12px 0' }}>
          Click the button below to search for real products from Robu.in, Amazon India, and Flipkart. We'll match
          each component and show you the best options with pricing and availability.
        </p>

        <button
          onClick={onStart}
          disabled={loading}
          style={{
            background: loading ? '#93C5FD' : 'linear-gradient(135deg, #2563EB, #1D4ED8)',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: '700',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            width: 'fit-content',
          }}
        >
          {loading ? '⟳ Searching products...' : '🔍 Search for Products'}
        </button>
      </div>
    </div>
  );
};
