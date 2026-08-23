'use client';

import { useState } from 'react';
import { businessApi } from '../../services/businessApi';

interface BreakEvenAnalysisProps {
  unitCost: number;
  msrp: number;
}

export const BreakEvenAnalysis: React.FC<BreakEvenAnalysisProps> = ({ unitCost, msrp }) => {
  const [fixedCosts, setFixedCosts] = useState(500000); // $500k default
  const analysis = businessApi.calculateBreakEven(fixedCosts, msrp, unitCost);

  // Generate chart data
  const units = Array.from({ length: 21 }, (_, i) => (analysis.breakeven_units / 20) * i);
  const chartData = units.map((u) => ({
    units: Math.round(u),
    revenue: u * msrp,
    cogs: u * unitCost,
    profit: u * (msrp - unitCost) - fixedCosts,
  }));

  const maxProfit = Math.max(...chartData.map((d) => d.profit));
  const minProfit = Math.min(...chartData.map((d) => d.profit));
  const profitRange = maxProfit - minProfit || 1;

  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Left: Inputs & Results */}
        <div
          style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '20px',
          }}
        >
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
            Break-Even Calculator
          </h3>

          {/* Fixed Costs Input */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '12px', color: '#475569', fontWeight: '600', marginBottom: '6px' }}>
              Fixed Costs (Annual)
            </label>
            <input
              type="number"
              value={fixedCosts}
              onChange={(e) => setFixedCosts(Math.max(0, Number(e.target.value)))}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '13px',
                fontFamily: 'inherit',
                boxSizing: 'border-box',
              }}
            />
            <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '4px' }}>
              Includes salaries, rent, utilities, marketing
            </div>
          </div>

          {/* Breakdown */}
          <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '12px', marginBottom: '16px' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '10px', letterSpacing: '0.05em' }}>
              Inputs
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569' }}>Fixed Costs</span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>${fixedCosts.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569' }}>Unit Selling Price</span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>${msrp.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#475569' }}>Unit Variable Cost</span>
                <span style={{ fontWeight: '700', color: '#0F172A' }}>${unitCost.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
              </div>
            </div>
          </div>

          {/* Results */}
          <div style={{ background: '#EFF6FF', borderRadius: '8px', padding: '12px', border: '1px solid #BFDBFE' }}>
            <div style={{ fontSize: '11px', color: '#1D4ED8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '10px', letterSpacing: '0.05em' }}>
              Break-Even Results
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div>
                <div style={{ color: '#1D4ED8', fontWeight: '600', marginBottom: '2px' }}>Break-Even Units</div>
                <div style={{ fontSize: '20px', fontWeight: '800', color: '#1D4ED8' }}>
                  {analysis.breakeven_units.toLocaleString()} units
                </div>
              </div>
              <div>
                <div style={{ color: '#1D4ED8', fontWeight: '600', marginBottom: '2px' }}>Break-Even Revenue</div>
                <div style={{ fontSize: '16px', fontWeight: '800', color: '#1D4ED8' }}>
                  ${analysis.breakeven_revenue.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                </div>
              </div>
              <div>
                <div style={{ color: '#1D4ED8', fontWeight: '600', marginBottom: '2px' }}>Contribution Margin</div>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#1D4ED8' }}>
                  ${analysis.contribution_margin.toLocaleString('en-US', { maximumFractionDigits: 0 })} per unit
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Chart */}
        <div
          style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '20px',
          }}
        >
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
            Profit vs Units Sold
          </h3>

          {/* Simple ASCII-style chart */}
          <div style={{ position: 'relative', height: '200px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            {/* Grid lines */}
            <svg
              width="100%"
              height="100%"
              style={{ position: 'absolute', top: 0, left: 0 }}
            >
              {/* Horizontal grid */}
              {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => (
                <line
                  key={`h-${idx}`}
                  x1="40"
                  y1={200 - pct * 180}
                  x2="100%"
                  y2={200 - pct * 180}
                  stroke="#F1F5F9"
                  strokeWidth="1"
                />
              ))}
              {/* Vertical grid (break-even line) */}
              <line
                x1={40 + ((chartData.length - 1) * (100 - 40) * analysis.breakeven_units) / (analysis.breakeven_units * 2)}
                y1="0"
                x2={40 + ((chartData.length - 1) * (100 - 40) * analysis.breakeven_units) / (analysis.breakeven_units * 2)}
                y2="200"
                stroke="#DC2626"
                strokeWidth="2"
                strokeDasharray="5,5"
              />
            </svg>

            {/* Bars */}
            <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: '180px', paddingBottom: '10px' }}>
              {chartData.map((d, idx) => {
                const barHeight = ((d.profit - minProfit) / profitRange) * 180;
                const isBreakEven = d.units >= analysis.breakeven_units && chartData[idx + 1]?.units < analysis.breakeven_units;
                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      flex: 1,
                    }}
                  >
                    <div
                      style={{
                        width: '8px',
                        height: barHeight,
                        background: d.profit >= 0 ? '#10B981' : '#DC2626',
                        borderRadius: '2px 2px 0 0',
                        transition: 'all 0.2s',
                      }}
                      title={`${d.units} units: $${d.profit.toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
                    />
                  </div>
                );
              })}
            </div>

            {/* X-axis */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '10px',
                color: '#94A3B8',
                paddingTop: '6px',
              }}
            >
              <span>0</span>
              <span>{(analysis.breakeven_units * 2).toLocaleString()} units</span>
            </div>
          </div>

          {/* Legend */}
          <div
            style={{
              marginTop: '12px',
              display: 'flex',
              gap: '16px',
              fontSize: '11px',
              color: '#475569',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  background: '#10B981',
                  borderRadius: '2px',
                }}
              />
              Profitable
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  background: '#DC2626',
                  borderRadius: '2px',
                }}
              />
              Loss
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '12px', height: '1px', background: '#DC2626' }} />
              Break-Even Point
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
