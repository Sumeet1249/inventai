'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';

// GradientWaves uses WebGL — must be client-side only
const GradientWaves = dynamic(
  () => import('@/components/ui/GradientWaves'),
  { ssr: false }
);

const AGENTS = [
  {
    icon: '⬡',
    title: 'CAD Generation',
    desc: 'Auto-generates 3D GLTF / STEP / STL models from your idea using CadQuery + parametric engine.',
  },
  {
    icon: '◈',
    title: 'Physics Simulation',
    desc: 'DeepXDE PINN solver computes stress fields, safety factors and thermal heatmaps.',
  },
  {
    icon: '◎',
    title: 'Business Intelligence',
    desc: 'Market sizing, competitor analysis and financial BOM with Excel export.',
  },
  {
    icon: '◇',
    title: 'Research RAG',
    desc: 'LangGraph RAG pipeline searches arXiv, PubMed, IEEE and CrossRef in parallel.',
  },
  {
    icon: '△',
    title: 'Patent Analysis',
    desc: 'Novelty scoring, prior-art gap detection and patent draft generation.',
  },
  {
    icon: '□',
    title: 'Report Generation',
    desc: 'Full PDF / DOCX engineering report and ZIP package export.',
  },
];

export default function Home() {
  return (
    <div style={{ background: '#000', minHeight: '100vh', color: '#fff', fontFamily: 'Inter, sans-serif' }}>

      {/* ── Nav ─────────────────────────────────────────────────── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
        padding: '0 40px', height: '60px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '30px', height: '30px',
            background: '#fff', borderRadius: '6px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{ color: '#000', fontWeight: '900', fontSize: '13px', letterSpacing: '-0.5px' }}>AI</span>
          </div>
          <span style={{ fontWeight: '700', fontSize: '17px', color: '#fff', letterSpacing: '-0.3px' }}>InventAI</span>
        </div>

        {/* Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          {['Features', 'How it works', 'Agents'].map(label => (
            <a key={label} href={`#${label.toLowerCase().replace(/\s+/, '-')}`}
              style={{ fontSize: '13px', color: 'rgba(255,255,255,0.55)', textDecoration: 'none', fontWeight: '500' }}>
              {label}
            </a>
          ))}
          <Link href="/projects/new" style={{
            fontSize: '13px', fontWeight: '600',
            background: '#fff', color: '#000',
            padding: '7px 18px', borderRadius: '6px',
            textDecoration: 'none',
          }}>
            Launch App →
          </Link>
        </div>
      </nav>

      {/* ── Hero (GradientWaves fills 100 vh) ───────────────────── */}
      <section style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden' }}>
        {/* Wave canvas — covers the full section */}
        <div style={{ position: 'absolute', inset: 0 }}>
          <GradientWaves
            horizonColor="#000000"
            waveColor="#1a1a1a"
            crestColor="#ffffff"
            speed={0.35}
            amplitude={2.2}
            waveScale={0.55}
            waveRatio={0.9}
            swell={32}
            turbulence={18}
            tilt={1.08}
            zoom={1.0}
            height={5.2}
            fogDepth={14}
            detail="medium"
            brightness={1.0}
            opacity={1.0}
            mouseInteraction={true}
            parallaxStrength={0.4}
            grain={true}
            grainIntensity={0.04}
          />
        </div>

        {/* Overlay gradient so text stays readable */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(to bottom, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.75) 100%)',
          pointerEvents: 'none',
        }} />

        {/* Hero text — centred over the waves */}
        <div style={{
          position: 'relative', zIndex: 10,
          height: '100%',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          textAlign: 'center', padding: '0 24px',
        }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            border: '1px solid rgba(255,255,255,0.2)',
            background: 'rgba(255,255,255,0.06)',
            backdropFilter: 'blur(8px)',
            padding: '5px 14px', borderRadius: '100px',
            fontSize: '12px', fontWeight: '600', color: 'rgba(255,255,255,0.75)',
            marginBottom: '28px', letterSpacing: '0.04em', textTransform: 'uppercase',
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#fff', display: 'inline-block' }} />
            AI-Powered Engineering Platform
          </div>

          {/* Headline */}
          <h1 style={{
            fontSize: 'clamp(40px, 7vw, 82px)',
            fontWeight: '800',
            color: '#fff',
            lineHeight: '1.08',
            letterSpacing: '-0.03em',
            marginBottom: '22px',
            maxWidth: '860px',
          }}>
            From Idea to<br />
            <span style={{
              background: 'linear-gradient(90deg, #ffffff 0%, rgba(255,255,255,0.55) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Patent &amp; CAD
            </span>{' '}
            in Minutes
          </h1>

          {/* Sub */}
          <p style={{
            fontSize: 'clamp(15px, 1.6vw, 18px)',
            color: 'rgba(255,255,255,0.58)',
            maxWidth: '540px',
            lineHeight: '1.75',
            marginBottom: '40px',
          }}>
            InventAI runs 6 specialized AI agents in parallel — generating 3D CAD models,
            physics simulations, market analysis, research synthesis, and patent drafts
            from a single idea.
          </p>

          {/* CTA row */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link href="/projects/new" style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              background: '#fff', color: '#000',
              padding: '13px 28px', borderRadius: '8px',
              fontSize: '15px', fontWeight: '700', textDecoration: 'none',
              letterSpacing: '-0.2px',
            }}>
              Start Inventing →
            </Link>
            <a href="#agents" style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              border: '1px solid rgba(255,255,255,0.25)',
              background: 'rgba(255,255,255,0.05)',
              color: 'rgba(255,255,255,0.8)',
              padding: '13px 28px', borderRadius: '8px',
              fontSize: '15px', fontWeight: '600', textDecoration: 'none',
              backdropFilter: 'blur(8px)',
            }}>
              See how it works
            </a>
          </div>
        </div>

        {/* Scroll indicator */}
        <div style={{
          position: 'absolute', bottom: '32px', left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px',
          opacity: 0.4,
        }}>
          <span style={{ fontSize: '11px', letterSpacing: '0.12em', textTransform: 'uppercase', color: '#fff' }}>Scroll</span>
          <div style={{ width: '1px', height: '32px', background: 'linear-gradient(to bottom, #fff, transparent)' }} />
        </div>
      </section>

      {/* ── Agent Grid ──────────────────────────────────────────── */}
      <section id="agents" style={{ padding: '100px 40px', maxWidth: '1160px', margin: '0 auto' }}>
        {/* Section label */}
        <div style={{ marginBottom: '56px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <span style={{ fontSize: '11px', fontWeight: '700', letterSpacing: '0.14em', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase' }}>
            6 Parallel Agents
          </span>
          <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: '800', color: '#fff', letterSpacing: '-0.03em', lineHeight: '1.1', margin: 0 }}>
            Every discipline.<br />One prompt.
          </h2>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1px',
          background: 'rgba(255,255,255,0.08)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '16px',
          overflow: 'hidden',
        }}>
          {AGENTS.map((agent, i) => (
            <div key={agent.title} style={{
              background: '#000',
              padding: '32px 28px',
              transition: 'background 0.2s',
            }}
              onMouseEnter={e => (e.currentTarget.style.background = '#111')}
              onMouseLeave={e => (e.currentTarget.style.background = '#000')}
            >
              <div style={{ fontSize: '22px', marginBottom: '14px', color: 'rgba(255,255,255,0.5)' }}>{agent.icon}</div>
              <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#fff', marginBottom: '8px', letterSpacing: '-0.2px' }}>
                {agent.title}
              </h3>
              <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.45)', lineHeight: '1.65', margin: 0 }}>
                {agent.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────────── */}
      <section id="how-it-works" style={{
        borderTop: '1px solid rgba(255,255,255,0.08)',
        padding: '100px 40px',
        maxWidth: '1160px', margin: '0 auto',
      }}>
        <span style={{ fontSize: '11px', fontWeight: '700', letterSpacing: '0.14em', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', display: 'block', marginBottom: '12px' }}>
          Pipeline
        </span>
        <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: '800', color: '#fff', letterSpacing: '-0.03em', marginBottom: '56px' }}>
          How it works
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {[
            { step: '01', title: 'Describe your invention', body: 'A single natural-language sentence. No CAD knowledge required.' },
            { step: '02', title: 'AI extracts engineering spec', body: 'GPT-4o-mini parses dimensions, materials, component type and constraints.' },
            { step: '03', title: '6 agents run in parallel', body: 'CAD, physics, business, research, patent and report agents execute simultaneously.' },
            { step: '04', title: 'Download your full package', body: 'GLTF / STEP / STL models, simulation data, patent draft and full report — all in one ZIP.' },
          ].map((item, i, arr) => (
            <div key={item.step} style={{
              display: 'grid', gridTemplateColumns: '80px 1fr',
              gap: '0 32px',
              padding: '36px 0',
              borderBottom: i < arr.length - 1 ? '1px solid rgba(255,255,255,0.08)' : 'none',
              alignItems: 'start',
            }}>
              <span style={{ fontSize: '12px', fontWeight: '700', color: 'rgba(255,255,255,0.2)', letterSpacing: '0.1em', paddingTop: '3px' }}>
                {item.step}
              </span>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#fff', margin: '0 0 8px', letterSpacing: '-0.3px' }}>
                  {item.title}
                </h3>
                <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.45)', margin: 0, lineHeight: '1.65' }}>
                  {item.body}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ──────────────────────────────────────────── */}
      <section style={{
        borderTop: '1px solid rgba(255,255,255,0.08)',
        padding: '100px 40px',
        textAlign: 'center',
      }}>
        <h2 style={{ fontSize: 'clamp(32px, 5vw, 64px)', fontWeight: '800', color: '#fff', letterSpacing: '-0.03em', marginBottom: '20px', lineHeight: '1.1' }}>
          Build your first invention.
        </h2>
        <p style={{ fontSize: '16px', color: 'rgba(255,255,255,0.45)', marginBottom: '36px' }}>
          No CAD experience needed. Just describe what you want to build.
        </p>
        <Link href="/projects/new" style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          background: '#fff', color: '#000',
          padding: '15px 36px', borderRadius: '8px',
          fontSize: '16px', fontWeight: '700', textDecoration: 'none',
          letterSpacing: '-0.3px',
        }}>
          Start Inventing →
        </Link>
      </section>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <footer style={{
        borderTop: '1px solid rgba(255,255,255,0.08)',
        padding: '28px 40px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.2)', fontWeight: '600' }}>InventAI</span>
        <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.18)' }}>
          Netaji Subhash Engineering College
        </span>
      </footer>
    </div>
  );
}
