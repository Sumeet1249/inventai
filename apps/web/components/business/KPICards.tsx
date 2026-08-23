'use client';

import type { BOMSummary } from '../../types/business';

interface KPICardsProps {
  bomSummary: BOMSummary | null;
  annualVolume?: number;
  bomHealthScore?: number;
}

interface KPICard {
  label: string;
  value: string | number;
  secondary?: string;
  color: string;
  icon: string;
  trend?: { direction: 'up' | 'down'; value: number };
}

export const KPICards: React.FC<KPICardsProps> = ({
  bomSummary,
  annualVolume = 500,
  bomHealthScore,
}) => {
  if (!bomSummary) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '24px' }}>
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            style={{
              background: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              height: '120px',
              animation: 'pulse 2s infinite',
            }}
          />
        ))}
      </div>
    );
  }

  const annualRevenue = bomSummary.target_msrp_usd * annualVolume;
  const annualGrossProfit = bomSummary.unit_gross_profit_usd * annualVolume;

  // Determine margin health
  const marginHealthColor =
    bomSummary.gross_margin_percentage >= 50
      ? '#10B981'
      : bomSummary.gross_margin_percentage >= 35
        ? '#D97706'
        : '#DC2626';

  // Determine revenue health (arbitrary thresholds for demo)
  const revenueHealthColor = annualRevenue >= 3000000 ? '#10B981' : '#D97706';

  // Risk score determination
  let riskLabel = 'Low';
  let riskColor = '#10B981';
  if (bomHealthScore !== undefined) {
    if (bomHealthScore < 50) {
      riskLabel = 'High';
      riskColor = '#DC2626';
    } else if (bomHealthScore < 70) {
      riskLabel = 'Medium';
      riskColor = '#D97706';
    }
  }

  const kpis: KPICard[] = [
    {
      label: 'Unit COGS',
      value: `$${bomSummary.total_unit_cost_usd.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
      secondary: 'Hardware + manufacturing',
      color: '#3B82F6',
      icon: '💰',
    },
    {
      label: 'Target MSRP',
      value: `$${bomSummary.target_msrp_usd.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
      secondary: 'Target selling price',
      color: '#2563EB',
      icon: '🏷️',
    },
    {
      label: 'Gross Margin',
      value: `${bomSummary.gross_margin_percentage.toFixed(1)}%`,
      secondary: `$${bomSummary.unit_gross_profit_usd.toLocaleString('en-US', { minimumFractionDigits: 0 })} per unit`,
      color: marginHealthColor,
      icon: '📈',
    },
    {
      label: 'Annual Revenue Potential',
      value: `$${(annualRevenue / 1000000).toFixed(1)}M`,
      secondary: `${annualVolume.toLocaleString()} units/year`,
      color: revenueHealthColor,
      icon: '💵',
    },
    {
      label: 'BOM Health',
      value: bomHealthScore !== undefined ? `${bomHealthScore}/100` : 'N/A',
      secondary: riskLabel,
      color: riskColor,
      icon: '⚠️',
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '24px' }}>
      {kpis.map((kpi, idx) => (
        <div
          key={idx}
          style={{
            background: '#ffffff',
            border: `1px solid #E2E8F0`,
            borderRadius: '12px',
            padding: '16px 18px',
            borderLeft: `4px solid ${kpi.color}`,
            transition: 'all 0.3s ease',
            cursor: 'default',
            position: 'relative',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.boxShadow =
              '0 4px 12px rgba(0,0,0,0.08)';
            (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.boxShadow = 'none';
            (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
          }}
        >
          {/* Icon */}
          <div style={{ fontSize: '20px', marginBottom: '6px' }}>{kpi.icon}</div>

          {/* Value */}
          <div
            style={{
              fontSize: '22px',
              fontWeight: '800',
              color: '#0F172A',
              letterSpacing: '-0.3px',
              marginBottom: '2px',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {kpi.value}
          </div>

          {/* Label */}
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
            {kpi.label}
          </div>

          {/* Secondary */}
          {kpi.secondary && (
            <div
              style={{
                fontSize: '11px',
                color: '#64748B',
                fontWeight: '500',
                lineHeight: '1.3',
              }}
            >
              {kpi.secondary}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
