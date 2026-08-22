'use client';

import React, { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Shield, AlertTriangle, CheckCircle, Thermometer, Zap, Wind, ChevronDown } from 'lucide-react';

interface PhysicsViewerProps {
  data: any;
  cadModelUrl?: string | null;
}

// ────────── Load Case Presets ──────────
const LOAD_CASES = [
  { key: 'hover', label: 'Hover', icon: Zap, description: 'Steady-state hover at max payload', force: 500, color: '#2563EB' },
  { key: 'maxThrust', label: 'Max Thrust', icon: Zap, description: 'Full throttle vertical ascent', force: 1200, color: '#D97706' },
  { key: 'windGust', label: 'Wind Gust', icon: Wind, description: '25 m/s lateral wind load', force: 800, color: '#DC2626' },
];

// ────────── Color Legend ──────────
const ColorLegend = () => {
  const stops = [
    { color: '#3B82F6', label: '0 MPa' },
    { color: '#10B981', label: '50' },
    { color: '#F59E0B', label: '150' },
    { color: '#EF4444', label: '300+' },
  ];
  return (
    <div style={{
      position: 'absolute', bottom: '16px', right: '16px', zIndex: 20,
      background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(8px)',
      borderRadius: '8px', padding: '10px 14px', border: '1px solid #E2E8F0',
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    }}>
      <div style={{ fontSize: '9px', fontWeight: '700', color: '#94A3B8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        Stress (MPa)
      </div>
      <div style={{ display: 'flex', height: '8px', borderRadius: '4px', overflow: 'hidden', width: '120px' }}>
        {stops.map((s, i) => (
          <div key={i} style={{ flex: 1, background: s.color }} />
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
        {stops.map((s, i) => (
          <span key={i} style={{ fontSize: '8px', color: '#64748B', fontFamily: 'monospace' }}>{s.label}</span>
        ))}
      </div>
    </div>
  );
};

// ────────── Failure Point Callout ──────────
const FailureCallout = ({ label, stress, reason, rank }: { label: string; stress: number; reason: string; rank: number }) => {
  const colors = ['#DC2626', '#D97706', '#F59E0B'];
  const bgColors = ['#FEF2F2', '#FFFBEB', '#FEF3C7'];
  const borderColors = ['#FECACA', '#FDE68A', '#FCD34D'];
  return (
    <div style={{
      padding: '12px 14px', background: bgColors[rank] || bgColors[2],
      border: `1px solid ${borderColors[rank] || borderColors[2]}`,
      borderRadius: '8px', marginBottom: '8px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
        <AlertTriangle style={{ width: '14px', height: '14px', color: colors[rank] || colors[2] }} />
        <span style={{ fontSize: '13px', fontWeight: '700', color: colors[rank] || colors[2] }}>{label}</span>
        <span style={{ marginLeft: 'auto', fontSize: '12px', fontWeight: '700', color: '#0F172A', fontFamily: 'Space Grotesk, monospace' }}>
          {stress.toFixed(1)} MPa
        </span>
      </div>
      <p style={{ fontSize: '11px', color: '#64748B', margin: 0, lineHeight: '1.5' }}>{reason}</p>
    </div>
  );
};

// ────────── Safety Factor Badge ──────────
const SafetyBadge = ({ factor }: { factor: number }) => {
  const passed = factor >= 1.5;
  const borderline = factor >= 1.0 && factor < 1.5;
  const color = passed ? '#059669' : borderline ? '#D97706' : '#DC2626';
  const bg = passed ? '#F0FDF4' : borderline ? '#FFFBEB' : '#FEF2F2';
  const border = passed ? '#BBF7D0' : borderline ? '#FDE68A' : '#FECACA';
  const label = passed ? 'PASS' : borderline ? 'BORDERLINE' : 'FAIL';
  const Icon = passed ? CheckCircle : AlertTriangle;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '14px',
      background: bg, border: `2px solid ${border}`, borderRadius: '12px',
      padding: '16px 20px', marginBottom: '16px',
    }}>
      <Icon style={{ width: '28px', height: '28px', color, flexShrink: 0 }} />
      <div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span style={{ fontSize: '28px', fontWeight: '800', color, fontFamily: 'Space Grotesk, sans-serif' }}>
            {factor.toFixed(2)}
          </span>
          <span style={{ fontSize: '11px', fontWeight: '700', color, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Safety Factor — {label}
          </span>
        </div>
        <p style={{ fontSize: '11px', color: '#64748B', margin: '2px 0 0 0' }}>
          {passed ? 'Structure exceeds minimum safety requirements' : borderline ? 'Structure meets minimum but has low margin' : 'Structure does not meet safety requirements — redesign needed'}
        </p>
      </div>
    </div>
  );
};

export default function PhysicsViewer({ data, cadModelUrl }: PhysicsViewerProps) {
  const [activeCase, setActiveCase] = useState('hover');

  const sf = data?.safety_factor ?? 0;
  const maxStress = data?.max_stress_mpa ?? 0;
  const material = data?.material_used || 'Aluminum 6061-T6';
  const yieldStrength = data?.yield_strength_mpa || 276;
  const pct = Math.min(100, (maxStress / yieldStrength) * 100);

  // Simulated failure points (derived from real data when available)
  const failurePoints = useMemo(() => {
    if (data?.failure_points) return data.failure_points;
    return [
      { label: 'Motor Mount Fillet', stress: maxStress * 1.0, reason: 'Stress concentration at the motor mount-to-arm fillet radius. Consider increasing fillet radius to 3mm.' },
      { label: 'Arm-Body Junction', stress: maxStress * 0.82, reason: 'Bending moment peak where folding arm meets the central body plate.' },
      { label: 'Battery Bay Floor', stress: maxStress * 0.55, reason: 'Distributed load from battery mass during high-G maneuvers.' },
    ];
  }, [data, maxStress]);

  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';
  const baseUrl = API.replace('/api/v1', '');

  return (
    <div style={{ display: 'flex', gap: '0', borderRadius: '12px', overflow: 'hidden', border: '1px solid #E2E8F0', background: '#fff' }}>
      {/* ── Left: 3D Stress Visualization (65%) ── */}
      <div style={{ flex: '6.5', position: 'relative', background: '#0F172A', minHeight: '480px' }}>
        {/* Stress heatmap image or placeholder */}
        {data?.heatmap_url ? (
          <img
            src={`${baseUrl}${data.heatmap_url}`}
            alt="Stress Heatmap"
            style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '20px' }}
            onError={e => { e.currentTarget.style.display = 'none'; }}
          />
        ) : (
          <div style={{
            width: '100%', height: '100%', display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', gap: '16px',
          }}>
            {/* Simulated stress visualization */}
            <div style={{ position: 'relative', width: '280px', height: '280px' }}>
              {/* Cross-section circle */}
              <svg viewBox="0 0 280 280" style={{ width: '100%', height: '100%' }}>
                <defs>
                  <radialGradient id="stressGradient" cx="35%" cy="30%">
                    <stop offset="0%" stopColor="#EF4444" />
                    <stop offset="30%" stopColor="#F59E0B" />
                    <stop offset="60%" stopColor="#10B981" />
                    <stop offset="100%" stopColor="#3B82F6" />
                  </radialGradient>
                </defs>
                {/* Main body */}
                <rect x="80" y="100" width="120" height="80" rx="8" fill="url(#stressGradient)" opacity="0.9" />
                {/* Arms */}
                <rect x="20" y="120" width="70" height="16" rx="4" fill="#F59E0B" opacity="0.8" transform="rotate(-25 55 128)" />
                <rect x="190" y="120" width="70" height="16" rx="4" fill="#F59E0B" opacity="0.8" transform="rotate(25 225 128)" />
                <rect x="20" y="150" width="70" height="16" rx="4" fill="#10B981" opacity="0.8" transform="rotate(25 55 158)" />
                <rect x="190" y="150" width="70" height="16" rx="4" fill="#10B981" opacity="0.8" transform="rotate(-25 225 158)" />
                {/* Motor mounts (high stress) */}
                <circle cx="30" cy="105" r="12" fill="#EF4444" opacity="0.9" />
                <circle cx="250" cy="105" r="12" fill="#EF4444" opacity="0.9" />
                <circle cx="30" cy="175" r="12" fill="#D97706" opacity="0.8" />
                <circle cx="250" cy="175" r="12" fill="#D97706" opacity="0.8" />
                {/* Failure markers */}
                <circle cx="30" cy="105" r="18" fill="none" stroke="#EF4444" strokeWidth="2" strokeDasharray="4 4">
                  <animate attributeName="r" values="18;22;18" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="82" cy="120" r="14" fill="none" stroke="#D97706" strokeWidth="2" strokeDasharray="4 4">
                  <animate attributeName="r" values="14;18;14" dur="2s" repeatCount="indefinite" />
                </circle>
              </svg>
              <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', textAlign: 'center' }}>
                <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                  FEA Mesh
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Load Case Toggle */}
        <div style={{
          position: 'absolute', top: '12px', left: '12px', zIndex: 20,
          display: 'flex', gap: '4px', background: 'rgba(15,23,42,0.85)', backdropFilter: 'blur(8px)',
          borderRadius: '8px', padding: '4px', border: '1px solid rgba(255,255,255,0.08)',
        }}>
          {LOAD_CASES.map(lc => (
            <button key={lc.key} onClick={() => setActiveCase(lc.key)}
              style={{
                padding: '6px 12px', border: 'none', borderRadius: '6px', cursor: 'pointer',
                fontSize: '11px', fontWeight: '600',
                background: activeCase === lc.key ? lc.color : 'transparent',
                color: activeCase === lc.key ? 'white' : 'rgba(255,255,255,0.5)',
                transition: 'all 0.15s ease', display: 'flex', alignItems: 'center', gap: '4px',
              }}>
              <lc.icon style={{ width: '12px', height: '12px' }} />
              {lc.label}
            </button>
          ))}
        </div>

        <ColorLegend />
      </div>

      {/* ── Right: Stats Panel (35%) ── */}
      <div style={{
        flex: '3.5', background: '#FAFBFC', borderLeft: '1px solid #E2E8F0',
        padding: '20px', overflowY: 'auto', maxHeight: '480px',
        display: 'flex', flexDirection: 'column', gap: '16px',
      }}>
        {/* Safety Factor Badge */}
        <SafetyBadge factor={sf} />

        {/* Key Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          {[
            { label: 'Max Stress', value: `${maxStress.toFixed(1)} MPa`, color: pct > 70 ? '#DC2626' : '#D97706' },
            { label: 'Yield Strength', value: `${yieldStrength} MPa`, color: '#059669' },
            { label: 'Material', value: material, color: '#0F172A' },
            { label: 'Load Case', value: LOAD_CASES.find(l => l.key === activeCase)?.label || 'Hover', color: '#2563EB' },
          ].map(m => (
            <div key={m.label} style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '10px 12px' }}>
              <div style={{ fontSize: '10px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '2px' }}>{m.label}</div>
              <div style={{ fontSize: '14px', fontWeight: '800', color: m.color, fontFamily: 'Space Grotesk, monospace' }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* Stress Load Bar */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', fontWeight: '600', color: '#475569' }}>Stress vs Yield</span>
            <span style={{ fontSize: '11px', color: '#94A3B8', fontFamily: 'monospace' }}>{pct.toFixed(0)}%</span>
          </div>
          <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{
              height: '100%', width: `${pct}%`, borderRadius: '3px', transition: 'width 0.8s ease',
              background: pct > 70 ? '#DC2626' : pct > 40 ? '#D97706' : '#059669',
            }} />
          </div>
        </div>

        {/* Failure Point Callouts */}
        <div>
          <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            ⚠ Critical Stress Regions
          </h4>
          {failurePoints.map((fp: any, i: number) => (
            <FailureCallout key={i} label={fp.label} stress={fp.stress} reason={fp.reason} rank={i} />
          ))}
        </div>

        {/* Recommendation */}
        {data?.recommendation && (
          <div style={{
            background: sf >= 1 ? '#F0FDF4' : '#FEF2F2',
            border: `1px solid ${sf >= 1 ? '#BBF7D0' : '#FECACA'}`,
            borderRadius: '8px', padding: '12px 14px', fontSize: '12px',
            color: sf >= 1 ? '#15803D' : '#B91C1C', lineHeight: '1.6',
          }}>
            {data.recommendation}
          </div>
        )}
      </div>
    </div>
  );
}
