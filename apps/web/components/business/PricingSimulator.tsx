'use client';

import { useState } from 'react';
import { businessApi } from '../../services/businessApi';

interface PricingSimulatorProps {
  unitCost: number;
  targetMSRP: number;
  annualVolume?: number;
}

export const PricingSimulator: React.FC<PricingSimulatorProps> = ({
  unitCost,
  targetMSRP,
  annualVolume = 500,
}) => {
  const [msrp, setMsrp] = useState(targetMSRP);
  const [targetMargin, setTargetMargin] = useState(0.567);
  const [volume, setVolume] = useState(annualVolume);

  const result = businessApi.calculatePricing(unitCost, msrp, volume);
  const recommendedMSRP = businessApi.calculateRecommendedMSRP(unitCost, targetMargin);
  const marginDiff = recommendedMSRP - msrp;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
      {/* MSRP Simulator */}
      <div
        style={{
          background: '#fff',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '20px',
        }}
      >
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
          MSRP & Margin Analyzer
        </h3>

        {/* MSRP Slider */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '12px' }}>
            <span style={{ color: '#475569', fontWeight: '600' }}>Target MSRP</span>
            <span style={{ color: '#0F172A', fontWeight: '700', fontSize: '16px' }}>
              ${msrp.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </span>
          </div>
          <input
            type="range"
            min={unitCost * 1.2}
            max={unitCost * 4}
            step={100}
            value={msrp}
            onChange={(e) => setMsrp(Number(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '10px', color: '#94A3B8' }}>
            <span>${(unitCost * 1.2).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            <span>${(unitCost * 4).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
          </div>
        </div>

        {/* Volume Input */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '12px', color: '#475569', fontWeight: '600', marginBottom: '6px' }}>
            Annual Volume
          </label>
          <input
            type="number"
            value={volume}
            onChange={(e) => setVolume(Math.max(1, Number(e.target.value)))}
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
        </div>

        {/* Results Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px' }}>
            <div style={{ fontSize: '10px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '4px' }}>
              Gross Profit / Unit
            </div>
            <div style={{ fontSize: '18px', fontWeight: '800', color: '#10B981' }}>
              ${result.grossProfit.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </div>
          </div>
          <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px' }}>
            <div style={{ fontSize: '10px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '4px' }}>
              Gross Margin %
            </div>
            <div style={{ fontSize: '18px', fontWeight: '800', color: '#2563EB' }}>
              {result.grossMarginPercentage.toFixed(1)}%
            </div>
          </div>
          <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px' }}>
            <div style={{ fontSize: '10px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '4px' }}>
              Annual Revenue
            </div>
            <div style={{ fontSize: '18px', fontWeight: '800', color: '#0F172A' }}>
              ${(result.annualRevenue / 1000000).toLocaleString('en-US', { maximumFractionDigits: 2 })}M
            </div>
          </div>
          <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px' }}>
            <div style={{ fontSize: '10px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '4px' }}>
              Annual Gross Profit
            </div>
            <div style={{ fontSize: '18px', fontWeight: '800', color: '#10B981' }}>
              ${(result.annualGrossProfit / 1000000).toLocaleString('en-US', { maximumFractionDigits: 2 })}M
            </div>
          </div>
        </div>
      </div>

      {/* Target Margin Calculator */}
      <div
        style={{
          background: '#fff',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '20px',
        }}
      >
        <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>
          Target Margin Calculator
        </h3>

        {/* Target Margin Slider */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '12px' }}>
            <span style={{ color: '#475569', fontWeight: '600' }}>Target Gross Margin</span>
            <span style={{ color: '#0F172A', fontWeight: '700', fontSize: '16px' }}>
              {(targetMargin * 100).toFixed(1)}%
            </span>
          </div>
          <input
            type="range"
            min={0.1}
            max={0.8}
            step={0.01}
            value={targetMargin}
            onChange={(e) => setTargetMargin(Number(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '10px', color: '#94A3B8' }}>
            <span>10%</span>
            <span>80%</span>
          </div>
        </div>

        {/* Comparison */}
        <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '8px', padding: '12px', marginBottom: '16px', fontSize: '12px' }}>
          <div style={{ color: '#92400E', fontWeight: '600', marginBottom: '8px' }}>
            📊 Recommended vs Current MSRP
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '11px' }}>
            <div>
              <div style={{ color: '#92400E', fontWeight: '600', marginBottom: '2px' }}>Current MSRP</div>
              <div style={{ fontSize: '16px', fontWeight: '800', color: '#B45309' }}>
                ${msrp.toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </div>
            </div>
            <div>
              <div style={{ color: '#92400E', fontWeight: '600', marginBottom: '2px' }}>Recommended MSRP</div>
              <div style={{ fontSize: '16px', fontWeight: '800', color: '#D97706' }}>
                ${recommendedMSRP.toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </div>
            </div>
          </div>
          <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #FCD34D', color: '#92400E', fontWeight: '600', fontSize: '12px' }}>
            {marginDiff > 0 ? (
              <>⬆️ Increase MSRP by ${marginDiff.toLocaleString('en-US', { maximumFractionDigits: 0 })} to hit {(targetMargin * 100).toFixed(1)}% margin</>
            ) : marginDiff < 0 ? (
              <>✓ Current MSRP exceeds target margin by ${Math.abs(marginDiff).toLocaleString('en-US', { maximumFractionDigits: 0 })}</>
            ) : (
              <>✓ Perfect match for {(targetMargin * 100).toFixed(1)}% target margin</>
            )}
          </div>
        </div>

        {/* Unit Cost Breakdown */}
        <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '12px' }}>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>
            Unit Economics
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#475569' }}>MSRP</span>
              <span style={{ fontWeight: '700', color: '#0F172A' }}>${msrp.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#DC2626' }}>
              <span style={{ color: '#475569' }}>- Unit COGS</span>
              <span style={{ fontWeight: '700' }}>-${unitCost.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '6px',
                borderTop: '1px solid #E2E8F0',
                color: '#10B981',
              }}
            >
              <span style={{ color: '#475569', fontWeight: '600' }}>= Gross Profit</span>
              <span style={{ fontWeight: '800', fontSize: '13px' }}>${result.grossProfit.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
