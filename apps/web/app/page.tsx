import Link from 'next/link';

const AGENTS = [
  {
    icon: '🔩',
    title: 'CAD Generation',
    desc: 'Generates 3D models (GLTF · STEP · STL) using CadQuery + parametric engine',
    badge: 'CadQuery',
    grad: 'linear-gradient(135deg,#3B82F6,#1D4ED8)',
    glow: 'rgba(59,130,246,0.18)',
  },
  {
    icon: '⚡',
    title: 'Physics Simulation',
    desc: 'DeepXDE PINN solver — stress analysis, safety factors, heatmaps',
    badge: 'PINN',
    grad: 'linear-gradient(135deg,#F97316,#C2410C)',
    glow: 'rgba(249,115,22,0.18)',
  },
  {
    icon: '💼',
    title: 'Business Intelligence',
    desc: 'Market sizing, competitor landscape, financial BOM & Excel export',
    badge: 'GPT-4o',
    grad: 'linear-gradient(135deg,#10B981,#047857)',
    glow: 'rgba(16,185,129,0.18)',
  },
  {
    icon: '📚',
    title: 'Research Synthesis',
    desc: 'RAG pipeline across arXiv · PubMed · IEEE · CrossRef citations',
    badge: 'LangGraph',
    grad: 'linear-gradient(135deg,#8B5CF6,#6D28D9)',
    glow: 'rgba(139,92,246,0.18)',
  },
  {
    icon: '📜',
    title: 'Patent Analysis',
    desc: 'Novelty scoring, prior art gaps, and patent claim draft generation',
    badge: 'AI-Patent',
    grad: 'linear-gradient(135deg,#F59E0B,#B45309)',
    glow: 'rgba(245,158,11,0.18)',
  },
  {
    icon: '📄',
    title: 'Report Generation',
    desc: 'Full PDF/DOCX engineering report + ZIP package with all artifacts',
    badge: 'Auto',
    grad: 'linear-gradient(135deg,#06B6D4,#0E7490)',
    glow: 'rgba(6,182,212,0.18)',
  },
];

const STEPS = [
  { n: '01', label: 'Describe your invention', sub: 'One sentence is enough' },
  { n: '02', label: '6 AI agents run in parallel', sub: 'CAD · Physics · Business · Research · Patent · Report' },
  { n: '03', label: 'Download your full package', sub: 'GLTF · STEP · STL · PDF · DOCX · BOM' },
];

export default function Home() {
  return (
    <div style={{ background: '#ffffff', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>

      {/* ── NAV ── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 100,
        background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid #F1F5F9',
        padding: '0 40px', height: '68px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '38px', height: '38px',
            background: 'linear-gradient(135deg, #2563EB, #059669)',
            borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(37,99,235,0.3)',
          }}>
            <span style={{ color: 'white', fontWeight: '900', fontSize: '15px', letterSpacing: '-0.5px' }}>AI</span>
          </div>
          <span style={{ fontWeight: '800', fontSize: '20px', color: '#0F172A', letterSpacing: '-0.5px' }}>InventAI</span>
          <span style={{
            background: '#EFF6FF', color: '#2563EB',
            fontSize: '11px', fontWeight: '700', padding: '3px 10px', borderRadius: '20px',
            letterSpacing: '0.03em',
          }}>HACKATHON 2026</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ fontSize: '13px', color: '#64748B', fontWeight: '500' }}>Netaji Subhash Engineering College</span>
          <Link href="/projects/new" style={{
            background: 'linear-gradient(135deg,#2563EB,#1D4ED8)',
            color: 'white', padding: '9px 22px', borderRadius: '8px',
            fontSize: '14px', fontWeight: '700', textDecoration: 'none',
            boxShadow: '0 2px 8px rgba(37,99,235,0.3)',
          }}>
            Start →
          </Link>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section style={{
        maxWidth: '1160px', margin: '0 auto',
        padding: '96px 40px 80px',
        textAlign: 'center',
      }}>
        {/* Pill badge */}
        <div style={{ marginBottom: '28px' }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            background: 'linear-gradient(135deg,#EFF6FF,#F0FDF4)',
            border: '1px solid #BFDBFE',
            color: '#1D4ED8', padding: '8px 18px', borderRadius: '100px',
            fontSize: '13px', fontWeight: '700',
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22C55E', display: 'inline-block', boxShadow: '0 0 0 3px rgba(34,197,94,0.25)' }} />
            6 AI Agents · Real 3D CAD · Live Physics Simulation
          </span>
        </div>

        {/* Headline */}
        <h1 style={{
          fontSize: 'clamp(42px,6vw,72px)', fontWeight: '900',
          color: '#0F172A', lineHeight: '1.08', marginBottom: '24px',
          letterSpacing: '-2px',
        }}>
          Turn Any Idea Into a
          <br />
          <span style={{
            background: 'linear-gradient(135deg,#2563EB 0%,#7C3AED 50%,#059669 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
            Full Engineering Package
          </span>
        </h1>

        {/* Sub */}
        <p style={{
          fontSize: '18px', color: '#475569', maxWidth: '580px',
          margin: '0 auto 44px', lineHeight: '1.75', fontWeight: '400',
        }}>
          InventAI runs <strong style={{ color: '#0F172A' }}>6 specialized AI agents</strong> in parallel —
          generating 3D CAD models, physics simulations, market analysis, research,
          patent drafts and a full report from a single idea.
        </p>

        {/* CTA */}
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/projects/new" style={{
            display: 'inline-flex', alignItems: 'center', gap: '10px',
            background: 'linear-gradient(135deg,#2563EB,#1D4ED8)',
            color: 'white', padding: '16px 36px', borderRadius: '12px',
            fontSize: '16px', fontWeight: '800', textDecoration: 'none',
            boxShadow: '0 6px 24px rgba(37,99,235,0.38)',
            letterSpacing: '-0.2px',
          }}>
            ⚡ Start Inventing Now
            <span style={{ opacity: 0.85, fontSize: '18px' }}>→</span>
          </Link>
          <a href="#how" style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            background: '#F8FAFC', border: '1.5px solid #E2E8F0',
            color: '#334155', padding: '16px 28px', borderRadius: '12px',
            fontSize: '15px', fontWeight: '600', textDecoration: 'none',
          }}>
            See How It Works
          </a>
        </div>

        {/* Stats strip */}
        <div style={{
          display: 'flex', justifyContent: 'center', gap: '48px',
          marginTop: '64px', flexWrap: 'wrap',
        }}>
          {[
            { val: '6', label: 'AI Agents' },
            { val: '3D', label: 'CAD Output' },
            { val: 'PINN', label: 'Physics Engine' },
            { val: 'PDF', label: 'Full Report' },
          ].map(s => (
            <div key={s.val} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: '900', color: '#0F172A', letterSpacing: '-1px' }}>{s.val}</div>
              <div style={{ fontSize: '13px', color: '#94A3B8', fontWeight: '500', marginTop: '2px' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── AGENT CARDS ── */}
      <section style={{
        background: '#FAFBFF',
        borderTop: '1px solid #F1F5F9',
        borderBottom: '1px solid #F1F5F9',
        padding: '80px 40px',
      }}>
        <div style={{ maxWidth: '1160px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '56px' }}>
            <h2 style={{ fontSize: '36px', fontWeight: '800', color: '#0F172A', letterSpacing: '-1px', marginBottom: '12px' }}>
              6 Agents. One Pipeline.
            </h2>
            <p style={{ fontSize: '16px', color: '#64748B', maxWidth: '480px', margin: '0 auto' }}>
              Each agent is a specialized AI system. They run sequentially and in parallel to cover every dimension of your invention.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '20px' }}>
            {AGENTS.map((a, i) => (
              <div key={a.title} style={{
                background: '#ffffff',
                border: '1px solid #F1F5F9',
                borderRadius: '16px',
                padding: '28px',
                boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
                position: 'relative',
                overflow: 'hidden',
                transition: 'transform 0.2s, box-shadow 0.2s',
              }}>
                {/* Glow top-left */}
                <div style={{
                  position: 'absolute', top: '-30px', left: '-30px',
                  width: '120px', height: '120px', borderRadius: '50%',
                  background: a.glow, filter: 'blur(20px)',
                  pointerEvents: 'none',
                }} />
                {/* Number */}
                <div style={{
                  position: 'absolute', top: '20px', right: '20px',
                  fontSize: '48px', fontWeight: '900', color: '#F8FAFC',
                  lineHeight: 1, letterSpacing: '-2px',
                  fontFamily: 'Space Grotesk, sans-serif',
                }}>
                  {String(i + 1).padStart(2, '0')}
                </div>

                {/* Icon */}
                <div style={{
                  width: '52px', height: '52px', borderRadius: '14px',
                  background: a.grad,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '24px', marginBottom: '18px',
                  boxShadow: `0 4px 12px ${a.glow}`,
                }}>
                  {a.icon}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#0F172A', margin: 0 }}>{a.title}</h3>
                  <span style={{
                    background: '#F1F5F9', color: '#475569',
                    fontSize: '10px', fontWeight: '700', padding: '2px 8px', borderRadius: '20px',
                    letterSpacing: '0.04em',
                  }}>{a.badge}</span>
                </div>
                <p style={{ fontSize: '13px', color: '#64748B', lineHeight: '1.65', margin: 0 }}>{a.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how" style={{ padding: '80px 40px', background: '#ffffff' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '36px', fontWeight: '800', color: '#0F172A', letterSpacing: '-1px', marginBottom: '12px' }}>
            How It Works
          </h2>
          <p style={{ fontSize: '16px', color: '#64748B', marginBottom: '56px' }}>Three steps from idea to full engineering package.</p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '24px' }}>
            {STEPS.map((s, i) => (
              <div key={s.n} style={{
                background: '#F8FAFC', border: '1px solid #F1F5F9',
                borderRadius: '16px', padding: '32px 24px', textAlign: 'center',
                position: 'relative',
              }}>
                <div style={{
                  width: '52px', height: '52px', borderRadius: '50%',
                  background: 'linear-gradient(135deg,#2563EB,#7C3AED)',
                  color: 'white', fontWeight: '900', fontSize: '16px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 20px',
                  boxShadow: '0 4px 12px rgba(37,99,235,0.3)',
                }}>
                  {s.n}
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#0F172A', marginBottom: '8px' }}>{s.label}</h3>
                <p style={{ fontSize: '13px', color: '#64748B' }}>{s.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PIPELINE VISUALIZATION ── */}
      <section style={{
        background: '#0F172A',
        padding: '80px 40px',
      }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '32px', fontWeight: '800', color: '#ffffff', letterSpacing: '-1px', marginBottom: '12px' }}>
            Full AI Engineering Pipeline
          </h2>
          <p style={{ color: '#94A3B8', fontSize: '15px', marginBottom: '52px' }}>
            Every component connected — from idea to deliverable.
          </p>

          {/* Pipeline flow */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0', flexWrap: 'wrap' }}>
            {[
              { label: 'User Idea', bg: '#1E293B', border: '#334155', text: '#F8FAFC' },
              null,
              { label: 'AI Orchestrator', bg: '#1D4ED8', border: '#3B82F6', text: '#fff' },
              null,
              { label: 'CAD\n3D Model', bg: '#1E293B', border: '#3B82F6', text: '#93C5FD' },
              { label: 'Physics\nSimulation', bg: '#1E293B', border: '#F97316', text: '#FED7AA' },
              { label: 'Business\nAnalysis', bg: '#1E293B', border: '#10B981', text: '#A7F3D0' },
              null,
              { label: 'Patent Draft +\nFull Report', bg: '#059669', border: '#34D399', text: '#fff' },
            ].map((node, i) => node === null ? (
              <div key={i} style={{ fontSize: '20px', color: '#334155', margin: '0 4px', userSelect: 'none' }}>→</div>
            ) : (
              <div key={i} style={{
                background: node.bg, border: `1px solid ${node.border}`,
                borderRadius: '10px', padding: '12px 18px', margin: '6px',
                textAlign: 'center', minWidth: '100px',
              }}>
                <span style={{
                  fontSize: '12px', fontWeight: '700', color: node.text,
                  whiteSpace: 'pre-line', lineHeight: '1.5',
                }}>{node.label}</span>
              </div>
            ))}
          </div>

          {/* Output badges */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', marginTop: '44px', flexWrap: 'wrap' }}>
            {['GLTF', 'STEP', 'STL', 'PINN Heatmap', 'Market Report', 'BOM Excel', 'Patent Draft', 'PDF Report', 'ZIP Package'].map(tag => (
              <span key={tag} style={{
                background: '#1E293B', border: '1px solid #334155',
                color: '#94A3B8', padding: '6px 14px', borderRadius: '100px',
                fontSize: '12px', fontWeight: '600',
              }}>{tag}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ── FINAL CTA ── */}
      <section style={{
        padding: '80px 40px',
        background: '#ffffff',
        textAlign: 'center',
      }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '40px', fontWeight: '900', color: '#0F172A', letterSpacing: '-1.5px', marginBottom: '16px' }}>
            Ready to build something
            <span style={{
              background: 'linear-gradient(135deg,#2563EB,#7C3AED)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
            }}> new?</span>
          </h2>
          <p style={{ color: '#64748B', fontSize: '16px', marginBottom: '36px', lineHeight: '1.7' }}>
            Describe any invention. InventAI handles the rest — in minutes.
          </p>
          <Link href="/projects/new" style={{
            display: 'inline-flex', alignItems: 'center', gap: '10px',
            background: 'linear-gradient(135deg,#2563EB,#1D4ED8)',
            color: 'white', padding: '18px 44px', borderRadius: '14px',
            fontSize: '17px', fontWeight: '800', textDecoration: 'none',
            boxShadow: '0 8px 28px rgba(37,99,235,0.38)',
            letterSpacing: '-0.3px',
          }}>
            ⚡ Start Inventing Now →
          </Link>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{
        borderTop: '1px solid #F1F5F9', padding: '28px 40px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: '#FAFBFF',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '28px', height: '28px', background: 'linear-gradient(135deg,#2563EB,#059669)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: '900', fontSize: '11px' }}>AI</span>
          </div>
          <span style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A' }}>InventAI</span>
        </div>
        <span style={{ fontSize: '13px', color: '#94A3B8' }}>Netaji Subhash Engineering College · Hackathon 2026</span>
      </footer>

    </div>
  );
}
