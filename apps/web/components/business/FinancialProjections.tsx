'use client';

import { useState } from 'react';
import type { FinancialProjection, Scenario, FinancialYear } from '../../types/business';
import { businessApi } from '../../services/businessApi';

interface FinancialProjectionsProps {
  projections?: FinancialProjection;
  unitCost: number;
  msrp: number;
}

export const FinancialProjections: React.FC<FinancialProjectionsProps> = ({
  projections,
  unitCost,
  msrp,
}) => {
  if (!projections) {
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
        Loading financial projections…
      </div>
    );
  }

  const years = [projections.year_1, projections.year_2, projections.year_3];
  const maxRevenue = Math.max(...years.map((y) => y.revenue_usd));
  const maxProfit = Math.max(...years.map((y) => y.gross_profit_usd));

  return (
    <div style={{ marginBottom: '24px' }}>
      {/* Table */}
      <div
        style={{
          background: '#fff',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px',
        }}
      >
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
          3-Year Financial Projections
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ background: '#F8FAFC' }}>
                {['Metric', 'Year 1', 'Year 2', 'Year 3', 'Total'].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: '10px 12px',
                      textAlign: h === 'Metric' ? 'left' : 'right',
                      color: '#64748B',
                      fontWeight: '700',
                      fontSize: '11px',
                      textTransform: 'uppercase',
                      borderBottom: '1px solid #E2E8F0',
                      letterSpacing: '0.05em',
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                {
                  label: 'Units Sold',
                  get: (y: FinancialYear) => y.units_sold.toLocaleString(),
                  total: years.reduce((s, y) => s + y.units_sold, 0).toLocaleString(),
                },
                {
                  label: 'Revenue',
                  get: (y: FinancialYear) => `$${(y.revenue_usd / 1000000).toFixed(2)}M`,
                  total: `$${years.reduce((s, y) => s + y.revenue_usd, 0) / 1000000}M`,
                },
                {
                  label: 'COGS',
                  get: (y: FinancialYear) => `$${(y.cogs_usd / 1000000).toFixed(2)}M`,
                  total: `$${years.reduce((s, y) => s + y.cogs_usd, 0) / 1000000}M`,
                },
                {
                  label: 'Gross Profit',
                  get: (y: FinancialYear) => `$${(y.gross_profit_usd / 1000000).toFixed(2)}M`,
                  total: `$${years.reduce((s, y) => s + y.gross_profit_usd, 0) / 1000000}M`,
                },
                {
                  label: 'Gross Margin %',
                  get: (y: FinancialYear) => `${y.gross_margin_percentage.toFixed(1)}%`,
                  total: '',
                },
              ].map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #F8FAFC' }}>
                  <td style={{ padding: '10px 12px', color: '#475569', fontWeight: '600' }}>
                    {row.label}
                  </td>
                  {years.map((y, i) => (
                    <td
                      key={i}
                      style={{
                        padding: '10px 12px',
                        textAlign: 'right',
                        color: '#0F172A',
                        fontWeight: '700',
                        fontFamily: 'monospace',
                      }}
                    >
                      {row.get(y)}
                    </td>
                  ))}
                  <td
                    style={{
                      padding: '10px 12px',
                      textAlign: 'right',
                      color: '#0F172A',
                      fontWeight: '800',
                      fontFamily: 'monospace',
                      background: '#F8FAFC',
                    }}
                  >
                    {row.total}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
        {/* Revenue Chart */}
        <div
          style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '16px',
          }}
        >
          <h4 style={{ fontSize: '12px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
            Revenue Growth
          </h4>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: '120px', gap: '8px' }}>
            {years.map((y, idx) => (
              <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '100%',
                    height: (y.revenue_usd / maxRevenue) * 100,
                    background: '#3B82F6',
                    borderRadius: '4px 4px 0 0',
                    minHeight: '20px',
                  }}
                  title={`Year ${idx + 1}: $${(y.revenue_usd / 1000000).toFixed(2)}M`}
                />
                <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '4px' }}>Y{idx + 1}</div>
              </div>
            ))}
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '8px', textAlign: 'center' }}>
            Total: ${years.reduce((s, y) => s + y.revenue_usd, 0) / 1000000}M
          </div>
        </div>

        {/* Gross Profit Chart */}
        <div
          style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '16px',
          }}
        >
          <h4 style={{ fontSize: '12px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
            Gross Profit Growth
          </h4>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: '120px', gap: '8px' }}>
            {years.map((y, idx) => (
              <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '100%',
                    height: (y.gross_profit_usd / maxProfit) * 100,
                    background: '#10B981',
                    borderRadius: '4px 4px 0 0',
                    minHeight: '20px',
                  }}
                  title={`Year ${idx + 1}: $${(y.gross_profit_usd / 1000000).toFixed(2)}M`}
                />
                <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '4px' }}>Y{idx + 1}</div>
              </div>
            ))}
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '8px', textAlign: 'center' }}>
            Total: ${years.reduce((s, y) => s + y.gross_profit_usd, 0) / 1000000}M
          </div>
        </div>

        {/* Units Chart */}
        <div
          style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '16px',
          }}
        >
          <h4 style={{ fontSize: '12px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
            Unit Volume
          </h4>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: '120px', gap: '8px' }}>
            {years.map((y, idx) => {
              const maxUnits = Math.max(...years.map((yr) => yr.units_sold));
              return (
                <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div
                    style={{
                      width: '100%',
                      height: (y.units_sold / maxUnits) * 100,
                      background: '#8B5CF6',
                      borderRadius: '4px 4px 0 0',
                      minHeight: '20px',
                    }}
                    title={`Year ${idx + 1}: ${y.units_sold.toLocaleString()} units`}
                  />
                  <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '4px' }}>Y{idx + 1}</div>
                </div>
              );
            })}
          </div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '8px', textAlign: 'center' }}>
            Total: {years.reduce((s, y) => s + y.units_sold, 0).toLocaleString()} units
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Scenario Simulator - Conservative/Base/Aggressive
 */
interface ScenarioSimulatorProps {
  baseAnalysis: {
    unitCost: number;
    msrp: number;
  };
}

export const ScenarioSimulator: React.FC<ScenarioSimulatorProps> = ({ baseAnalysis }) => {
  const [scenarios, setScenarios] = useState<Record<string, Scenario>>({
    conservative: {
      name: 'Conservative',
      units_sold: 300,
      msrp_usd: baseAnalysis.msrp * 0.9,
      unit_cogs_reduction_percent: 0,
    },
    base: {
      name: 'Base',
      units_sold: 500,
      msrp_usd: baseAnalysis.msrp,
      unit_cogs_reduction_percent: 5,
    },
    aggressive: {
      name: 'Aggressive',
      units_sold: 1000,
      msrp_usd: baseAnalysis.msrp * 1.1,
      unit_cogs_reduction_percent: 10,
    },
  });

  // Calculate results for each scenario
  const results = Object.entries(scenarios).map(([key, scenario]) => {
    const adjustedCOGS = baseAnalysis.unitCost * (1 - scenario.unit_cogs_reduction_percent / 100);
    const result = businessApi.calculatePricing(adjustedCOGS, scenario.msrp_usd, scenario.units_sold);
    return {
      key,
      name: scenario.name,
      ...result,
      unitsSold: scenario.units_sold,
    };
  });

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
        Scenario Planning
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
        {results.map((scenario) => (
          <div
            key={scenario.key}
            style={{
              background: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '10px',
              padding: '16px',
            }}
          >
            <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
              {scenario.name} Scenario
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569' }}>Annual Volume</span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>{scenario.unitsSold.toLocaleString()} units</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569' }}>MSRP</span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>
                  ${scenario.msrp.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569' }}>Unit COGS</span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>
                  ${scenario.unitCost.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  paddingTop: '8px',
                  borderTop: '1px solid #E2E8F0',
                  marginTop: '8px',
                }}
              >
                <span style={{ color: '#475569', fontWeight: '600' }}>Revenue</span>
                <span style={{ fontWeight: '800', color: '#0F172A', fontSize: '13px' }}>
                  ${(scenario.annualRevenue / 1000000).toFixed(2)}M
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569', fontWeight: '600' }}>Gross Profit</span>
                <span style={{ fontWeight: '800', color: '#10B981' }}>
                  ${(scenario.annualGrossProfit / 1000000).toFixed(2)}M
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569', fontWeight: '600' }}>Margin %</span>
                <span style={{ fontWeight: '800', color: '#2563EB' }}>{scenario.grossMarginPercentage.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
