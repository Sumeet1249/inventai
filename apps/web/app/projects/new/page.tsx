'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

const EXAMPLE_IDEAS = [
  "A foldable inspection drone with ultrasonic sensors for infrastructure maintenance",
  "Solar-powered water purification device for remote areas",
  "Lightweight carbon fiber exoskeleton for industrial workers",
  "Modular vertical farming unit with AI crop monitoring",
];

export default function NewProjectPage() {
  const [idea, setIdea] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!idea.trim()) return;
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API}/orchestrator/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'New Invention', idea_description: idea }),
      });
      let id = `proj-${Date.now().toString(36)}`;
      if (res.ok) {
        const data = await res.json();
        if (data && (data.id || data.project_id)) {
          id = data.id || data.project_id;
        }
      }
      router.push(`/projects/${id}?idea=${encodeURIComponent(idea)}`);
    } catch (err: any) {
      console.warn('Backend start error, proceeding to live runner dashboard', err);
      const fallbackId = `proj-${Date.now().toString(36)}`;
      router.push(`/projects/${fallbackId}?idea=${encodeURIComponent(idea)}`);
    }
  };

  return (
    <div style={{ background: '#F8FAFC', minHeight: '100vh' }}>
      {/* Nav */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '0 32px', height: '60px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}>
          <div style={{ width: '28px', height: '28px', background: 'linear-gradient(135deg,#2563EB,#059669)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: '800', fontSize: '12px' }}>AI</span>
          </div>
          <span style={{ fontWeight: '700', fontSize: '16px', color: '#0F172A', fontFamily: 'Space Grotesk,sans-serif' }}>InventAI</span>
        </a>
        <span style={{ color: '#CBD5E1', margin: '0 4px' }}>›</span>
        <span style={{ fontSize: '14px', color: '#64748B' }}>New Invention</span>
      </nav>

      <div style={{ maxWidth: '760px', margin: '0 auto', padding: '60px 24px' }}>
        {/* Header */}
        <div style={{ marginBottom: '40px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0F172A', marginBottom: '8px', fontFamily: 'Space Grotesk,sans-serif' }}>
            Describe Your Invention
          </h1>
          <p style={{ color: '#64748B', fontSize: '16px' }}>
            Our 6 AI agents will generate CAD models, physics simulations, market analysis, research synthesis and a patent draft — automatically.
          </p>
        </div>

        {/* Main Form Card */}
        <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '14px', padding: '32px', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
          <form onSubmit={handleSubmit}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#334155', marginBottom: '8px' }}>
              Idea Description *
            </label>
            <textarea
              value={idea}
              onChange={e => setIdea(e.target.value)}
              required
              rows={5}
              placeholder="E.g., A foldable inspection drone with ultrasonic sensors for infrastructure maintenance and AI-powered defect detection..."
              style={{
                width: '100%', border: '2px solid #E2E8F0', borderRadius: '10px', padding: '14px 16px',
                fontSize: '15px', color: '#0F172A', background: '#F8FAFC', resize: 'vertical',
                outline: 'none', fontFamily: 'Inter,sans-serif', lineHeight: '1.6',
                transition: 'border-color 0.2s',
              }}
              onFocus={e => e.target.style.borderColor = '#2563EB'}
              onBlur={e => e.target.style.borderColor = '#E2E8F0'}
            />
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '6px', textAlign: 'right' }}>
              {idea.length} characters
            </div>

            {error && (
              <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '8px', padding: '12px 16px', marginTop: '16px', fontSize: '14px', color: '#DC2626' }}>
                ⚠️ {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !idea.trim()}
              style={{
                marginTop: '20px', width: '100%', background: loading ? '#93C5FD' : '#2563EB',
                color: 'white', border: 'none', borderRadius: '10px', padding: '14px 24px',
                fontSize: '16px', fontWeight: '700', cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                transition: 'background 0.2s',
              }}
            >
              {loading ? (
                <>
                  <span style={{ display: 'inline-block', width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.5)', borderTop: '2px solid white', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                  Orchestrating AI Agents...
                </>
              ) : '⚡ Launch 6 AI Agents →'}
            </button>
          </form>
        </div>

        {/* Example Ideas */}
        <div style={{ marginTop: '32px' }}>
          <p style={{ fontSize: '13px', fontWeight: '600', color: '#94A3B8', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Or try an example idea
          </p>
          <div style={{ display: 'grid', gap: '10px' }}>
            {EXAMPLE_IDEAS.map(ex => (
              <button
                key={ex}
                onClick={() => setIdea(ex)}
                style={{
                  background: '#fff', border: '1px solid #E2E8F0', borderRadius: '10px',
                  padding: '14px 18px', textAlign: 'left', cursor: 'pointer', fontSize: '14px',
                  color: '#334155', transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: '10px',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = '#93C5FD'; (e.currentTarget as HTMLElement).style.background = '#EFF6FF'; }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = '#E2E8F0'; (e.currentTarget as HTMLElement).style.background = '#fff'; }}
              >
                <span style={{ color: '#2563EB', fontWeight: '700', fontSize: '16px' }}>+</span>
                {ex}
              </button>
            ))}
          </div>
        </div>

        {/* Agent Pipeline Preview */}
        <div style={{ marginTop: '40px', background: '#fff', border: '1px solid #E2E8F0', borderRadius: '14px', padding: '28px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#0F172A', marginBottom: '20px' }}>What happens when you submit</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
            {[
              { num: 1, icon: '🔩', title: 'CAD Agent', desc: 'Generates 3D model (GLTF + STEP + STL)', time: '~10s', color: '#EFF6FF' },
              { num: 2, icon: '⚡', title: 'Physics Agent', desc: 'PINN stress simulation + safety factor', time: '~5s', color: '#FFF7ED' },
              { num: 3, icon: '💼', title: 'Business Agent', desc: 'Market sizing + BOM spreadsheet', time: '~7s', color: '#F0FDF4' },
              { num: 4, icon: '📚', title: 'Research Agent', desc: 'RAG search across arXiv + IEEE + PubMed', time: '~60s', color: '#FDF4FF' },
              { num: 5, icon: '📜', title: 'Patent Agent', desc: 'Novelty score + gap analysis', time: '~40s', color: '#FFFBEB' },
              { num: 6, icon: '📄', title: 'Report Agent', desc: 'Full PDF/DOCX + ZIP package', time: '~3s', color: '#F0F9FF' },
            ].map((step, i, arr) => (
              <div key={step.num} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: step.color, border: '2px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', flexShrink: 0 }}>
                    {step.icon}
                  </div>
                  {i < arr.length - 1 && <div style={{ width: '2px', height: '28px', background: '#E2E8F0', margin: '4px 0' }} />}
                </div>
                <div style={{ paddingTop: '6px', paddingBottom: i < arr.length - 1 ? '0' : '0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: '600', fontSize: '14px', color: '#0F172A' }}>{step.title}</span>
                    <span style={{ fontSize: '11px', color: '#94A3B8', background: '#F1F5F9', padding: '2px 8px', borderRadius: '10px' }}>{step.time}</span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#64748B', marginTop: '2px' }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
