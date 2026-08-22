'use client';

import React, { useEffect, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import WorkflowVisualizer from '@/components/dashboard/WorkflowVisualizer';

const ThreeViewer = dynamic(() => import('@/components/cad/ThreeViewer'), { ssr: false });
const CircuitCanvas = dynamic(() => import('@/components/circuit/CircuitCanvas'), {
  ssr: false,
  loading: () => (
    <div style={{ height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94A3B8', fontSize: '14px', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
      Loading circuit designer...
    </div>
  ),
});

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

// ────────── CAD Results (Advanced ThreeViewer) ──────────
const CadResult = ({ data, isGenerating, generationStatus }: { data: any; isGenerating?: boolean; generationStatus?: string }) => {
  // Use a relative URL — Next.js rewrites /api/* → backend so it works
  // from browser regardless of Docker network or localhost mapping.
  const gltfUrl = data?.gltf_url ? data.gltf_url : null;
  return (
    <div>
      <SectionHeader icon="🔩" title="CAD Generation" badge={data?.gltf_url ? 'Completed' : 'Running'} badgeType={data?.gltf_url ? 'green' : 'blue'} />
      <ThreeViewer
        modelUrl={gltfUrl}
        isGenerating={isGenerating || false}
        generationStatus={generationStatus || ''}
        cadData={data}
      />
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

  const [tab, setTab] = useState<'overview' | 'cad' | 'physics' | 'business' | 'research' | 'patent' | 'report' | 'circuit'>('overview');
  const [agents, setAgents] = useState<Record<string, AgentState>>({
    cad: fresh(), physics: fresh(), business: fresh(), research: fresh(), patent: fresh(), report: fresh(),
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

  // Run the full pipeline on mount
  useEffect(() => {
    const ideaText = decodeURIComponent(idea);
    const projectId = resolvedParams.id;

    // 1. CAD → 2. Physics → 3. Business (parallel) → 4. Research → 5. Patent → 6. Report
    const run = async () => {
      let cadData: any = null;

      await runSSE('cad', `${API}/cad/generate`, { project_id: projectId, idea_description: ideaText, prompt: ideaText }, undefined);
      setAgents(prev => { cadData = prev.cad.data; return prev; });
      
      // Physics after CAD
      runSSE('physics', `${API}/physics/simulate`, { cad_model_id: projectId, simulation_type: 'stress', boundary_conditions: { force_n: 500, temp_c: 25 }, material_id: 'aluminum' });
      
      // Business in parallel
      runSSE('business', `${API}/business/generate`, { project_id: projectId, idea_description: ideaText, project_data: {} });

      // Research
      await runJSON('research', `${API}/research/search`, { query: ideaText });

      // Patent
      await runJSON('patent', `${API}/patents/analyze`, { query: ideaText });

      // Report last
      setAgents(prev => {
        const allData = {
          cad_url: prev.cad.data?.gltf_url || '',
          physics: prev.physics.data || {},
          business: prev.business.data || {},
          research: prev.research.data || {},
          patent: prev.patent.data || {},
        };
        runSSE('report', `${API}/reports/generate`, {
          project_id: projectId, idea_description: ideaText, report_type: 'full', project_data: allData
        });
        return prev;
      });
    };

    run();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const allDone = Object.values(agents).every(a => a.done || a.error);
  const passCount = Object.values(agents).filter(a => a.done && !a.error).length;

  const TABS = [
    { key: 'overview', label: 'Overview', icon: '📊' },
    { key: 'cad', label: 'CAD', icon: '🔩' },
    { key: 'circuit', label: 'Circuit', icon: '⚡' },
    { key: 'physics', label: 'Physics', icon: '🔬' },
    { key: 'business', label: 'Business', icon: '💼' },
    { key: 'research', label: 'Research', icon: '📚' },
    { key: 'patent', label: 'Patent', icon: '📜' },
    { key: 'report', label: 'Report', icon: '📄' },
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
            : <CadResult data={agents.cad.data} isGenerating={!agents.cad.done} generationStatus={agents.cad.status} />
        )}

        {tab === 'physics' && (agents.physics.done && !agents.physics.error && agents.physics.data ? <PhysicsResult data={agents.physics.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.physics.error ? `❌ ${agents.physics.status}` : <><Spinner /> &nbsp; {agents.physics.status || 'Running PINN simulation...'}</>}</div></Card>
        ))}

        {tab === 'business' && (agents.business.done && !agents.business.error && agents.business.data ? <BusinessResult data={agents.business.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.business.error ? `❌ ${agents.business.status}` : <><Spinner /> &nbsp; {agents.business.status || 'Analyzing market...'}</>}</div></Card>
        ))}

        {tab === 'research' && (agents.research.done && !agents.research.error && agents.research.data ? <ResearchResult data={agents.research.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.research.error ? `❌ ${agents.research.status}` : <><Spinner /> &nbsp; {agents.research.status || 'Searching academic databases...'}</>}</div></Card>
        ))}

        {tab === 'patent' && (agents.patent.done && !agents.patent.error && agents.patent.data ? <PatentResult data={agents.patent.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.patent.error ? `❌ ${agents.patent.status}` : <><Spinner /> &nbsp; {agents.patent.status || 'Analyzing patent landscape...'}</>}</div></Card>
        ))}

        {tab === 'report' && (agents.report.done && !agents.report.error && agents.report.data ? <ReportResult data={agents.report.data} /> : (
          <Card><div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>{agents.report.error ? `❌ ${agents.report.status}` : <><Spinner /> &nbsp; {agents.report.status || 'Generating report package...'}</>}</div></Card>
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
