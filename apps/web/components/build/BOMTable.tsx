'use client';

import React from 'react';

interface BOMTableProps {
  bom: any;
}

export const BOMTable: React.FC<BOMTableProps> = ({ bom }) => {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '13px',
        }}
      >
        <thead>
          <tr style={{ background: 'rgba(59, 130, 246, 0.05)' }}>
            {['Component', 'Category', 'Specs', 'Qty', 'Required'].map((h) => (
              <th
                key={h}
                style={{
                  padding: '10px 12px',
                  textAlign: 'left',
                  color: '#64748B',
                  fontWeight: '600',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  borderBottom: '1px solid rgba(147, 197, 253, 0.3)',
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bom.items.map((item: any, i: number) => (
            <tr
              key={i}
              style={{
                borderBottom: '1px solid rgba(147, 197, 253, 0.15)',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'rgba(59, 130, 246, 0.03)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'transparent';
              }}
            >
              <td style={{ padding: '10px 12px', fontWeight: '600', color: '#0F172A' }}>
                {item.component.name}
              </td>
              <td style={{ padding: '10px 12px', color: '#64748B' }}>
                <span
                  style={{
                    background: 'rgba(37, 99, 235, 0.1)',
                    color: '#1D4ED8',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '600',
                  }}
                >
                  {item.component.category}
                </span>
              </td>
              <td style={{ padding: '10px 12px', color: '#64748B', fontSize: '12px' }}>
                {item.component.voltage && `${item.component.voltage}`}
                {item.component.interface && ` • ${item.component.interface.join(', ')}`}
              </td>
              <td style={{ padding: '10px 12px', fontWeight: '700', color: '#0F172A' }}>
                {item.component.quantity}
              </td>
              <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                {item.component.is_required ? (
                  <span style={{ color: '#15803D', fontWeight: '600' }}>✓</span>
                ) : (
                  <span style={{ color: '#94A3B8', fontSize: '12px' }}>○</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Summary */}
      <div
        style={{
          marginTop: '16px',
          padding: '12px 16px',
          background: 'rgba(59, 130, 246, 0.05)',
          border: '1px solid rgba(147, 197, 253, 0.2)',
          borderRadius: '8px',
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '16px',
        }}
      >
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Total Items
          </div>
          <div style={{ fontSize: '18px', fontWeight: '800', color: '#0F172A', marginTop: '4px' }}>
            {bom.total_components}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Required
          </div>
          <div style={{ fontSize: '18px', fontWeight: '800', color: '#15803D', marginTop: '4px' }}>
            {bom.required_count}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Optional
          </div>
          <div style={{ fontSize: '18px', fontWeight: '800', color: '#F59E0B', marginTop: '4px' }}>
            {bom.optional_count}
          </div>
        </div>
      </div>
    </div>
  );
};
