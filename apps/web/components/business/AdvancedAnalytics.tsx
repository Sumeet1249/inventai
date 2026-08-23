'use client';

import type { BOMItem, SupplierInfo, RiskAlert, MarketSizing } from '../../types/business';
import { businessApi } from '../../services/businessApi';

/**
 * Task 11: Sensitivity Heatmap
 */
export const SensitivityHeatmap: React.FC<{ msrp: number; unitCost: number }> = ({ msrp, unitCost }) => {
  const grid = businessApi.generateSensitivityGrid(msrp, unitCost);

  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
      }}
    >
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
        Profit Sensitivity Analysis
      </h3>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ fontSize: '10px', borderCollapse: 'collapse', minWidth: '600px' }}>
          <thead>
            <tr>
              <th style={{ padding: '4px 6px', textAlign: 'center', color: '#94A3B8', fontWeight: '600', background: '#F8FAFC' }}>
                COGS ↓ / MSRP →
              </th>
              {grid.msrpRange.map((msrp, i) => (
                <th
                  key={i}
                  style={{
                    padding: '4px 6px',
                    textAlign: 'center',
                    color: '#64748B',
                    fontWeight: '600',
                    background: '#F8FAFC',
                    fontSize: '9px',
                  }}
                >
                  ${msrp.toLocaleString()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {grid.cogsRange.map((cogs, rowIdx) => (
              <tr key={rowIdx}>
                <td
                  style={{
                    padding: '4px 6px',
                    textAlign: 'center',
                    color: '#64748B',
                    fontWeight: '600',
                    background: '#F8FAFC',
                    fontSize: '9px',
                  }}
                >
                  ${cogs.toLocaleString()}
                </td>
                {grid.margins[rowIdx].map((margin, colIdx) => {
                  let bg = '#E0F2FE';
                  let color = '#0C4A6E';
                  if (margin >= 60) {
                    bg = '#D1FAE5';
                    color = '#065F46';
                  } else if (margin >= 45) {
                    bg = '#FEF3C7';
                    color = '#92400E';
                  } else if (margin < 20) {
                    bg = '#FEE2E2';
                    color = '#991B1B';
                  }
                  return (
                    <td
                      key={colIdx}
                      style={{
                        padding: '6px 4px',
                        textAlign: 'center',
                        background: bg,
                        color: color,
                        fontWeight: '700',
                        fontSize: '10px',
                        border: '1px solid #E2E8F0',
                      }}
                      title={`Margin: ${margin.toFixed(1)}%`}
                    >
                      {margin.toFixed(0)}%
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ fontSize: '11px', color: '#64748B', marginTop: '12px' }}>
        💡 This matrix shows gross margin % for different pricing and cost scenarios. Green = healthy (60%+), Yellow = good (45%+), Red = risky (&lt;20%).
      </div>
    </div>
  );
};

/**
 * Task 12: Market Sizing
 */
export const MarketSizingVisualization: React.FC<{ market?: MarketSizing }> = ({ market }) => {
  if (!market) {
    return (
      <div
        style={{
          background: '#fff',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '40px 20px',
          textAlign: 'center',
          color: '#94A3B8',
        }}
      >
        Market sizing data unavailable
      </div>
    );
  }

  const tamToSam = market.tam_usd > 0 ? (market.sam_usd / market.tam_usd) * 100 : 0;
  const samToSom = market.sam_usd > 0 ? (market.som_usd / market.sam_usd) * 100 : 0;

  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
      }}
    >
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
        Market Opportunity (TAM / SAM / SOM)
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Nested Circles Visualization */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '220px', height: '220px' }}>
            {/* TAM */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                borderRadius: '50%',
                background: '#EFF6FF',
                border: '2px solid #3B82F6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <div style={{ textAlign: 'center', fontSize: '11px' }}>
                <div style={{ fontWeight: '700', color: '#3B82F6' }}>TAM</div>
                <div style={{ fontSize: '10px', color: '#64748B' }}>
                  ${(market.tam_usd / 1000000000).toFixed(2)}B
                </div>
              </div>
            </div>

            {/* SAM */}
            <div
              style={{
                position: 'absolute',
                inset: '25%',
                borderRadius: '50%',
                background: '#FEF3C7',
                border: '2px solid #F59E0B',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <div style={{ textAlign: 'center', fontSize: '11px' }}>
                <div style={{ fontWeight: '700', color: '#D97706' }}>SAM</div>
                <div style={{ fontSize: '10px', color: '#64748B' }}>
                  ${(market.sam_usd / 1000000000).toFixed(2)}B
                </div>
              </div>
            </div>

            {/* SOM */}
            <div
              style={{
                position: 'absolute',
                inset: '50%',
                borderRadius: '50%',
                background: '#D1FAE5',
                border: '2px solid #10B981',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <div style={{ textAlign: 'center', fontSize: '11px' }}>
                <div style={{ fontWeight: '700', color: '#10B981' }}>SOM</div>
                <div style={{ fontSize: '10px', color: '#64748B' }}>
                  ${(market.som_usd / 1000000).toFixed(0)}M
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '12px', borderLeft: '4px solid #3B82F6' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600', marginBottom: '4px' }}>
              TAM — Total Addressable Market
            </div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#3B82F6' }}>
              ${(market.tam_usd / 1000000000).toFixed(2)}B
            </div>
          </div>

          <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '12px', borderLeft: '4px solid #F59E0B' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600', marginBottom: '4px' }}>
              SAM — Serviceable Available Market
            </div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#D97706' }}>
              ${(market.sam_usd / 1000000000).toFixed(2)}B ({tamToSam.toFixed(1)}% of TAM)
            </div>
          </div>

          <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '12px', borderLeft: '4px solid #10B981' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600', marginBottom: '4px' }}>
              SOM — Serviceable Obtainable Market
            </div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#10B981' }}>
              ${(market.som_usd / 1000000).toFixed(0)}M ({samToSom.toFixed(1)}% of SAM)
            </div>
          </div>

          {/* Customer Segments */}
          {market.customer_segments && market.customer_segments.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600', marginBottom: '6px' }}>
                Target Customer Segments
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {market.customer_segments.slice(0, 3).map((seg, idx) => (
                  <div
                    key={idx}
                    style={{
                      fontSize: '11px',
                      color: '#475569',
                      padding: '4px 8px',
                      background: '#F1F5F9',
                      borderRadius: '4px',
                    }}
                  >
                    • {seg}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Task 13: Supplier Analysis
 */
export const SupplierAnalysis: React.FC<{ suppliers?: SupplierInfo[] }> = ({ suppliers = [] }) => {
  if (suppliers.length === 0) {
    return (
      <div
        style={{
          background: '#fff',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '40px 20px',
          textAlign: 'center',
          color: '#94A3B8',
        }}
      >
        No supplier data available
      </div>
    );
  }

  const totalSpend = suppliers.reduce((sum, s) => sum + s.spend_usd, 0);
  const singleSourceRisk = suppliers.filter((s) => s.name === suppliers[0].name).length;

  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
      }}
    >
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
        Supplier Analysis
      </h3>

      <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
          <thead>
            <tr style={{ background: '#F8FAFC' }}>
              {['Supplier', 'Components', 'Spend', 'Concentration', 'Availability', 'Lead Time', 'Risk'].map((h) => (
                <th
                  key={h}
                  style={{
                    padding: '10px 12px',
                    textAlign: 'left',
                    color: '#64748B',
                    fontWeight: '700',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    borderBottom: '1px solid #E2E8F0',
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {suppliers.map((supplier, idx) => {
              const concentration = ((supplier.spend_usd / totalSpend) * 100).toFixed(1);
              const isHighConcentration = parseFloat(concentration) > 30;
              return (
                <tr key={idx} style={{ borderBottom: '1px solid #F8FAFC' }}>
                  <td style={{ padding: '10px 12px', fontWeight: '600', color: '#0F172A' }}>
                    {supplier.name}
                  </td>
                  <td style={{ padding: '10px 12px', color: '#475569' }}>{supplier.component_count}</td>
                  <td style={{ padding: '10px 12px', fontWeight: '700', color: '#0F172A' }}>
                    ${supplier.spend_usd.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                  </td>
                  <td
                    style={{
                      padding: '10px 12px',
                      fontWeight: '700',
                      color: isHighConcentration ? '#DC2626' : '#10B981',
                      background: isHighConcentration ? '#FEE2E2' : '#F0FDF4',
                    }}
                  >
                    {concentration}%
                  </td>
                  <td style={{ padding: '10px 12px', color: '#475569' }}>
                    {supplier.availability || 'Available'}
                  </td>
                  <td style={{ padding: '10px 12px', color: '#475569' }}>
                    {supplier.lead_time_days || '—'} days
                  </td>
                  <td style={{ padding: '10px 12px' }}>
                    <span
                      style={{
                        background: supplier.risk_level === 'high' ? '#FEE2E2' : supplier.risk_level === 'medium' ? '#FEF3C7' : '#F0FDF4',
                        color: supplier.risk_level === 'high' ? '#DC2626' : supplier.risk_level === 'medium' ? '#D97706' : '#10B981',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: '700',
                        textTransform: 'capitalize',
                      }}
                    >
                      {supplier.risk_level || 'Low'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Concentration Alert */}
      {suppliers[0]?.spend_usd && (suppliers[0].spend_usd / totalSpend) > 0.3 && (
        <div
          style={{
            background: '#FEF3C7',
            border: '1px solid #FCD34D',
            borderRadius: '8px',
            padding: '12px 14px',
            color: '#92400E',
            fontSize: '12px',
            fontWeight: '600',
          }}
        >
          ⚠️ {((suppliers[0].spend_usd / totalSpend) * 100).toFixed(0)}% of BOM value depends on {suppliers[0].name}. Consider diversifying suppliers.
        </div>
      )}
    </div>
  );
};

/**
 * Task 14: Risk Alerts
 */
export const RiskAlerts: React.FC<{ alerts?: RiskAlert[] }> = ({ alerts = [] }) => {
  if (alerts.length === 0) {
    return null;
  }

  const grouped = alerts.reduce(
    (acc, alert) => {
      if (!acc[alert.severity]) acc[alert.severity] = [];
      acc[alert.severity].push(alert);
      return acc;
    },
    {} as Record<string, RiskAlert[]>
  );

  const severityOrder = ['error', 'warning', 'info', 'success'];
  const severityConfig: Record<string, { bg: string; border: string; icon: string }> = {
    error: { bg: '#FEE2E2', border: '#FECACA', icon: '🔴' },
    warning: { bg: '#FEF3C7', border: '#FCD34D', icon: '🟡' },
    info: { bg: '#EFF6FF', border: '#BFDBFE', icon: '🔵' },
    success: { bg: '#F0FDF4', border: '#BBEF7D', icon: '🟢' },
  };

  return (
    <div style={{ marginBottom: '24px' }}>
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
        Risk Alerts
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {severityOrder.flatMap((sev) =>
          (grouped[sev] || []).map((alert) => {
            const config = severityConfig[sev];
            return (
              <div
                key={alert.id}
                style={{
                  background: config.bg,
                  border: `1px solid ${config.border}`,
                  borderRadius: '8px',
                  padding: '12px 14px',
                  fontSize: '12px',
                }}
              >
                <div style={{ fontWeight: '700', marginBottom: '4px' }}>
                  {config.icon} {alert.title}
                </div>
                <div style={{ fontSize: '11px', color: '#475569', marginBottom: '4px' }}>
                  {alert.description}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

/**
 * Task 15: Export Center
 */
export const ExportCenter: React.FC<{
  projectId: string;
  exportFiles?: Record<string, string | undefined>;
}> = ({ projectId, exportFiles = {} }) => {
  const exports = [
    { key: 'bom_csv_url', label: '📊 Download BOM (CSV)', color: '#3B82F6' },
    { key: 'financial_proforma_excel_url', label: '💰 Download Financial Pro Forma (Excel)', color: '#10B981' },
    { key: 'business_report_pdf_url', label: '📄 Download Business Report (PDF)', color: '#8B5CF6' },
    { key: 'cost_analysis_url', label: '💡 Download Cost Analysis', color: '#D97706' },
  ];

  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
      }}
    >
      <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
        Export Reports
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
        {exports.map((exp) => {
          const url = exportFiles[exp.key as keyof typeof exportFiles];
          const isAvailable = !!url;

          return (
            <a
              key={exp.key}
              href={url || '#'}
              target={isAvailable ? '_blank' : undefined}
              rel={isAvailable ? 'noopener noreferrer' : undefined}
              style={{
                display: 'block',
                background: isAvailable ? '#F8FAFC' : '#F1F5F9',
                border: `1px solid ${isAvailable ? '#E2E8F0' : '#CBD5E1'}`,
                borderRadius: '8px',
                padding: '14px 16px',
                textAlign: 'center',
                color: isAvailable ? exp.color : '#94A3B8',
                textDecoration: 'none',
                fontWeight: '600',
                fontSize: '12px',
                cursor: isAvailable ? 'pointer' : 'not-allowed',
                opacity: isAvailable ? 1 : 0.6,
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                if (isAvailable) {
                  (e.currentTarget as HTMLElement).style.background = '#EFF6FF';
                  (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                }
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = '#F8FAFC';
                (e.currentTarget as HTMLElement).style.boxShadow = 'none';
              }}
              title={isAvailable ? undefined : 'This export is not yet available'}
            >
              {exp.label}
            </a>
          );
        })}
      </div>
    </div>
  );
};
