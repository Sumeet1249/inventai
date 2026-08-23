'use client';

import type { CostBreakdown, BOMItem } from '../../types/business';

interface CostAnalysisProps {
  costBreakdown?: CostBreakdown;
  bomItems?: BOMItem[];
  totalCOGS?: number;
}

/**
 * Cost Breakdown - Donut chart style visualization
 * Shows: Hardware, Labor, Manufacturing, Packaging, Testing, Shipping, Warranty
 */
export const CostBreakdownChart: React.FC<{ breakdown?: CostBreakdown }> = ({ breakdown }) => {
  if (!breakdown || breakdown.total_unit_cost === 0) {
    return (
      <div
        style={{
          background: '#fff',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '20px',
          height: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#94A3B8',
        }}
      >
        Cost breakdown unavailable
      </div>
    );
  }

  const items = [
    { label: 'Hardware COGS', value: breakdown.hardware_cogs, color: '#3B82F6' },
    { label: 'Assembly Labor', value: breakdown.assembly_labor, color: '#8B5CF6' },
    { label: 'Manufacturing Overhead', value: breakdown.manufacturing_overhead, color: '#EC4899' },
    { label: 'Packaging', value: breakdown.packaging, color: '#F59E0B' },
    { label: 'Testing / QA', value: breakdown.testing_qa, color: '#10B981' },
    { label: 'Shipping Allowance', value: breakdown.shipping_allowance, color: '#06B6D4' },
    { label: 'Warranty Reserve', value: breakdown.warranty_reserve, color: '#D97706' },
  ].filter((item) => item.value > 0);

  const total = breakdown.total_unit_cost;
  const radius = 60;
  const circumference = 2 * Math.PI * radius;

  let offset = 0;
  const segments = items.map((item) => {
    const percentage = (item.value / total) * 100;
    const strokeDasharray = (percentage / 100) * circumference;
    const strokeDashoffset = offset;
    offset += strokeDasharray;

    return {
      ...item,
      percentage,
      strokeDasharray,
      strokeDashoffset,
    };
  });

  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px',
      }}
    >
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
        Unit Cost Structure
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignItems: 'center' }}>
        {/* Donut Chart */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <svg width="200" height="200" viewBox="0 0 200 200" style={{ transform: 'rotate(-90deg)' }}>
            {segments.map((seg, idx) => (
              <circle
                key={idx}
                cx="100"
                cy="100"
                r={radius}
                fill="none"
                stroke={seg.color}
                strokeWidth="20"
                strokeDasharray={seg.strokeDasharray}
                strokeDashoffset={-seg.strokeDashoffset}
                style={{ transition: 'all 0.3s ease' }}
              />
            ))}
            <text
              x="100"
              y="105"
              textAnchor="middle"
              fontSize="20"
              fontWeight="700"
              fill="#0F172A"
              style={{ pointerEvents: 'none' }}
            >
              ${total.toFixed(0)}
            </text>
          </svg>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {segments.map((seg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '12px',
              }}
            >
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '2px',
                  background: seg.color,
                  flexShrink: 0,
                }}
              />
              <div style={{ flex: 1, color: '#475569', fontWeight: '500' }}>{seg.label}</div>
              <div style={{ color: '#0F172A', fontWeight: '700', minWidth: '60px', textAlign: 'right' }}>
                ${seg.value.toFixed(0)} ({seg.percentage.toFixed(1)}%)
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #F1F5F9',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '12px',
        }}
      >
        {items.map((item, idx) => (
          <div
            key={idx}
            style={{
              background: '#F8FAFC',
              padding: '10px 12px',
              borderRadius: '8px',
              borderLeft: `3px solid ${item.color}`,
            }}
          >
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
              {item.label}
            </div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#0F172A' }}>
              ${item.value.toFixed(0)}
            </div>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '500', marginTop: '2px' }}>
              {((item.value / total) * 100).toFixed(1)}% of unit cost
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Cost Concentration - Pareto analysis
 * Top 5 components responsible for X% of total cost
 */
export const CostConcentration: React.FC<{ items?: BOMItem[] }> = ({ items = [] }) => {
  // Calculate top components by extended cost
  const sorted = [...items].sort((a, b) => b.extended_cost_usd - a.extended_cost_usd);
  const top5 = sorted.slice(0, 5);
  const totalCost = items.reduce((sum, item) => sum + item.extended_cost_usd, 0);
  const top5Total = top5.reduce((sum, item) => sum + item.extended_cost_usd, 0);
  const top5Percentage = (top5Total / totalCost) * 100;

  // Cumulative percentages for Pareto
  let cumulative = 0;
  const paretoData = sorted.map((item) => {
    cumulative += item.extended_cost_usd;
    return {
      component: item.component_name,
      cost: item.extended_cost_usd,
      percentage: (item.extended_cost_usd / totalCost) * 100,
      cumulativePercentage: (cumulative / totalCost) * 100,
    };
  });

  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px',
      }}
    >
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
        Cost Concentration Analysis
      </h3>

      {/* Summary */}
      <div
        style={{
          background: '#F0FDF4',
          border: '1px solid #DCFCE7',
          borderRadius: '8px',
          padding: '12px 14px',
          marginBottom: '16px',
          color: '#15803D',
          fontSize: '13px',
          fontWeight: '600',
        }}
      >
        💡 Top 5 components represent <strong>{top5Percentage.toFixed(1)}%</strong> of hardware COGS — focus optimization efforts here for maximum impact.
      </div>

      {/* Bar Chart Visualization */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
        {top5.map((item, idx) => {
          const barWidth = (item.extended_cost_usd / sorted[0].extended_cost_usd) * 100;
          return (
            <div key={idx}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '4px',
                  fontSize: '12px',
                }}
              >
                <span style={{ fontWeight: '600', color: '#0F172A' }}>
                  {idx + 1}. {item.component_name}
                </span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>
                  ${item.extended_cost_usd.toLocaleString('en-US', { maximumFractionDigits: 0 })} ({((item.extended_cost_usd / totalCost) * 100).toFixed(1)}%)
                </span>
              </div>
              <div
                style={{
                  height: '6px',
                  background: '#E2E8F0',
                  borderRadius: '3px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    height: '100%',
                    width: `${barWidth}%`,
                    background: ['#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'][idx],
                    borderRadius: '3px',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Pareto Table */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #F1F5F9',
        }}
      >
        <h4 style={{ fontSize: '12px', fontWeight: '700', color: '#475569', margin: '0 0 8px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Full Pareto Breakdown
        </h4>
        <div style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '11px' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '11px',
            }}
          >
            <thead style={{ position: 'sticky', top: 0, background: '#F8FAFC' }}>
              <tr>
                <th style={{ padding: '6px 8px', textAlign: 'left', color: '#64748B', fontWeight: '700', fontSize: '10px', textTransform: 'uppercase', borderBottom: '1px solid #E2E8F0' }}>
                  Component
                </th>
                <th style={{ padding: '6px 8px', textAlign: 'right', color: '#64748B', fontWeight: '700', fontSize: '10px', textTransform: 'uppercase', borderBottom: '1px solid #E2E8F0' }}>
                  Cost
                </th>
                <th style={{ padding: '6px 8px', textAlign: 'center', color: '#64748B', fontWeight: '700', fontSize: '10px', textTransform: 'uppercase', borderBottom: '1px solid #E2E8F0' }}>
                  %
                </th>
                <th style={{ padding: '6px 8px', textAlign: 'center', color: '#64748B', fontWeight: '700', fontSize: '10px', textTransform: 'uppercase', borderBottom: '1px solid #E2E8F0' }}>
                  Cumulative %
                </th>
              </tr>
            </thead>
            <tbody>
              {paretoData.slice(0, 10).map((item, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #F8FAFC' }}>
                  <td style={{ padding: '6px 8px', color: '#475569', fontWeight: '500' }}>{item.component}</td>
                  <td style={{ padding: '6px 8px', textAlign: 'right', color: '#0F172A', fontWeight: '700', fontFamily: 'monospace' }}>
                    ${item.cost.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td style={{ padding: '6px 8px', textAlign: 'center', color: '#0F172A', fontWeight: '700' }}>
                    {item.percentage.toFixed(1)}%
                  </td>
                  <td style={{ padding: '6px 8px', textAlign: 'center', color: '#0F172A', fontWeight: '700' }}>
                    {item.cumulativePercentage.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
