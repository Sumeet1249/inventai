'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import for 3D visualization (optional)
const ThreeViewer = dynamic(() => import('@/components/cad/ThreeViewer'), { ssr: false });

interface PhysicsResult {
  simulation_type: string;
  status: string;
  primary_metric: number;
  primary_metric_name: string;
  primary_metric_unit: string;
  limit: number;
  safety_factor: number;
  critical_regions: any[];
  timestamp: string;
  explanation: string;
}

interface PhysiXScore {
  overall_score: number;
  structural_score?: number;
  thermal_score?: number;
  fluid_score?: number;
  vibration_score?: number;
  aerodynamic_score?: number;
  material_check: string;
  safety_factor: number;
  manufacturability: string;
  breakdown: Record<string, number>;
}

interface DesignIteration {
  iteration: number;
  design_params: Record<string, any>;
  physics_results: PhysicsResult[];
  status: string;
}

interface PhysiXDashboardProps {
  selfCorrectionResult: {
    status: string;
    final_iteration: number;
    final_design: Record<string, any>;
    physics_results: PhysicsResult[];
    design_history: Record<string, any>[];
    physix_score: PhysiXScore;
    convergence_time_seconds: number;
    last_diagnosis?: Record<string, any>;
    iteration_details?: DesignIteration[];
  };
}

// ============================================================================
// Mini Components
// ============================================================================

const Badge = ({ children, type = 'gray', style = {} }: any) => {
  const colors: Record<string, [string, string]> = {
    blue: ['#EFF6FF', '#1D4ED8'],
    green: ['#F0FDF4', '#15803D'],
    orange: ['#FFF7ED', '#C2410C'],
    red: ['#FEF2F2', '#B91C1C'],
    gray: ['#F1F5F9', '#475569'],
    purple: ['#FDF4FF', '#7C3AED'],
  };
  const [bg, fg] = colors[type] || colors.gray;
  return (
    <span
      style={{
        background: bg,
        color: fg,
        padding: '4px 12px',
        borderRadius: '20px',
        fontSize: '11px',
        fontWeight: '700',
        display: 'inline-block',
        ...style,
      }}
    >
      {children}
    </span>
  );
};

const SectionHeader = ({ icon, title, badge, badgeType }: any) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
    <span style={{ fontSize: '22px' }}>{icon}</span>
    <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', margin: 0 }}>{title}</h2>
    {badge && <Badge type={badgeType}>{badge}</Badge>}
  </div>
);

const Card = ({ children, style = {} }: any) => (
  <div
    style={{
      background: '#fff',
      border: '1px solid #E2E8F0',
      borderRadius: '12px',
      padding: '24px',
      ...style,
    }}
  >
    {children}
  </div>
);

const StatBox = ({ label, value, unit = '', color = '#0F172A', subtext = '' }: any) => (
  <div style={{ textAlign: 'center' }}>
    <div
      style={{
        fontSize: '32px',
        fontWeight: '800',
        color,
        fontFamily: 'Space Grotesk, sans-serif',
        letterSpacing: '-0.5px',
      }}
    >
      {value}
      {unit && <span style={{ fontSize: '18px', fontWeight: '600' }}> {unit}</span>}
    </div>
    <div style={{ fontSize: '12px', fontWeight: '600', color: '#0F172A', marginTop: '4px' }}>{label}</div>
    {subtext && (
      <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>{subtext}</div>
    )}
  </div>
);

// ============================================================================
// Main Component
// ============================================================================

export const PhysiXDashboard: React.FC<PhysiXDashboardProps> = ({ selfCorrectionResult }) => {
  const {
    status,
    final_iteration,
    final_design,
    physics_results,
    design_history,
    physix_score,
    convergence_time_seconds,
    last_diagnosis,
  } = selfCorrectionResult;

  const [expandedPhysics, setExpandedPhysics] = useState<string | null>(null);

  // Determine status colors
  const statusColors: Record<string, [string, string, string]> = {
    SUCCESS: ['#F0FDF4', '#15803D', '✅'],
    FAILED_CONVERGENCE: ['#FEF2F2', '#B91C1C', '⚠️'],
    ERROR: ['#FEF2F2', '#B91C1C', '❌'],
  };

  const [bgColor, textColor, statusIcon] = statusColors[status] || statusColors.ERROR;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* SECTION 1: Self-Correction Overview */}
      {/* ═══════════════════════════════════════════════════════════════ */}

      <Card style={{ background: bgColor, border: `2px solid ${textColor}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ fontSize: '40px' }}>{statusIcon}</span>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: textColor, margin: '0 0 4px 0' }}>
              {status === 'SUCCESS' ? '✅ Physics Checks Passed!' : 'Physics Validation'}
            </h3>
            <p style={{ fontSize: '14px', color: textColor, margin: 0, opacity: 0.9 }}>
              {status === 'SUCCESS'
                ? `Design converged to optimal solution in ${final_iteration} iteration${final_iteration !== 1 ? 's' : ''}`
                : 'Design did not reach convergence criteria'}
            </p>
          </div>
        </div>
      </Card>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* SECTION 2: Key Metrics Summary */}
      {/* ═══════════════════════════════════════════════════════════════ */}

      <Card>
        <SectionHeader icon="📊" title="PhysiX Score & Metrics" badge="Real-time" badgeType="blue" />

        {/* Multi-Physics Score Breakdown */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {/* Overall Score */}
          <div
            style={{
              background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
              borderRadius: '12px',
              padding: '20px',
              textAlign: 'center',
              color: '#fff',
            }}
          >
            <div style={{ fontSize: '36px', fontWeight: '800' }}>
              {Math.round(physix_score.overall_score)}
            </div>
            <div style={{ fontSize: '12px', fontWeight: '600', marginTop: '4px', opacity: 0.9 }}>Overall Score</div>
          </div>

          {/* Structural */}
          {physix_score.structural_score !== undefined && (
            <div
              style={{
                background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center',
                color: '#fff',
              }}
            >
              <div style={{ fontSize: '36px', fontWeight: '800' }}>
                {Math.round(physix_score.structural_score)}
              </div>
              <div style={{ fontSize: '12px', fontWeight: '600', marginTop: '4px', opacity: 0.9 }}>Structural</div>
            </div>
          )}

          {/* Thermal */}
          {physix_score.thermal_score !== undefined && (
            <div
              style={{
                background: 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center',
                color: '#fff',
              }}
            >
              <div style={{ fontSize: '36px', fontWeight: '800' }}>
                {Math.round(physix_score.thermal_score)}
              </div>
              <div style={{ fontSize: '12px', fontWeight: '600', marginTop: '4px', opacity: 0.9 }}>Thermal</div>
            </div>
          )}

          {/* Fluid */}
          {physix_score.fluid_score !== undefined && (
            <div
              style={{
                background: 'linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center',
                color: '#fff',
              }}
            >
              <div style={{ fontSize: '36px', fontWeight: '800' }}>
                {Math.round(physix_score.fluid_score)}
              </div>
              <div style={{ fontSize: '12px', fontWeight: '600', marginTop: '4px', opacity: 0.9 }}>Fluid</div>
            </div>
          )}
        </div>

        {/* Key Stats Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <StatBox label="Safety Factor" value={physix_score.safety_factor.toFixed(2)} color="#10B981" />
          <StatBox label="Manufacturability" value={physix_score.manufacturability} color="#3B82F6" />
          <StatBox label="Material Check" value={physix_score.material_check} color="#F59E0B" />
          <StatBox
            label="Time to Converge"
            value={convergence_time_seconds.toFixed(2)}
            unit="s"
            color="#8B5CF6"
          />
        </div>
      </Card>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* SECTION 3: Self-Correcting Loop Iterations */}
      {/* ═══════════════════════════════════════════════════════════════ */}

      <Card>
        <SectionHeader
          icon="🔄"
          title="Self-Correcting Design Loop"
          badge={`${final_iteration} Iteration${final_iteration !== 1 ? 's' : ''}`}
          badgeType="purple"
        />

        <div style={{ position: 'relative', paddingLeft: '30px' }}>
          {design_history.map((design: any, idx: number) => {
            const isLast = idx === design_history.length - 1;
            const isPassed = isLast && status === 'SUCCESS';

            return (
              <div key={idx} style={{ marginBottom: '24px', position: 'relative' }}>
                {/* Timeline dot */}
                <div
                  style={{
                    position: 'absolute',
                    left: '-30px',
                    top: '4px',
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: isPassed ? '#10B981' : idx < design_history.length - 1 ? '#94A3B8' : '#F59E0B',
                    border: '3px solid #fff',
                    boxShadow: '0 0 0 2px #E2E8F0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px',
                    fontWeight: '700',
                    color: '#fff',
                  }}
                >
                  {isPassed ? '✓' : idx < design_history.length - 1 ? '↻' : '→'}
                </div>

                {/* Iteration details */}
                <div
                  style={{
                    background: '#F8FAFC',
                    border: `2px solid ${isPassed ? '#10B981' : '#E2E8F0'}`,
                    borderRadius: '10px',
                    padding: '14px 16px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '8px',
                    }}
                  >
                    <span style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A' }}>
                      Iteration {idx + 1}
                    </span>
                    <Badge type={isPassed ? 'green' : idx < design_history.length - 1 ? 'orange' : 'blue'}>
                      {isPassed ? '✅ PASS' : idx < design_history.length - 1 ? '⚠️ Optimizing' : '→ Checking'}
                    </Badge>
                  </div>

                  {/* Design parameters */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '12px' }}>
                    <div>
                      <span style={{ color: '#94A3B8' }}>Thickness:</span>{' '}
                      <span style={{ fontWeight: '600', color: '#0F172A' }}>{design.thickness_mm}mm</span>
                    </div>
                    <div>
                      <span style={{ color: '#94A3B8' }}>Material:</span>{' '}
                      <span style={{ fontWeight: '600', color: '#0F172A' }}>{design.material}</span>
                    </div>
                    {design.fillet_radius_mm > 0 && (
                      <div>
                        <span style={{ color: '#94A3B8' }}>Fillet:</span>{' '}
                        <span style={{ fontWeight: '600', color: '#0F172A' }}>{design.fillet_radius_mm}mm</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* SECTION 4: Physics Results per Simulation */}
      {/* ═══════════════════════════════════════════════════════════════ */}

      <Card>
        <SectionHeader
          icon="⚙️"
          title="Physics Simulation Results"
          badge={`${physics_results.length} Simulations`}
          badgeType="blue"
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {physics_results.map((result: PhysicsResult, idx: number) => (
            <div
              key={idx}
              style={{
                border: '1px solid #E2E8F0',
                borderRadius: '10px',
                overflow: 'hidden',
                background: '#F8FAFC',
              }}
            >
              {/* Header (clickable) */}
              <button
                onClick={() =>
                  setExpandedPhysics(expandedPhysics === result.simulation_type ? null : result.simulation_type)
                }
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  border: 'none',
                  background: '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', textAlign: 'left' }}>
                  <span
                    style={{
                      fontSize: '12px',
                      fontWeight: '700',
                      textTransform: 'uppercase',
                      color:
                        result.status === 'PASS'
                          ? '#10B981'
                          : result.status === 'WARNING'
                            ? '#F59E0B'
                            : '#EF4444',
                    }}
                  >
                    {result.status}
                  </span>
                  <span style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A' }}>
                    {result.simulation_type.charAt(0).toUpperCase() + result.simulation_type.slice(1)}
                  </span>
                </div>
                <span style={{ fontSize: '18px' }}>
                  {expandedPhysics === result.simulation_type ? '▼' : '▶'}
                </span>
              </button>

              {/* Expanded details */}
              {expandedPhysics === result.simulation_type && (
                <div style={{ padding: '16px', background: '#fff', borderTop: '1px solid #E2E8F0' }}>
                  {/* Primary Metric */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(3, 1fr)',
                      gap: '16px',
                      marginBottom: '16px',
                    }}
                  >
                    <div
                      style={{
                        background: '#F1F5F9',
                        borderRadius: '8px',
                        padding: '12px',
                        textAlign: 'center',
                      }}
                    >
                      <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600' }}>
                        {result.primary_metric_name}
                      </div>
                      <div style={{ fontSize: '20px', fontWeight: '800', color: '#0F172A', marginTop: '4px' }}>
                        {result.primary_metric.toFixed(1)}
                      </div>
                      <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '2px' }}>
                        {result.primary_metric_unit}
                      </div>
                    </div>

                    <div
                      style={{
                        background: '#F1F5F9',
                        borderRadius: '8px',
                        padding: '12px',
                        textAlign: 'center',
                      }}
                    >
                      <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600' }}>Limit</div>
                      <div style={{ fontSize: '20px', fontWeight: '800', color: '#0F172A', marginTop: '4px' }}>
                        {result.limit.toFixed(1)}
                      </div>
                      <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '2px' }}>
                        {result.primary_metric_unit}
                      </div>
                    </div>

                    <div
                      style={{
                        background: '#F1F5F9',
                        borderRadius: '8px',
                        padding: '12px',
                        textAlign: 'center',
                      }}
                    >
                      <div style={{ fontSize: '11px', color: '#64748B', fontWeight: '600' }}>Safety Factor</div>
                      <div
                        style={{
                          fontSize: '20px',
                          fontWeight: '800',
                          color: result.safety_factor >= 1.5 ? '#10B981' : '#F59E0B',
                          marginTop: '4px',
                        }}
                      >
                        {result.safety_factor.toFixed(2)}
                      </div>
                      <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '2px' }}>×</div>
                    </div>
                  </div>

                  {/* Explanation */}
                  <div
                    style={{
                      background: '#F8FAFC',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                      padding: '12px',
                      fontSize: '13px',
                      color: '#475569',
                      lineHeight: '1.5',
                    }}
                  >
                    {result.explanation}
                  </div>

                  {/* Critical Regions */}
                  {result.critical_regions.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <div style={{ fontSize: '12px', fontWeight: '700', color: '#0F172A', marginBottom: '8px' }}>
                        Critical Regions:
                      </div>
                      {result.critical_regions.map((region: any, ridx: number) => (
                        <div
                          key={ridx}
                          style={{
                            background: '#FEF3C7',
                            border: '1px solid #FCD34D',
                            borderRadius: '6px',
                            padding: '8px 10px',
                            fontSize: '12px',
                            color: '#78350F',
                            marginBottom: '6px',
                          }}
                        >
                          <strong>{region.name}</strong>: {JSON.stringify(region).slice(0, 60)}...
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* SECTION 5: Failure Diagnosis (if applicable) */}
      {/* ═══════════════════════════════════════════════════════════════ */}

      {last_diagnosis && last_diagnosis.failed && (
        <Card style={{ background: '#FEF2F2', border: '2px solid #FCA5A5' }}>
          <SectionHeader
            icon="🔍"
            title="Failure Diagnosis & Prescriptions"
            badge="Final Iteration"
            badgeType="red"
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            {/* Root Cause */}
            <div style={{ background: '#fff', borderRadius: '8px', padding: '12px', border: '1px solid #FECACA' }}>
              <div style={{ fontSize: '11px', fontWeight: '700', color: '#991B1B', textTransform: 'uppercase' }}>
                Root Cause
              </div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#7F1D1D', marginTop: '4px' }}>
                {last_diagnosis.root_cause}
              </div>
            </div>

            {/* Severity */}
            <div style={{ background: '#fff', borderRadius: '8px', padding: '12px', border: '1px solid #FECACA' }}>
              <div style={{ fontSize: '11px', fontWeight: '700', color: '#991B1B', textTransform: 'uppercase' }}>
                Severity
              </div>
              <Badge type={last_diagnosis.severity === 'CRITICAL' ? 'red' : 'orange'} style={{ marginTop: '4px' }}>
                {last_diagnosis.severity}
              </Badge>
            </div>
          </div>

          {/* Recommended Fixes */}
          <div style={{ background: '#fff', borderRadius: '8px', padding: '12px', border: '1px solid #FECACA' }}>
            <div style={{ fontSize: '11px', fontWeight: '700', color: '#991B1B', textTransform: 'uppercase', marginBottom: '8px' }}>
              Recommended Fixes
            </div>
            <ul
              style={{
                margin: 0,
                paddingLeft: '18px',
                fontSize: '12px',
                color: '#7F1D1D',
                lineHeight: '1.6',
              }}
            >
              {last_diagnosis.recommended_fixes.map((fix: string, idx: number) => (
                <li key={idx}>{fix}</li>
              ))}
            </ul>
          </div>
        </Card>
      )}

      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* SECTION 6: Final Design Parameters */}
      {/* ═══════════════════════════════════════════════════════════════ */}

      <Card>
        <SectionHeader icon="🏗️" title="Final Optimized Design" badge="Ready" badgeType="green" />

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px' }}>
          {Object.entries(final_design).map(([key, value]: [string, any]) => (
            <div
              key={key}
              style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '12px',
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: '600', color: '#94A3B8', textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}
              </div>
              <div
                style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#0F172A',
                  marginTop: '4px',
                  wordBreak: 'break-word',
                }}
              >
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default PhysiXDashboard;
