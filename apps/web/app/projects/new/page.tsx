'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/ui/Navbar';
import DotGridBackground from '@/components/ui/DotGridBackground';

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
    <div style={{ background: '#000', minHeight: '100vh', color: '#fff', fontFamily: '"Google Sans"' }}>
      <DotGridBackground />
      <Navbar variant="dark" showLogo={true} topOffset="4vh" />

      <div style={{ maxWidth: '760px', margin: '0 auto', padding: '120px 24px 60px', position: 'relative', zIndex: 10 }}>
        {/* Header */}
        <div style={{ marginBottom: '40px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '600', color: '#fff', marginBottom: '8px' }}>
            Describe Your Invention
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '16px' }}>
            Our 6 AI agents will generate CAD models, physics simulations, market analysis, research synthesis and a patent draft — automatically.
          </p>
        </div>

        {/* Main Form Card - Liquid Glass */}
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.25)',
          borderRadius: '16px',
          padding: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        }}>
          <form onSubmit={handleSubmit}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: 'rgba(255,255,255,0.8)', marginBottom: '8px' }}>
              Idea Description *
            </label>
            <textarea
              value={idea}
              onChange={e => setIdea(e.target.value)}
              required
              rows={5}
              placeholder="E.g., A foldable inspection drone with ultrasonic sensors for infrastructure maintenance and AI-powered defect detection..."
              style={{
                width: '100%', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '10px', padding: '14px 16px',
                fontSize: '15px', color: '#fff', background: 'rgba(255,255,255,0.05)', resize: 'vertical',
                outline: 'none', fontFamily: '"Google Sans", sans-serif', lineHeight: '1.6',
                transition: 'border-color 0.2s',
              }}
              onFocus={e => e.target.style.borderColor = 'rgba(255,255,255,0.4)'}
              onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.2)'}
            />
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginTop: '6px', textAlign: 'right' }}>
              {idea.length} characters
            </div>

            {error && (
              <div style={{ background: 'rgba(220, 38, 38, 0.1)', border: '1px solid rgba(220, 38, 38, 0.3)', borderRadius: '8px', padding: '12px 16px', marginTop: '16px', fontSize: '14px', color: '#fca5a5' }}>
                ⚠️ {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !idea.trim()}
              style={{
                marginTop: '20px', width: '100%', 
                background: loading ? 'rgba(255,255,255,0.2)' : 'rgba(255, 255, 255, 0.15)',
                color: '#fff', border: '1px solid rgba(255,255,255,0.25)', borderRadius: '10px', padding: '14px 24px',
                fontSize: '16px', fontWeight: '700', cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                transition: 'all 0.3s',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
              }}
              onMouseEnter={e => !loading && (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)')}
              onMouseLeave={e => !loading && (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)')}
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
          <p style={{ fontSize: '13px', fontWeight: '600', color: 'rgba(255,255,255,0.4)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Or try an example idea
          </p>
          <div style={{ display: 'grid', gap: '10px' }}>
            {EXAMPLE_IDEAS.map(ex => (
              <button
                key={ex}
                onClick={() => setIdea(ex)}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)', 
                  border: '1px solid rgba(255,255,255,0.15)', 
                  borderRadius: '10px',
                  padding: '14px 18px', textAlign: 'left', cursor: 'pointer', fontSize: '14px',
                  color: 'rgba(255,255,255,0.8)', transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: '10px',
                  backdropFilter: 'blur(8px)',
                  WebkitBackdropFilter: 'blur(8px)',
                }}
                onMouseEnter={e => { 
                  (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.3)'; 
                  (e.currentTarget as HTMLElement).style.background = 'rgba(255, 255, 255, 0.15)';
                }}
                onMouseLeave={e => { 
                  (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.15)'; 
                  (e.currentTarget as HTMLElement).style.background = 'rgba(255, 255, 255, 0.08)';
                }}
              >
                <span style={{ color: 'rgba(255,255,255,0.8)', fontWeight: '700', fontSize: '16px' }}>+</span>
                {ex}
              </button>
            ))}
          </div>
        </div>

        {/* Agent Pipeline Preview */}
        <div style={{ marginTop: '40px', 
          background: 'rgba(255, 255, 255, 0.08)',
          border: '1px solid rgba(255,255,255,0.15)', 
          borderRadius: '14px', 
          padding: '28px',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
        }}>
          <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#fff', marginBottom: '20px' }}>What happens when you submit</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
            {[
              { num: 1, icon: '🔩', title: 'CAD Agent', desc: 'Generates 3D model (GLTF + STEP + STL)', time: '~10s', color: 'rgba(100,200,255,0.2)' },
              { num: 2, icon: '⚡', title: 'Physics Agent', desc: 'PINN stress simulation + safety factor', time: '~5s', color: 'rgba(255,165,0,0.2)' },
              { num: 3, icon: '💼', title: 'Business Agent', desc: 'Market sizing + BOM spreadsheet', time: '~7s', color: 'rgba(100,255,100,0.2)' },
              { num: 4, icon: '📚', title: 'Research Agent', desc: 'RAG search across arXiv + IEEE + PubMed', time: '~60s', color: 'rgba(200,100,255,0.2)' },
              { num: 5, icon: '📜', title: 'Patent Agent', desc: 'Novelty score + gap analysis', time: '~40s', color: 'rgba(255,200,100,0.2)' },
              { num: 6, icon: '📄', title: 'Report Agent', desc: 'Full PDF/DOCX + ZIP package', time: '~3s', color: 'rgba(100,255,255,0.2)' },
            ].map((step, i, arr) => (
              <div key={step.num} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: step.color, border: '1px solid rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', flexShrink: 0 }}>
                    {step.icon}
                  </div>
                  {i < arr.length - 1 && <div style={{ width: '2px', height: '28px', background: 'rgba(255,255,255,0.1)', margin: '4px 0' }} />}
                </div>
                <div style={{ paddingTop: '6px', paddingBottom: i < arr.length - 1 ? '0' : '0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: '600', fontSize: '14px', color: '#fff' }}>{step.title}</span>
                    <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '10px' }}>{step.time}</span>
                  </div>
                  <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', marginTop: '2px' }}>{step.desc}</p>
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
