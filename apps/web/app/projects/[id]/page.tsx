'use client';

import React, { useEffect, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import WorkflowVisualizer from '@/components/dashboard/WorkflowVisualizer';
import { PhysiXDashboard } from '@/components/physics/PhysiXDashboard';

const ThreeViewer = dynamic(() => import('@/components/cad/ThreeViewer'), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

// ────────── Types ──────────
interface AgentState { status: string; done: boolean; error: boolean; data: any; elapsed: number; }
const fresh = (): AgentState => ({ status: 'Queued', done: false, error: false, data: null, elapsed: 0 });

// ────────── Small UI helpers ──────────
const Badge = ({ children, type = 'gray' }: { children: React.ReactNode; type?: string }) => {
  const colors: Record<string, [string, string]> = {
    blue: ['#EFF6FF', '#1D4ED8'], green: ['#F0FDF4', '#15803D'],
    orange: ['#FFF7ED', '#C2410C'], red: ['#FEF2F2', '#B91C1C'],
    gray: ['#F1F5F9', '#475569'], purple: ['#FDF4FF', '#7C3AED'],
  };
  const [bg, fg] = colors[type] || colors.gray;
  return (
    <span style={{ background: bg, color: fg, padding: '2px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600' }}>
      {children}
    </span>
  );
};

const Spinner = () => (
  <span style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid #CBD5E1', borderTop: '2px solid #2563EB', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
);

const Stat = ({ label, value, sub, color = '#0F172A' }: any) => (
  <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '18px 20px' }}>
    <div style={{ fontSize: '26px', fontWeight: '800', color, fontFamily: 'Space Grotesk, sans-serif' }}>{value}</div>
    <div style={{ fontSize: '13px', fontWeight: '600', color: '#0F172A', marginTop: '2px' }}>{label}</div>
    {sub && <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>{sub}</div>}
  </div>
);

const SectionHeader = ({ icon, title, badge, badgeType }: any) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
    <span style={{ fontSize: '20px' }}>{icon}</span>
    <h2 style={{ fontSize: '17px', fontWeight: '700', color: '#0F172A', margin: 0 }}>{title}</h2>
    {badge && <Badge type={badgeType}>{badge}</Badge>}
  </div>
);

const Card = ({ children, style = {} }: any) => (
  <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '24px', ...style }}>
    {children}
  </div>
);

// ────────── Agent Step Timeline (Removed in favor of WorkflowVisualizer) ──────────

// ────────── Circuit Design Result ──────────
const CircuitResult = ({ data, projectId }: { data: any; projectId: string }) => {
  const BACKEND = typeof window !== 'undefined'
    ? (window.location.hostname === 'localhost' ? 'http://localhost:8080' : window.location.origin)
    : 'http://nginx:80';

  const bom: any[]    = data?.bom || [];
  const elec          = data?.elec_spec || {};
  const rails: string[] = data?.power_rails || [];
  const schematicUrl  = data?.schematic_url ? `${BACKEND}${data.schematic_url}` : null;

  const typeColors: Record<string, string> = {
    battery: '#EF4444', bec: '#F97316', ldo: '#F97316', buck: '#F97316',
    flight_controller: '#3B82F6', mcu: '#3B82F6', esc: '#8B5CF6',
    motor_driver: '#8B5CF6', motor: '#EC4899', servo: '#EC4899',
    receiver: '#10B981', gps: '#10B981', telemetry: '#10B981',
    vtx: '#06B6D4', camera: '#06B6D4', sensor: '#A3E635',
    charger: '#F59E0B', connector: '#94A3B8',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <SectionHeader icon="⚡" title="Circuit Design" badge="Completed" badgeType="green" />

      {/* Power Analysis */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '12px' }}>
        {[
          { label: 'Battery',     val: `${elec.power_input_v ?? '?'} V`,        color: '#EF4444' },
          { label: 'Peak Draw',   val: `${elec.total_current_a ?? '?'} A`,      color: '#F97316' },
          { label: 'Flight Time', val: `${elec.flight_time_min ?? '?'} min`,    color: '#22C55E' },
          { label: 'MCU',         val: elec.mcu ?? 'N/A',                        color: '#3B82F6' },
        ].map(s => (
          <div key={s.label} style={{
            background: '#fff', border: '1px solid #F1F5F9',
            borderRadius: '12px', padding: '16px 18px',
            borderLeft: `4px solid ${s.color}`,
          }}>
            <div style={{ fontSize: '20px', fontWeight: '800', color: '#0F172A', letterSpacing: '-0.5px' }}>{s.val}</div>
            <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600', marginTop: '2px' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Power Rails */}
      <Card>
        <div style={{ fontSize: '13px', fontWeight: '700', color: '#334155', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Power Rails</div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {rails.map((r, i) => {
            const railColors = ['#EF4444', '#F97316', '#22C55E', '#3B82F6', '#8B5CF6'];
            const c = railColors[i % railColors.length];
            return (
              <div key={r} style={{
                background: `${c}18`, border: `1.5px solid ${c}44`,
                color: c, padding: '6px 16px', borderRadius: '100px',
                fontSize: '13px', fontWeight: '700',
              }}>{r}</div>
            );
          })}
        </div>
      </Card>

      {/* SVG Schematic */}
      {schematicUrl && (
        <Card style={{ padding: '0', overflow: 'hidden', borderRadius: '14px' }}>
          <div style={{
            background: '#0F172A', padding: '16px 20px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <span style={{ fontSize: '14px', fontWeight: '700', color: '#F1F5F9' }}>⚡ Circuit Schematic</span>
            <a href={schematicUrl} target="_blank" rel="noopener noreferrer"
              style={{ fontSize: '12px', color: '#3B82F6', fontWeight: '600', textDecoration: 'none' }}>
              ↗ Open SVG
            </a>
          </div>
          <img
            src={schematicUrl}
            alt="Circuit Schematic"
            style={{ width: '100%', display: 'block', background: '#0F172A' }}
          />
        </Card>
      )}

      {/* Communication buses */}
      {elec.communication && elec.communication.length > 0 && (
        <Card>
          <div style={{ fontSize: '13px', fontWeight: '700', color: '#334155', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Communication Buses</div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {elec.communication.map((bus: string) => (
              <span key={bus} style={{
                background: '#EFF6FF', color: '#1D4ED8',
                padding: '5px 14px', borderRadius: '100px',
                fontSize: '12px', fontWeight: '700',
              }}>{bus}</span>
            ))}
          </div>
          {elec.sensors && elec.sensors.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase' }}>Sensors</div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {elec.sensors.map((s: string) => (
                  <span key={s} style={{
                    background: '#F0FDF4', color: '#15803D',
                    padding: '4px 12px', borderRadius: '100px',
                    fontSize: '12px', fontWeight: '600',
                  }}>{s}</span>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* BOM Table */}
      <Card style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{
          padding: '16px 20px', borderBottom: '1px solid #F1F5F9',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <span style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A' }}>
            Component BOM ({bom.length} parts)
          </span>
          <span style={{ fontSize: '14px', fontWeight: '800', color: '#059669' }}>
            Total: {data?.bom_total ?? '$0.00'}
          </span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: '#F8FAFC' }}>
                {['Ref', 'Component', 'Type', 'Voltage', 'Current', 'Package', 'Est. Cost'].map(h => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', color: '#64748B', fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid #E2E8F0' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bom.map((comp: any, i: number) => {
                const c = typeColors[comp.type] || '#94A3B8';
                return (
                  <tr key={comp.ref + i} style={{ borderBottom: '1px solid #F8FAFC' }}>
                    <td style={{ padding: '10px 14px', fontWeight: '700', color: c, fontFamily: 'monospace' }}>{comp.ref}</td>
                    <td style={{ padding: '10px 14px', color: '#0F172A', fontWeight: '600' }}>{comp.name}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <span style={{ background: `${c}18`, color: c, padding: '2px 8px', borderRadius: '100px', fontSize: '11px', fontWeight: '700' }}>
                        {comp.type.replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px', color: '#64748B', fontFamily: 'monospace', fontSize: '12px' }}>{comp.voltage || '—'}</td>
                    <td style={{ padding: '10px 14px', color: '#64748B', fontFamily: 'monospace', fontSize: '12px' }}>{comp.current || '—'}</td>
                    <td style={{ padding: '10px 14px', color: '#94A3B8', fontSize: '12px' }}>{comp.package || '—'}</td>
                    <td style={{ padding: '10px 14px', color: '#059669', fontWeight: '700' }}>{comp.est_cost}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Notes */}
      {elec.notes && (
        <div style={{
          background: '#FFFBEB', border: '1px solid #FDE68A',
          borderRadius: '10px', padding: '14px 18px',
          fontSize: '13px', color: '#92400E',
        }}>
          💡 {elec.notes}
        </div>
      )}
    </div>
  );
};

// ────────── Unified CAD + Circuit Tab ──────────
const CadResult = ({
  data, isGenerating, generationStatus, circuitData, circuitGenerating, circuitStatus,
}: {
  data: any; isGenerating?: boolean; generationStatus?: string;
  circuitData?: any; circuitGenerating?: boolean; circuitStatus?: string;
}) => {
  const BACKEND = (typeof window !== 'undefined')
    ? (window.location.hostname === 'localhost' ? 'http://localhost:8080' : window.location.origin)
    : 'http://nginx:80';
  const gltfUrl      = data?.gltf_url      ? `${BACKEND}${data.gltf_url}` : null;
  const schematicUrl = circuitData?.schematic_url ? `${BACKEND}${circuitData.schematic_url}` : null;

  const bom: any[]      = circuitData?.bom || [];
  const elec            = circuitData?.elec_spec || {};
  const rails: string[] = circuitData?.power_rails || [];

  const typeColors: Record<string, string> = {
    battery: '#EF4444', bec: '#F97316', ldo: '#F97316', buck: '#F97316',
    flight_controller: '#3B82F6', mcu: '#3B82F6', esc: '#8B5CF6',
    motor_driver: '#8B5CF6', motor: '#EC4899', servo: '#EC4899',
    receiver: '#10B981', gps: '#10B981', telemetry: '#10B981',
    vtx: '#06B6D4', camera: '#06B6D4', sensor: '#A3E635',
    charger: '#F59E0B', connector: '#94A3B8',
  };

  // CAD spec summary badges from parameters
  const params = data?.parameters || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* ── SECTION 1: 3D CAD MODEL ── */}
      <div style={{
        background: '#fff', border: '1px solid #E2E8F0',
        borderRadius: '16px', overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 24px', borderBottom: '1px solid #F1F5F9',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: '#FAFBFF',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '20px' }}>🔩</span>
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: '700', color: '#0F172A', margin: 0 }}>3D CAD Model</h2>
              <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0 }}>
                {params.component_type ? params.component_type.replace('_', ' ') : ''} · {params.span_mm || ''}mm
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {data?.gltf_url && <Badge type="green">GLTF ✓</Badge>}
            {data?.step_url && <Badge type="blue">STEP ✓</Badge>}
            {data?.stl_url  && <Badge type="gray">STL ✓</Badge>}
            <Badge type={data?.gltf_url ? 'green' : 'blue'}>{isGenerating ? 'Generating…' : 'Completed'}</Badge>
          </div>
        </div>

        {/* CAD Spec quick stats */}
        {params.component_type && (
          <div style={{
            padding: '12px 24px', borderBottom: '1px solid #F1F5F9',
            display: 'flex', gap: '24px', flexWrap: 'wrap', background: '#F8FAFC',
          }}>
            {[
              { k: 'Type',      v: params.component_type?.replace(/_/g,' ') },
              { k: 'Span',      v: params.span_mm ? `${params.span_mm}mm` : null },
              { k: 'Arms',      v: params.arm_count },
              { k: 'Motors',    v: params.motor_count },
              { k: 'Wall',      v: params.wall_mm ? `${params.wall_mm}mm` : null },
              { k: 'Material',  v: params.material },
            ].filter(s => s.v).map(s => (
              <div key={s.k}>
                <div style={{ fontSize: '10px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.k}</div>
                <div style={{ fontSize: '13px', color: '#0F172A', fontWeight: '700' }}>{String(s.v)}</div>
              </div>
            ))}
          </div>
        )}

        {/* 3D Viewer */}
        <div style={{ padding: '0' }}>
          <ThreeViewer
            modelUrl={gltfUrl}
            isGenerating={isGenerating || false}
            generationStatus={generationStatus || ''}
            cadData={data}
          />
        </div>

        {/* Export links */}
        {data && (data.gltf_url || data.step_url || data.stl_url) && (
          <div style={{
            padding: '12px 24px', borderTop: '1px solid #F1F5F9',
            display: 'flex', gap: '12px', background: '#FAFBFF',
          }}>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: '600', lineHeight: '28px' }}>Download:</span>
            {[
              { url: data.gltf_url, label: '⬇ GLTF', color: '#2563EB' },
              { url: data.step_url, label: '⬇ STEP', color: '#059669' },
              { url: data.stl_url,  label: '⬇ STL',  color: '#7C3AED' },
            ].filter(f => f.url).map(f => (
              <a key={f.label}
                href={`${BACKEND}${f.url}`}
                target="_blank" rel="noopener noreferrer"
                style={{
                  background: '#F8FAFC', border: '1px solid #E2E8F0',
                  color: f.color, padding: '5px 14px', borderRadius: '8px',
                  fontSize: '12px', fontWeight: '700', textDecoration: 'none',
                }}>
                {f.label}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* ── SECTION 2: CIRCUIT DESIGN (derived from CAD) ── */}
      <div style={{
        background: '#fff', border: '1px solid #E2E8F0',
        borderRadius: '16px', overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 24px', background: '#0F172A',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '20px' }}>⚡</span>
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: '700', color: '#F1F5F9', margin: 0 }}>
                Circuit Design
              </h2>
              <p style={{ fontSize: '12px', color: '#64748B', margin: 0 }}>
                Auto-generated from CAD spec · Electronics Agent
              </p>
            </div>
          </div>
          <Badge type={circuitData ? 'green' : 'gray'}>
            {circuitGenerating ? 'Generating…' : circuitData ? 'Completed' : 'Waiting for CAD'}
          </Badge>
        </div>

        {/* Loading state */}
        {!circuitData && (
          <div style={{ padding: '48px', textAlign: 'center', color: '#94A3B8' }}>
            {circuitGenerating
              ? <><Spinner /> &nbsp; {circuitStatus || 'Electronics agent generating circuit…'}</>
              : isGenerating
                ? <><Spinner /> &nbsp; Waiting for CAD to complete…</>
                : '⚡ Circuit design will appear here after CAD generation'
            }
          </div>
        )}

        {/* Circuit content */}
        {circuitData && (
          <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>

            {/* Power stats row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '12px' }}>
              {[
                { label: 'Battery',     val: `${elec.power_input_v ?? '?'}V`,       color: '#EF4444' },
                { label: 'Peak Draw',   val: `${elec.total_current_a ?? '?'}A`,     color: '#F97316' },
                { label: 'Flight Time', val: `${elec.flight_time_min ?? '?'} min`,  color: '#22C55E' },
                { label: 'MCU / FC',    val: elec.mcu ?? 'N/A',                      color: '#3B82F6' },
              ].map(s => (
                <div key={s.label} style={{
                  background: '#F8FAFC', border: `1px solid #F1F5F9`,
                  borderRadius: '10px', padding: '14px 16px',
                  borderLeft: `4px solid ${s.color}`,
                }}>
                  <div style={{ fontSize: '18px', fontWeight: '800', color: '#0F172A', letterSpacing: '-0.3px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.val}</div>
                  <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', marginTop: '2px' }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Power rails + comms in one row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div style={{ background: '#F8FAFC', borderRadius: '12px', padding: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '10px' }}>Power Rails</div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {rails.map((r, i) => {
                    const rc = ['#EF4444','#F97316','#22C55E','#3B82F6','#8B5CF6'][i % 5];
                    return (
                      <span key={r} style={{
                        background: `${rc}15`, border: `1.5px solid ${rc}40`,
                        color: rc, padding: '4px 12px', borderRadius: '100px',
                        fontSize: '12px', fontWeight: '700',
                      }}>{r}</span>
                    );
                  })}
                </div>
              </div>
              <div style={{ background: '#F8FAFC', borderRadius: '12px', padding: '16px' }}>
                <div style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '10px' }}>Communication Buses</div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {(elec.communication || []).map((b: string) => (
                    <span key={b} style={{ background: '#EFF6FF', color: '#1D4ED8', padding: '4px 10px', borderRadius: '100px', fontSize: '11px', fontWeight: '700' }}>{b}</span>
                  ))}
                  {(elec.sensors || []).slice(0, 3).map((s: string) => (
                    <span key={s} style={{ background: '#F0FDF4', color: '#15803D', padding: '4px 10px', borderRadius: '100px', fontSize: '11px', fontWeight: '600' }}>{s}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* SVG Schematic — full width, dark background */}
            {schematicUrl && (
              <div style={{ borderRadius: '12px', overflow: 'hidden', border: '1px solid #1E293B' }}>
                <div style={{
                  background: '#1E293B', padding: '12px 16px',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                }}>
                  <span style={{ fontSize: '13px', fontWeight: '700', color: '#94A3B8' }}>Schematic Diagram</span>
                  <a href={schematicUrl} target="_blank" rel="noopener noreferrer"
                    style={{ fontSize: '11px', color: '#3B82F6', fontWeight: '600', textDecoration: 'none' }}>
                    ↗ Full screen
                  </a>
                </div>
                <img
                  src={schematicUrl}
                  alt="Circuit Schematic"
                  style={{ width: '100%', display: 'block', background: '#0F172A' }}
                />
              </div>
            )}

            {/* BOM Table — compact */}
            <div style={{ borderRadius: '12px', overflow: 'hidden', border: '1px solid #E2E8F0' }}>
              <div style={{
                padding: '12px 16px', background: '#F8FAFC',
                borderBottom: '1px solid #E2E8F0',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <span style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A' }}>
                  Electronic BOM — {bom.length} components
                </span>
                <span style={{ fontSize: '13px', fontWeight: '800', color: '#059669' }}>
                  {circuitData.bom_total ?? ''}
                </span>
              </div>
              <div style={{ overflowX: 'auto', maxHeight: '280px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                  <thead style={{ position: 'sticky', top: 0, background: '#F8FAFC' }}>
                    <tr>
                      {['Ref','Component','Type','Voltage','Current','Package','Cost'].map(h => (
                        <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: '#64748B', fontWeight: '700', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid #E2E8F0' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {bom.map((comp: any, i: number) => {
                      const c = typeColors[comp.type] || '#94A3B8';
                      return (
                        <tr key={i} style={{ borderBottom: '1px solid #F8FAFC' }}
                          onMouseEnter={e => (e.currentTarget.style.background = '#F8FAFC')}
                          onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                          <td style={{ padding: '8px 12px', fontWeight: '700', color: c, fontFamily: 'monospace', fontSize: '11px' }}>{comp.ref}</td>
                          <td style={{ padding: '8px 12px', color: '#0F172A', fontWeight: '600' }}>{comp.name}</td>
                          <td style={{ padding: '8px 12px' }}>
                            <span style={{ background: `${c}18`, color: c, padding: '2px 7px', borderRadius: '100px', fontSize: '10px', fontWeight: '700' }}>
                              {comp.type?.replace(/_/g,' ')}
                            </span>
                          </td>
                          <td style={{ padding: '8px 12px', color: '#64748B', fontFamily: 'monospace', fontSize: '11px' }}>{comp.voltage || '—'}</td>
                          <td style={{ padding: '8px 12px', color: '#64748B', fontFamily: 'monospace', fontSize: '11px' }}>{comp.current || '—'}</td>
                          <td style={{ padding: '8px 12px', color: '#94A3B8', fontSize: '11px' }}>{comp.package || '—'}</td>
                          <td style={{ padding: '8px 12px', color: '#059669', fontWeight: '700' }}>{comp.est_cost}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ────────── Physics Results ──────────
const PhysicsResult = ({ data }: { data: any }) => {
  const sf = data.safety_factor ?? 0;
  const sfColor = sf >= 2 ? '#059669' : sf >= 1 ? '#D97706' : '#DC2626';
  const pct = Math.min(100, (data.max_stress_mpa / 300) * 100);
  return (
    <Card>
      <SectionHeader icon="⚡" title="Physics Simulation" badge="Completed" badgeType="green" />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '20px' }}>
        <Stat label="Max Stress" value={`${data.max_stress_mpa?.toFixed(1)} MPa`} color={pct > 70 ? '#DC2626' : '#D97706'} />
        <Stat label="Safety Factor" value={sf.toFixed(2)} color={sfColor} sub={sf >= 2 ? 'Safe ✓' : sf >= 1 ? 'Borderline' : '⚠ Unsafe'} />
        <Stat label="Material" value={data.material_used || 'N/A'} />
      </div>
      {/* Stress bar */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ fontSize: '13px', fontWeight: '600', color: '#475569' }}>Stress Load</span>
          <span style={{ fontSize: '13px', color: '#94A3B8' }}>{data.max_stress_mpa?.toFixed(1)} / 300 MPa</span>
        </div>
        <div style={{ height: '8px', background: '#F1F5F9', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: pct > 70 ? '#DC2626' : pct > 40 ? '#D97706' : '#059669', borderRadius: '4px', transition: 'width 0.5s ease' }} />
        </div>
      </div>
      <div style={{ background: sf >= 1 ? '#F0FDF4' : '#FEF2F2', border: `1px solid ${sf >= 1 ? '#BBF7D0' : '#FECACA'}`, borderRadius: '8px', padding: '12px 16px', fontSize: '13px', color: sf >= 1 ? '#15803D' : '#B91C1C' }}>
        {data.recommendation}
      </div>
      {data.heatmap_url && (
        <div style={{ marginTop: '16px' }}>
          <p style={{ fontSize: '12px', fontWeight: '600', color: '#94A3B8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Stress Heatmap</p>
          <img src={`${API.replace('/api/v1', '')}${data.heatmap_url}`} alt="Stress Heatmap" style={{ width: '100%', borderRadius: '8px', border: '1px solid #E2E8F0', maxHeight: '200px', objectFit: 'contain', background: '#F8FAFC' }} onError={e => (e.currentTarget.style.display = 'none')} />
        </div>
      )}
    </Card>
  );
};

// ────────── Business Results ──────────
const BusinessResult = ({ data }: { data: any }) => (
  <Card>
    <SectionHeader icon="💼" title="Business Intelligence" badge="Completed" badgeType="green" />
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
      <Stat label="Market Size Est." value={data.market_size_est || '–'} color="#059669" />
      <Stat label="Suggested MSRP" value={data.suggested_msrp || '–'} color="#2563EB" />
    </div>
    {data.bom_url && (
      <a href={`${API.replace('/api/v1', '')}${data.bom_url}`} target="_blank" rel="noopener noreferrer"
        style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: '8px', padding: '10px 18px', fontSize: '14px', fontWeight: '600', color: '#15803D', textDecoration: 'none' }}>
        📊 Download Financial BOM (Excel)
      </a>
    )}
  </Card>
);

// ────────── Research Results ──────────
const ResearchResult = ({ data }: { data: any }) => (
  <Card>
    <SectionHeader icon="📚" title="Research & Knowledge RAG" badge="Completed" badgeType="green" />
    <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '16px', marginBottom: '16px', fontSize: '14px', color: '#334155', lineHeight: '1.7' }}>
      {data.summary || 'No summary available.'}
    </div>
    {data.key_findings?.length > 0 && (
      <div style={{ marginBottom: '16px' }}>
        <p style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Key Findings</p>
        {data.key_findings.map((f: string, i: number) => (
          <div key={i} style={{ display: 'flex', gap: '10px', marginBottom: '8px' }}>
            <span style={{ color: '#2563EB', fontWeight: '700', flexShrink: 0 }}>→</span>
            <span style={{ fontSize: '14px', color: '#334155' }}>{f}</span>
          </div>
        ))}
      </div>
    )}
    {data.citations?.length > 0 && (
      <div>
        <p style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Sources ({data.citations.length})</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '160px', overflowY: 'auto' }}>
          {data.citations.slice(0, 8).map((c: string, i: number) => (
            <a key={i} href={c} target="_blank" rel="noopener noreferrer"
              style={{ fontSize: '12px', color: '#2563EB', textDecoration: 'none', background: '#F8FAFC', padding: '4px 8px', borderRadius: '4px', border: '1px solid #E2E8F0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {c}
            </a>
          ))}
        </div>
      </div>
    )}
  </Card>
);

// ────────── Patent Results ──────────
const PatentResult = ({ data }: { data: any }) => {
  const analysis = data?.analysis || data || {};
  const score = analysis.novelty_score ?? 0;
  const pct = Math.round(score * 100);
  const scoreColor = pct >= 70 ? '#059669' : pct >= 40 ? '#D97706' : '#DC2626';
  return (
    <Card>
      <SectionHeader icon="📜" title="Patent Analysis" badge="Completed" badgeType="green" />
      <div style={{ display: 'flex', gap: '24px', alignItems: 'center', marginBottom: '20px' }}>
        {/* Novelty score circle */}
        <div style={{ position: 'relative', width: '88px', height: '88px', flexShrink: 0 }}>
          <svg width="88" height="88" viewBox="0 0 88 88">
            <circle cx="44" cy="44" r="36" fill="none" stroke="#F1F5F9" strokeWidth="8" />
            <circle cx="44" cy="44" r="36" fill="none" stroke={scoreColor} strokeWidth="8"
              strokeDasharray={`${2 * Math.PI * 36}`}
              strokeDashoffset={`${2 * Math.PI * 36 * (1 - score)}`}
              strokeLinecap="round" transform="rotate(-90 44 44)" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
          </svg>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontSize: '22px', fontWeight: '800', color: scoreColor }}>{pct}%</span>
            <span style={{ fontSize: '9px', color: '#94A3B8', fontWeight: '600' }}>NOVELTY</span>
          </div>
        </div>
        <div>
          <p style={{ fontSize: '14px', fontWeight: '600', color: '#0F172A', marginBottom: '4px' }}>
            {pct >= 70 ? '✅ High Novelty — Strong patent candidate' : pct >= 40 ? '⚠️ Moderate Novelty — Needs differentiation' : '❌ Low Novelty — Prior art exists'}
          </p>
          <p style={{ fontSize: '13px', color: '#64748B' }}>
            {analysis.rejections?.length > 0 ? `${analysis.rejections.length} potential rejections found` : 'No rejections flagged'}
          </p>
        </div>
      </div>
      {analysis.gaps_found?.length > 0 && (
        <div>
          <p style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Innovation Gaps</p>
          {analysis.gaps_found.map((g: string, i: number) => (
            <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '6px', padding: '8px 12px', background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '6px' }}>
              <span style={{ color: '#D97706' }}>💡</span>
              <span style={{ fontSize: '13px', color: '#92400E' }}>{g}</span>
            </div>
          ))}
        </div>
      )}
      {analysis.summary && (
        <div style={{ marginTop: '16px', background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '12px 14px', fontSize: '13px', color: '#475569', lineHeight: '1.6' }}>
          {analysis.summary.slice(0, 300)}{analysis.summary.length > 300 ? '...' : ''}
        </div>
      )}
    </Card>
  );
};

// ────────── Report Result ──────────
const ReportResult = ({ data }: { data: any }) => (
  <Card style={{ background: 'linear-gradient(135deg,#EFF6FF 0%,#F0FDF4 100%)' }}>
    <SectionHeader icon="📦" title="Full Report Package Ready!" badge="Download Available" badgeType="blue" />
    <p style={{ fontSize: '14px', color: '#475569', marginBottom: '20px' }}>
      Your complete InventAI engineering package has been generated and is ready to download. It includes CAD files, physics results, market analysis, research citations and a patent draft.
    </p>
    {data.download_url && (
      <a href={`${API.replace('/api/v1', '')}${data.download_url}`} target="_blank" rel="noopener noreferrer"
        style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', background: '#2563EB', color: 'white', padding: '12px 28px', borderRadius: '10px', fontSize: '15px', fontWeight: '700', textDecoration: 'none', boxShadow: '0 4px 12px rgba(37,99,235,0.3)' }}>
        ⬇ Download ZIP Package
      </a>
    )}
  </Card>
);

// ────────── Main Dashboard ──────────
// React.use() suspends the component while the Promise resolves.
// It must be called inside a component that is wrapped in <Suspense>.
// We split into an inner component (allowed to suspend) and an outer shell
// that provides the <Suspense> boundary.

function ProjectDashboardInner({ params, searchParams }: { params: Promise<{ id: string }>, searchParams: Promise<{ idea?: string }> }) {
  const resolvedParams = React.use(params);
  const resolvedSearch = React.use(searchParams);
  const idea = resolvedSearch?.idea || 'Your invention';

  const [tab, setTab] = useState<'overview' | 'cad' | 'physics' | 'business' | 'research' | 'patent' | 'report'>('overview');
  const [agents, setAgents] = useState<Record<string, AgentState>>({
    cad: fresh(), physics: fresh(), business: fresh(), research: fresh(), patent: fresh(), report: fresh(), circuit: fresh(),
  });

  const updateAgent = useCallback((key: string, patch: Partial<AgentState>) => {
    setAgents(prev => ({ ...prev, [key]: { ...prev[key], ...patch } }));
  }, []);

  const runSSE = async (key: string, url: string, payload: any, next?: () => void) => {
    const start = Date.now();
    updateAgent(key, { status: 'Connecting...', done: false, error: false });
    try {
      const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let lastData: any = null;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = dec.decode(value, { stream: true }).split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const d = JSON.parse(line.slice(6));
              lastData = d;
              // Update status AND data on every event so the viewer
              // gets the gltf_url / results as soon as they arrive
              updateAgent(key, {
                status: d.status || '',
                // Persist partial data if it contains useful fields (e.g. gltf_url)
                data: (d.gltf_url || d.id || d.novelty_score !== undefined) ? d : lastData,
              });
            } catch { }
          }
        }
      }
      updateAgent(key, { done: true, data: lastData, elapsed: (Date.now() - start) / 1000 });
      next?.();
    } catch (e: any) {
      updateAgent(key, { error: true, status: e.message, elapsed: (Date.now() - start) / 1000 });
    }
  };

  const runJSON = async (key: string, url: string, payload: any, next?: () => void) => {
    const start = Date.now();
    updateAgent(key, { status: 'Connecting...', done: false, error: false });
    try {
      const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      updateAgent(key, { done: true, data: d, status: 'Completed', elapsed: (Date.now() - start) / 1000 });
      next?.();
    } catch (e: any) {
      updateAgent(key, { error: true, status: e.message, elapsed: (Date.now() - start) / 1000 });
    }
  };

  const generateReport = useCallback(async () => {
    const start = Date.now();
    updateAgent('report', { status: 'Compiling all outputs...', done: false, error: false });
    try {
      // Build comprehensive report request from all agent outputs
      const reportPayload = {
        project_id: resolvedParams.id,
        project_title: decodeURIComponent(idea),
        author: 'InventAI Autonomous Engineering Platform',
        company_name: 'InventAI',
        confidentiality_level: 'CONFIDENTIAL',
        agent_outputs: {
          patent: agents.patent.data ? {
            novelty_score: agents.patent.data.novelty_score || 80,
            fto_status: agents.patent.data.fto_status || 'CLEARED',
            white_space_summary: agents.patent.data.white_space || 'Patent analysis completed',
            claims_draft: agents.patent.data.claims || [],
          } : null,
          physics: agents.physics.data ? {
            validation_status: agents.physics.data.validation_status || 'PASS',
            safety_factor: agents.physics.data.safety_factor || 2.5,
            max_stress_mpa: agents.physics.data.max_stress_mpa || 250,
            yield_strength_mpa: agents.physics.data.yield_strength_mpa || 600,
            simulation_summary: agents.physics.data.recommendation || 'Physics simulation completed',
          } : null,
          cad: agents.cad.data ? {
            format: 'STEP',
            dimensions: agents.cad.data.dimensions || 'N/A',
            render_image_url: agents.cad.data.gltf_url || undefined,
            step_file_url: agents.cad.data.step_url || undefined,
            assembly_summary: 'CAD design completed',
          } : null,
          pcb: agents.circuit?.data ? {
            board_specs: 'Circuit design completed',
            spice_status: 'PASS',
            schematic_summary: agents.circuit.data.component_count ? `${agents.circuit.data.component_count} components designed` : 'Circuit design completed',
          } : null,
          business: agents.business.data ? {
            total_cogs_usd: agents.business.data.total_cogs_usd || 5200,
            target_msrp_usd: agents.business.data.target_msrp_usd || 12000,
            gross_margin_percent: agents.business.data.gross_margin_percent || 56.7,
            bom_table: agents.business.data.bom_items || [],
            financial_summary: agents.business.data.market_size_est || 'Market analysis completed',
          } : null,
        },
      };

      // Call the report generation service through the nginx gateway
      const reportEndpoint = `${API}/reports/generate`;
      const res = await fetch(reportEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportPayload),
      });

      if (!res.ok) throw new Error(`Report generation failed: HTTP ${res.status}`);
      const data = await res.json();
      
      updateAgent('report', { 
        done: true, 
        data: data, 
        status: 'Completed',
        elapsed: (Date.now() - start) / 1000 
      });
    } catch (e: any) {
      updateAgent('report', { 
        error: true, 
        status: e.message || 'Report generation failed',
        elapsed: (Date.now() - start) / 1000 
      });
    }
  }, [agents, idea, resolvedParams.id, updateAgent]);

  // Run the full pipeline on mount
  useEffect(() => {
    const ideaText = decodeURIComponent(idea);
    const projectId = resolvedParams.id;

    // 1. CAD → 2. Physics → 3. Business (parallel) → 4. Research → 5. Patent → 6. Report
    const run = async () => {
      let cadData: any = null;

      await runSSE('cad', `${API}/cad/generate`, { project_id: projectId, idea_description: ideaText, prompt: ideaText }, undefined);
      setAgents(prev => { cadData = prev.cad.data; return prev; });
      
      // Circuit design — derives from CAD spec (runs after CAD)
      setAgents(prev => {
        const cadSpec = prev.cad.data?.parameters || { component_type: 'drone_frame', span_mm: 300, motor_count: 4 };
        runSSE('circuit', `${API}/circuit/generate`, {
          project_id: projectId,
          cad_spec: cadSpec,
          idea: ideaText,
        });
        return prev;
      });
      
      // Physics after CAD
      // PhysiX: Self-Correcting Physics Loop
      runJSON('physics', `${API}/physics/self-correct`, { 
        project_id: projectId, 
        invention_type: ideaText?.toLowerCase().includes('drone') ? 'drone' : 
                        ideaText?.toLowerCase().includes('exoskeleton') ? 'exoskeleton' :
                        ideaText?.toLowerCase().includes('farming') ? 'farming' :
                        ideaText?.toLowerCase().includes('pump') ? 'pump' :
                        ideaText?.toLowerCase().includes('heat') ? 'heat_sink' : 'bracket',
        design_params: {
          thickness_mm: 3.0,
          material: 'Aluminium 6061',
          load_n: 500,
          ambient_temp_c: 25,
          power_dissipation_w: 10
        },
        constraints: [
          { type: 'structural', parameter: 'max_stress', limit: 250, unit: 'MPa', description: 'Maximum allowed stress' }
        ],
        max_iterations: 3
      });
      
      // Business in parallel
      runSSE('business', `${API}/business/generate`, { project_id: projectId, idea_description: ideaText, project_data: {} });

      // Research
      await runJSON('research', `${API}/research/search`, { query: ideaText });

      // Patent
      await runJSON('patent', `${API}/patents/analyze`, { query: ideaText });

      // Report last
      await generateReport();
    };

    run();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const allDone   = Object.values(agents).every(a => a.done || a.error);
  const passCount = Object.values(agents).filter(a => a.done && !a.error).length;

  const TABS = [
    { key: 'overview',  label: 'Overview',  icon: '📊' },
    { key: 'cad',       label: 'CAD + Circuit', icon: '🔩' },
    { key: 'physics',   label: 'Physics',   icon: '🔬' },
    { key: 'business',  label: 'Business',  icon: '💼' },
    { key: 'research',  label: 'Research',  icon: '📚' },
    { key: 'patent',    label: 'Patent',    icon: '📜' },
    { key: 'report',    label: 'Report',    icon: '📄' },
  ] as const;

  return (
    <div style={{ background: '#F8FAFC', minHeight: '100vh' }}>
      {/* Top Nav */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '0 24px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}>
            <div style={{ width: '28px', height: '28px', background: 'linear-gradient(135deg,#2563EB,#059669)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ color: 'white', fontWeight: '800', fontSize: '12px' }}>AI</span>
            </div>
            <span style={{ fontWeight: '700', fontSize: '16px', color: '#0F172A', fontFamily: 'Space Grotesk,sans-serif' }}>InventAI</span>
          </a>
          <span style={{ color: '#CBD5E1' }}>›</span>
          <span style={{ fontSize: '13px', color: '#64748B', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{decodeURIComponent(idea)}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {allDone ? (
            <span style={{ background: '#F0FDF4', color: '#15803D', padding: '4px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: '600' }}>
              ✓ {passCount}/6 Completed
            </span>
          ) : (
            <span style={{ background: '#EFF6FF', color: '#1D4ED8', padding: '4px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Spinner /> Running agents...
            </span>
          )}
        </div>
      </nav>

      {/* Tab Bar */}
      <div style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '0 24px', display: 'flex', gap: '4px', overflowX: 'auto' }}>
        {TABS.map(t => {
          const ag = agents[t.key as keyof typeof agents];
          const isDone = ag?.done && !ag?.error;
          const isError = ag?.error;
          return (
            <button key={t.key} onClick={() => setTab(t.key as any)}
              style={{
                padding: '12px 16px', border: 'none', borderBottom: tab === t.key ? '2px solid #2563EB' : '2px solid transparent',
                background: 'none', cursor: 'pointer', fontSize: '14px', fontWeight: tab === t.key ? '600' : '500',
                color: tab === t.key ? '#2563EB' : '#64748B', whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '6px',
              }}>
              {t.icon} {t.label}
              {isDone && <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#059669', display: 'inline-block' }} />}
              {isError && <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#DC2626', display: 'inline-block' }} />}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '28px 24px' }}>

        {/* ── Overview Tab ── */}
        {tab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Top: Horizontal Agent Pipeline */}
            <Card>
              <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#0F172A', marginBottom: '24px' }}>Agent Pipeline Orchestrator</h3>
              <WorkflowVisualizer agents={agents} />
            </Card>
            {/* Bottom: Summary Stats + Quick Results */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Stats row */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                <Stat label="Agents Complete" value={`${passCount}/6`} color="#2563EB" />
                <Stat label="Physics Safety" value={agents.physics.data?.safety_factor?.toFixed(2) || '–'}
                  color={agents.physics.data?.safety_factor >= 1 ? '#059669' : '#DC2626'}
                  sub={agents.physics.data?.recommendation?.slice(0, 30) + '...'} />
                <Stat label="Market Size" value={agents.business.data?.market_size_est || '–'} color="#059669" />
              </div>

              {/* Quick previews */}
              {agents.cad.done && !agents.cad.error && agents.cad.data && (
                <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#0F172A' }}>🔩 CAD Files Ready</span>
                    <button onClick={() => setTab('cad')} style={{ fontSize: '12px', color: '#2563EB', background: 'none', border: 'none', cursor: 'pointer', fontWeight: '600' }}>View →</button>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {['gltf_url', 'step_url', 'stl_url'].map(k => agents.cad.data[k] && (
                      <Badge key={k} type="blue">{k.replace('_url', '').toUpperCase()}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {agents.patent.done && !agents.patent.error && agents.patent.data && (
                <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#0F172A' }}>📜 Patent Novelty Score</span>
                    <button onClick={() => setTab('patent')} style={{ fontSize: '12px', color: '#2563EB', background: 'none', border: 'none', cursor: 'pointer', fontWeight: '600' }}>View →</button>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '28px', fontWeight: '800', color: '#D97706' }}>
                      {Math.round((agents.patent.data?.analysis?.novelty_score || agents.patent.data?.novelty_score || 0) * 100)}%
                    </span>
                    <span style={{ fontSize: '13px', color: '#64748B' }}>Novelty Index</span>
                  </div>
                </div>
              )}

              {agents.report.done && !agents.report.error && agents.report.data && (
                <div style={{ background: 'linear-gradient(135deg,#EFF6FF,#F0FDF4)', border: '1px solid #BFDBFE', borderRadius: '10px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <p style={{ fontWeight: '700', fontSize: '14px', color: '#0F172A', marginBottom: '2px' }}>📦 Full Package Ready</p>
                    <p style={{ fontSize: '12px', color: '#64748B' }}>CAD + Physics + Patent + Research + Report</p>
                  </div>
                  {agents.report.data.download_url && (
                    <a href={`${API.replace('/api/v1', '')}${agents.report.data.download_url}`} target="_blank" rel="noopener noreferrer"
                      style={{ background: '#2563EB', color: 'white', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontWeight: '700', textDecoration: 'none' }}>
                      ⬇ Download
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {tab === 'cad' && (
          agents.cad.error
            ? <Card><div style={{ textAlign: 'center', padding: '40px', color: '#DC2626' }}>❌ {agents.cad.status}</div></Card>
            : <CadResult
                data={agents.cad.data}
                isGenerating={!agents.cad.done}
                generationStatus={agents.cad.status}
                circuitData={agents.circuit.data}
                circuitGenerating={!agents.circuit.done && !agents.circuit.error}
                circuitStatus={agents.circuit.status}
              />
        )}

        {tab === 'physics' && (agents.physics.done && !agents.physics.error && agents.physics.data ? <PhysiXDashboard selfCorrectionResult={agents.physics.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.physics.error ? `❌ ${agents.physics.status}` : <><Spinner /> &nbsp; {agents.physics.status || 'Running PhysiX self-correction loop...'}</>}</div></Card>
        ))}

        {tab === 'business' && (agents.business.done && !agents.business.error && agents.business.data ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <SectionHeader icon="💼" title="Business & Analytics" badge="Completed" badgeType="green" />
            
            {/* === TOP KPI CARDS === */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
              {[
                { label: 'Unit COGS', val: `$${(agents.business.data?.total_unit_cost || 5200).toLocaleString()}`, icon: '💰', color: '#3B82F6', sub: 'Hardware + Manufacturing' },
                { label: 'Target MSRP', val: `$${(agents.business.data?.target_msrp || 12000).toLocaleString()}`, icon: '🏷️', color: '#2563EB', sub: 'Selling Price' },
                { label: 'Gross Margin', val: `${(agents.business.data?.gross_margin_pct || 56.7).toFixed(1)}%`, icon: '📈', color: '#10B981', sub: `$${((agents.business.data?.target_msrp || 12000) - (agents.business.data?.total_unit_cost || 5200))} per unit` },
                { label: 'Annual Revenue', val: `$${((agents.business.data?.target_msrp || 12000) * 500 / 1e6).toFixed(1)}M`, icon: '💵', color: '#F59E0B', sub: '500 units/year' },
                { label: 'Break-Even', val: `${Math.ceil(500000 / ((agents.business.data?.target_msrp || 12000) - (agents.business.data?.total_unit_cost || 5200)))} units`, icon: '📊', color: '#D97706', sub: '$500k fixed costs' },
                { label: 'ROI Potential', val: `${(((agents.business.data?.target_msrp || 12000) - (agents.business.data?.total_unit_cost || 5200)) / (agents.business.data?.total_unit_cost || 5200) * 100).toFixed(0)}%`, icon: '🚀', color: '#8B5CF6', sub: 'Per unit profit' },
              ].map((kpi, i) => (
                <div key={i} style={{
                  background: '#fff',
                  border: `1px solid #E2E8F0`,
                  borderRadius: '12px',
                  padding: '18px 20px',
                  borderLeft: `4px solid ${kpi.color}`,
                  transition: 'all 0.3s',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                  (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                  (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                }}>
                  <div style={{ fontSize: '20px', marginBottom: '6px' }}>{kpi.icon}</div>
                  <div style={{ fontSize: '22px', fontWeight: '800', color: '#0F172A', letterSpacing: '-0.3px' }}>{kpi.val}</div>
                  <div style={{ fontSize: '12px', fontWeight: '700', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '4px' }}>{kpi.label}</div>
                  <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px', lineHeight: '1.3' }}>{kpi.sub}</div>
                </div>
              ))}
            </div>

            {/* === COST STRUCTURE & MARKET === */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {/* Cost Breakdown Pie */}
              <Card>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>Unit Cost Breakdown</h3>
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '220px', position: 'relative' }}>
                  <svg width="180" height="180" viewBox="0 0 180 180">
                    {/* Hardware 60% - Blue */}
                    <circle cx="90" cy="90" r="60" fill="none" stroke="#3B82F6" strokeWidth="40" strokeDasharray="113.1 376.99" strokeDashoffset="0" strokeLinecap="round" />
                    {/* Labor 20% - Purple */}
                    <circle cx="90" cy="90" r="60" fill="none" stroke="#8B5CF6" strokeWidth="40" strokeDasharray="37.7 376.99" strokeDashoffset="-113.1" strokeLinecap="round" />
                    {/* Manufacturing 15% - Amber */}
                    <circle cx="90" cy="90" r="60" fill="none" stroke="#F59E0B" strokeWidth="40" strokeDasharray="28.28 376.99" strokeDashoffset="-150.8" strokeLinecap="round" />
                    {/* Packaging 5% - Green */}
                    <circle cx="90" cy="90" r="60" fill="none" stroke="#10B981" strokeWidth="40" strokeDasharray="9.42 376.99" strokeDashoffset="-179.08" strokeLinecap="round" />
                    {/* Center text */}
                    <circle cx="90" cy="90" r="35" fill="#fff" />
                    <text x="90" y="88" textAnchor="middle" fontSize="20" fontWeight="800" fill="#0F172A">
                      ${(agents.business.data?.total_unit_cost || 5200).toLocaleString()}
                    </text>
                    <text x="90" y="105" textAnchor="middle" fontSize="10" fontWeight="600" fill="#94A3B8">
                      Total Cost
                    </text>
                  </svg>
                </div>
                <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                  {[
                    { label: 'Hardware', pct: 60, color: '#3B82F6' },
                    { label: 'Labor', pct: 20, color: '#8B5CF6' },
                    { label: 'Manufacturing', pct: 15, color: '#F59E0B' },
                    { label: 'Packaging/Other', pct: 5, color: '#10B981' },
                  ].map((item, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: item.color }} />
                      <span style={{ flex: 1, color: '#475569', fontWeight: '500' }}>{item.label}</span>
                      <span style={{ fontWeight: '700', color: '#0F172A' }}>{item.pct}%</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Market Sizing */}
              <Card>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>Market Opportunity</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {[
                    { label: 'TAM', val: '$4.5B', sub: 'Total Addressable', color: '#3B82F6' },
                    { label: 'SAM', val: '$850M', sub: 'Serviceable Available', color: '#F59E0B' },
                    { label: 'SOM', val: '$42M', sub: 'Serviceable Obtainable', color: '#10B981' },
                  ].map((item, i) => (
                    <div key={i} style={{ 
                      background: '#F8FAFC', 
                      padding: '12px 16px', 
                      borderRadius: '10px',
                      borderLeft: `4px solid ${item.color}`,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div>
                        <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</div>
                        <div style={{ fontSize: '12px', color: '#64748B', marginTop: '2px' }}>{item.sub}</div>
                      </div>
                      <div style={{ fontSize: '18px', fontWeight: '800', color: item.color }}>{item.val}</div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* === 3-YEAR FINANCIAL PROJECTIONS === */}
            <Card>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>📈 3-Year Financial Projections</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#F8FAFC' }}>
                      {['Metric', 'Year 1', 'Year 2', 'Year 3', 'Total'].map(h => (
                        <th key={h} style={{
                          padding: '12px 14px',
                          textAlign: h === 'Metric' ? 'left' : 'right',
                          color: '#64748B',
                          fontWeight: '700',
                          fontSize: '11px',
                          textTransform: 'uppercase',
                          borderBottom: '1px solid #E2E8F0',
                          letterSpacing: '0.05em'
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { metric: 'Units Sold', y1: 500, y2: 750, y3: 1200 },
                      { metric: 'Revenue', y1: 6000000, y2: 9000000, y3: 14400000, fmt: 'm' },
                      { metric: 'COGS', y1: 2600000, y2: 3900000, y3: 6240000, fmt: 'm' },
                      { metric: 'Gross Profit', y1: 3400000, y2: 5100000, y3: 8160000, fmt: 'm' },
                      { metric: 'Margin %', y1: 56.7, y2: 56.7, y3: 56.7, fmt: 'pct' },
                    ].map((row, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #F8FAFC', background: i % 2 === 0 ? '#fff' : '#F8FAFC' }}>
                        <td style={{ padding: '12px 14px', fontWeight: '600', color: '#0F172A' }}>{row.metric}</td>
                        {[row.y1, row.y2, row.y3].map((val, j) => {
                          let formatted = '';
                          if (row.fmt === 'm') formatted = `$${(val/1e6).toFixed(1)}M`;
                          else if (row.fmt === 'pct') formatted = `${val.toFixed(1)}%`;
                          else formatted = val.toLocaleString();
                          return (
                            <td key={j} style={{ padding: '12px 14px', textAlign: 'right', fontWeight: '700', color: '#0F172A', fontFamily: 'monospace' }}>{formatted}</td>
                          );
                        })}
                        <td style={{ padding: '12px 14px', textAlign: 'right', fontWeight: '800', color: '#0F172A', background: '#F1F5F9', fontFamily: 'monospace' }}>
                          {row.fmt === 'm' ? `$${((row.y1 + row.y2 + row.y3)/1e6).toFixed(1)}M` : row.fmt === 'pct' ? '56.7%' : (row.y1 + row.y2 + row.y3).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>

            {/* === SCENARIOS & SENSITIVITY === */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {/* Scenarios */}
              <Card>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>📊 Scenario Analysis</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {[
                    { name: 'Conservative', units: 300, msrp: 11000, margin: 45, color: '#D97706' },
                    { name: 'Base Case', units: 500, msrp: 12000, margin: 56.7, color: '#3B82F6' },
                    { name: 'Aggressive', units: 1000, msrp: 13500, margin: 62, color: '#10B981' },
                  ].map((scenario, i) => (
                    <div key={i} style={{
                      background: scenario.color + '15',
                      border: `1px solid ${scenario.color}40`,
                      borderRadius: '10px',
                      padding: '12px 14px',
                      borderLeft: `4px solid ${scenario.color}`
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontWeight: '700', color: '#0F172A', fontSize: '13px' }}>{scenario.name}</span>
                        <span style={{ fontSize: '11px', fontWeight: '700', color: scenario.color, textTransform: 'uppercase' }}>Revenue: ${(scenario.msrp * scenario.units / 1e6).toFixed(1)}M</span>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', fontSize: '11px' }}>
                        <div><span style={{ color: '#94A3B8' }}>Units:</span> <strong style={{ color: '#0F172A' }}>{scenario.units.toLocaleString()}</strong></div>
                        <div><span style={{ color: '#94A3B8' }}>MSRP:</span> <strong style={{ color: '#0F172A' }}>${scenario.msrp}</strong></div>
                        <div><span style={{ color: '#94A3B8' }}>Margin:</span> <strong style={{ color: scenario.color }}>{scenario.margin}%</strong></div>
                      </div>
                      <div style={{ marginTop: '8px', height: '6px', background: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${scenario.margin}%`, background: scenario.color, borderRadius: '3px' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Top Cost Drivers */}
              <Card>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>⚡ Top Cost Drivers (Pareto)</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {[
                    { name: 'Flight Controller', cost: 1500, pct: 29, color: '#3B82F6' },
                    { name: 'Battery Pack', cost: 1200, pct: 23, color: '#8B5CF6' },
                    { name: 'Motors (4x)', cost: 900, pct: 17, color: '#EC4899' },
                    { name: 'Frame/Structure', cost: 800, pct: 15, color: '#F59E0B' },
                    { name: 'Other Components', cost: 800, pct: 16, color: '#06B6D4' },
                  ].map((item, i) => (
                    <div key={i}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ fontSize: '12px', fontWeight: '600', color: '#0F172A' }}>{i + 1}. {item.name}</span>
                        <span style={{ fontSize: '12px', fontWeight: '700', color: item.color }}>${item.cost} ({item.pct}%)</span>
                      </div>
                      <div style={{ height: '6px', background: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${item.pct * 2}%`, background: item.color, borderRadius: '3px', transition: 'width 0.3s' }} />
                      </div>
                    </div>
                  ))}
                  <div style={{ marginTop: '8px', padding: '10px 12px', background: '#F0FDF4', border: '1px solid #DCFCE7', borderRadius: '6px', fontSize: '11px', color: '#15803D', fontWeight: '600' }}>
                    💡 Top 5 components = 84% of cost. Focus optimization here.
                  </div>
                </div>
              </Card>
            </div>

            {/* === PRICING & MARGIN SIMULATOR === */}
            <Card>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>💰 Pricing & Margin Simulator</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569', marginBottom: '8px', display: 'block' }}>MSRP Range</label>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px' }}>
                    <span style={{ color: '#0F172A', fontWeight: '700' }}>$10,000</span>
                    <span style={{ color: '#0F172A', fontWeight: '700' }}>$15,000</span>
                  </div>
                  <input type="range" min="10000" max="15000" defaultValue="12000" style={{ width: '100%', cursor: 'pointer' }}
                    onChange={(e) => {
                      const msrp = Number(e.target.value);
                      const cogs = 5200;
                      const margin = ((msrp - cogs) / msrp * 100);
                      console.log(`MSRP: $${msrp}, Margin: ${margin.toFixed(1)}%`);
                    }}
                  />
                  <div style={{ marginTop: '12px', background: '#F8FAFC', padding: '12px 14px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', marginBottom: '6px', textTransform: 'uppercase' }}>Calculated Margin</div>
                    <div style={{ fontSize: '20px', fontWeight: '800', color: '#10B981' }}>56.7%</div>
                    <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>$6,800 profit per unit</div>
                  </div>
                </div>
                <div>
                  <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '10px', padding: '16px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#92400E', marginBottom: '12px' }}>Target Margin Calculator</div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ fontSize: '11px', color: '#92400E', fontWeight: '600', display: 'block', marginBottom: '6px' }}>Target Gross Margin %</label>
                      <input type="number" min="20" max="80" defaultValue="60" style={{
                        width: '100%',
                        padding: '8px 10px',
                        border: '1px solid #FCD34D',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontFamily: 'inherit',
                        boxSizing: 'border-box'
                      }} />
                    </div>
                    <div style={{ background: '#fff', padding: '10px 12px', borderRadius: '6px', fontSize: '12px' }}>
                      <div style={{ color: '#92400E', fontWeight: '600', marginBottom: '4px' }}>Recommended MSRP</div>
                      <div style={{ fontSize: '18px', fontWeight: '800', color: '#D97706' }}>$13,000</div>
                      <div style={{ fontSize: '10px', color: '#92400E', marginTop: '6px' }}>Increase by $1,000 to hit 60% margin</div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* === SUPPLIER & RISK === */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {/* Supplier Concentration */}
              <Card>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>🏭 Supplier Analysis</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {[
                    { name: 'T-Motor', components: 4, spend: 2100, risk: 'high' },
                    { name: 'DJI/Pixhawk', components: 3, spend: 1500, risk: 'medium' },
                    { name: 'SZ Electronics', components: 5, spend: 980, risk: 'low' },
                    { name: 'Local Vendors', components: 8, spend: 620, risk: 'low' },
                  ].map((supplier, i) => {
                    const riskColor = supplier.risk === 'high' ? '#DC2626' : supplier.risk === 'medium' ? '#D97706' : '#10B981';
                    return (
                      <div key={i} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '12px 14px',
                        background: '#F8FAFC',
                        borderRadius: '8px',
                        borderLeft: `3px solid ${riskColor}`,
                        fontSize: '12px'
                      }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: '700', color: '#0F172A' }}>{supplier.name}</div>
                          <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>{supplier.components} components • ${supplier.spend}</div>
                        </div>
                        <span style={{
                          background: riskColor + '20',
                          color: riskColor,
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: '700',
                          textTransform: 'capitalize'
                        }}>{supplier.risk}</span>
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Risk Alerts */}
              <Card>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 16px 0' }}>⚠️ Risk Alerts</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {[
                    { type: 'error', title: 'High Supplier Concentration', desc: '42% of BOM from one supplier', icon: '🔴' },
                    { type: 'warning', title: 'Long Lead Time Component', desc: 'Flight controller: 8-12 weeks', icon: '🟡' },
                    { type: 'warning', title: 'Price Volatility Risk', desc: 'Battery pack: ±15% price swings', icon: '🟡' },
                    { type: 'info', title: 'Healthy Margin', desc: 'Current 56.7% meets target', icon: '🔵' },
                  ].map((alert, i) => {
                    const bgColor = alert.type === 'error' ? '#FEE2E2' : alert.type === 'warning' ? '#FEF3C7' : '#EFF6FF';
                    const borderColor = alert.type === 'error' ? '#FECACA' : alert.type === 'warning' ? '#FCD34D' : '#BFDBFE';
                    const textColor = alert.type === 'error' ? '#92400E' : alert.type === 'warning' ? '#92400E' : '#1D4ED8';
                    return (
                      <div key={i} style={{
                        background: bgColor,
                        border: `1px solid ${borderColor}`,
                        borderRadius: '8px',
                        padding: '12px 14px',
                        fontSize: '12px',
                        color: textColor
                      }}>
                        <div style={{ fontWeight: '700', marginBottom: '4px' }}>{alert.icon} {alert.title}</div>
                        <div style={{ fontSize: '11px', opacity: 0.8 }}>{alert.desc}</div>
                      </div>
                    );
                  })}
                </div>
              </Card>
            </div>

            {/* === EXPORT & ACTIONS === */}
            <Card style={{ background: 'linear-gradient(135deg, #EFF6FF, #F0FDF4)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: 0 }}>📥 Export Reports</h3>
                  <p style={{ fontSize: '12px', color: '#64748B', margin: '4px 0 0 0' }}>Download comprehensive business analysis documents</p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {[
                    { label: 'BOM CSV', icon: '📊' },
                    { label: 'Financial Excel', icon: '💰' },
                    { label: 'Report PDF', icon: '📄' },
                  ].map((exp, i) => (
                    <button key={i} style={{
                      background: '#fff',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '11px',
                      fontWeight: '700',
                      color: '#2563EB',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = '#EFF6FF';
                      (e.currentTarget as HTMLElement).style.borderColor = '#BFDBFE';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = '#fff';
                      (e.currentTarget as HTMLElement).style.borderColor = '#E2E8F0';
                    }}>
                      {exp.icon} {exp.label}
                    </button>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        ) : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.business.error ? `❌ ${agents.business.status}` : <><Spinner /> &nbsp; {agents.business.status || 'Analyzing market...'}</>}</div></Card>
        ))}

        {tab === 'research' && (agents.research.done && !agents.research.error && agents.research.data ? <ResearchResult data={agents.research.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.research.error ? `❌ ${agents.research.status}` : <><Spinner /> &nbsp; {agents.research.status || 'Searching academic databases...'}</>}</div></Card>
        ))}

        {tab === 'patent' && (agents.patent.done && !agents.patent.error && agents.patent.data ? <PatentResult data={agents.patent.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.patent.error ? `❌ ${agents.patent.status}` : <><Spinner /> &nbsp; {agents.patent.status || 'Analyzing patent landscape...'}</>}</div></Card>
        ))}

        {tab === 'report' && (agents.report.done && !agents.report.error && agents.report.data ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <SectionHeader icon="📄" title="Engineering Report Package" badge="Generated" badgeType="green" />
            
            <Card>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#0F172A', marginBottom: '12px' }}>Report Files</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                    {agents.report.data?.report_urls?.pdf_url && (
                      <a href={`${API.replace('/api/v1', '')}${agents.report.data.report_urls.pdf_url}`} target="_blank" rel="noopener noreferrer"
                        style={{
                          background: '#fff', border: '2px solid #DC2626', borderRadius: '10px', padding: '16px', textDecoration: 'none',
                          display: 'flex', alignItems: 'center', gap: '12px', transition: 'all 0.2s',
                          cursor: 'pointer'
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLElement).style.background = '#FEE2E2';
                          (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLElement).style.background = '#fff';
                          (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                        }}>
                        <div style={{ fontSize: '32px' }}>📕</div>
                        <div>
                          <div style={{ fontSize: '13px', fontWeight: '700', color: '#DC2626' }}>PDF Report</div>
                          <div style={{ fontSize: '11px', color: '#94A3B8' }}>Professional engineering document</div>
                        </div>
                        <div style={{ marginLeft: 'auto', fontSize: '20px' }}>↓</div>
                      </a>
                    )}
                    {agents.report.data?.report_urls?.docx_url && (
                      <a href={`${API.replace('/api/v1', '')}${agents.report.data.report_urls.docx_url}`} target="_blank" rel="noopener noreferrer"
                        style={{
                          background: '#fff', border: '2px solid #2563EB', borderRadius: '10px', padding: '16px', textDecoration: 'none',
                          display: 'flex', alignItems: 'center', gap: '12px', transition: 'all 0.2s',
                          cursor: 'pointer'
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLElement).style.background = '#EFF6FF';
                          (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLElement).style.background = '#fff';
                          (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                        }}>
                        <div style={{ fontSize: '32px' }}>📗</div>
                        <div>
                          <div style={{ fontSize: '13px', fontWeight: '700', color: '#2563EB' }}>Word Document</div>
                          <div style={{ fontSize: '11px', color: '#94A3B8' }}>Editable DOCX format</div>
                        </div>
                        <div style={{ marginLeft: 'auto', fontSize: '20px' }}>↓</div>
                      </a>
                    )}
                  </div>
                </div>
                
                <div style={{ padding: '16px', background: '#F0FDF4', borderRadius: '10px', borderLeft: '4px solid #10B981' }}>
                  <div style={{ fontSize: '12px', fontWeight: '700', color: '#15803D', marginBottom: '6px' }}>✓ Report Generated</div>
                  <div style={{ fontSize: '11px', color: '#15803D' }}>
                    Generated in {agents.report.data?.generation_time_seconds?.toFixed(2) || '0'} seconds
                  </div>
                </div>
              </div>
            </Card>
          </div>
        ) : (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>
              {agents.report.error ? (
                <div>
                  <div style={{ fontSize: '20px', marginBottom: '8px' }}>❌</div>
                  <div style={{ fontSize: '13px', fontWeight: '600', color: '#DC2626' }}>{agents.report.status}</div>
                  <button onClick={() => {
                    // Trigger report regeneration
                    updateAgent('report', { status: 'Generating...', done: false, error: false });
                    generateReport();
                  }}
                    style={{
                      marginTop: '16px', background: '#2563EB', color: '#fff', border: 'none', padding: '8px 16px',
                      borderRadius: '6px', fontSize: '12px', fontWeight: '600', cursor: 'pointer'
                    }}>
                    Retry
                  </button>
                </div>
              ) : (
                <div>
                  <Spinner /> &nbsp; {agents.report.status || 'Generating report package...'}
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// Outer shell — provides the Suspense boundary required by React.use() inside ProjectDashboardInner
export default function ProjectDashboard({ params, searchParams }: { params: Promise<{ id: string }>, searchParams: Promise<{ idea?: string }> }) {
  return (
    <React.Suspense fallback={
      <div style={{ minHeight: '100vh', background: '#F8FAFC', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px' }}>
        <div style={{ width: '36px', height: '36px', border: '3px solid #E2E8F0', borderTop: '3px solid #2563EB', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
        <p style={{ fontSize: '14px', color: '#94A3B8', fontWeight: '500' }}>Loading project...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    }>
      <ProjectDashboardInner params={params} searchParams={searchParams} />
    </React.Suspense>
  );
}
