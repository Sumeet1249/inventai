import Link from 'next/link';

export default function Home() {
  return (
    <div style={{ background: '#F8FAFC', minHeight: '100vh' }}>
      {/* Top Nav */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '0 32px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #2563EB, #059669)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: '800', fontSize: '14px' }}>AI</span>
          </div>
          <span style={{ fontFamily: 'Space Grotesk, sans-serif', fontWeight: '700', fontSize: '18px', color: '#0F172A' }}>InventAI</span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <span style={{ fontSize: '13px', color: '#64748B', padding: '6px 12px' }}>Netaji Subhash Engineering College</span>
        </div>
      </nav>

      {/* Hero */}
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '80px 24px 40px' }}>
        <div style={{ textAlign: 'center', marginBottom: '64px' }}>
          <span style={{ display: 'inline-block', background: '#EFF6FF', color: '#1D4ED8', padding: '4px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: '600', marginBottom: '20px' }}>
            🚀 AI-Powered Engineering Platform
          </span>
          <h1 style={{ fontSize: '56px', fontWeight: '800', color: '#0F172A', lineHeight: '1.15', marginBottom: '20px', fontFamily: 'Space Grotesk, sans-serif' }}>
            From Idea to
            <span style={{ background: 'linear-gradient(135deg, #2563EB, #059669)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}> Patent & CAD</span>
            <br/>in Minutes
          </h1>
          <p style={{ fontSize: '18px', color: '#475569', maxWidth: '560px', margin: '0 auto 36px', lineHeight: '1.7' }}>
            InventAI autonomously runs 6 specialized AI agents — generating 3D CAD models, physics simulations, market analysis, research synthesis, and patent drafts from a single idea.
          </p>
          <Link href="/projects/new" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#2563EB', color: 'white', padding: '14px 32px', borderRadius: '10px', fontSize: '16px', fontWeight: '700', textDecoration: 'none', boxShadow: '0 4px 14px rgba(37,99,235,0.35)' }}>
            ⚡ Start Inventing Now →
          </Link>
        </div>

        {/* 6 Agent Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '64px' }}>
          {[
            { icon: '🔩', title: 'CAD Generation', desc: 'Auto-generates 3D GLTF/STEP/STL models from your idea using CadQuery', color: '#EFF6FF', border: '#BFDBFE', badge: '#2563EB' },
            { icon: '⚡', title: 'Physics Simulation', desc: 'DeepXDE PINN solver computes stress, safety factors and heatmaps', color: '#FFF7ED', border: '#FED7AA', badge: '#C2410C' },
            { icon: '💼', title: 'Business Intelligence', desc: 'Market sizing, competitor analysis and financial BOM with Excel export', color: '#F0FDF4', border: '#BBF7D0', badge: '#15803D' },
            { icon: '📚', title: 'Research RAG', desc: 'LangGraph RAG pipeline searches arXiv, PubMed, IEEE and CrossRef', color: '#FDF4FF', border: '#E9D5FF', badge: '#7C3AED' },
            { icon: '📜', title: 'Patent Analysis', desc: 'Novelty scoring, gap detection and patent draft generation', color: '#FFFBEB', border: '#FDE68A', badge: '#D97706' },
            { icon: '📄', title: 'Report Generation', desc: 'Full PDF/DOCX engineering report + ZIP package export', color: '#F0F9FF', border: '#BAE6FD', badge: '#0369A1' },
          ].map((agent) => (
            <div key={agent.title} style={{ background: agent.color, border: `1px solid ${agent.border}`, borderRadius: '12px', padding: '24px' }}>
              <div style={{ fontSize: '28px', marginBottom: '10px' }}>{agent.icon}</div>
              <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#0F172A', marginBottom: '6px' }}>{agent.title}</h3>
              <p style={{ fontSize: '13px', color: '#475569', lineHeight: '1.6' }}>{agent.desc}</p>
            </div>
          ))}
        </div>

        {/* How to Run */}
        <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '14px', padding: '36px' }}>
          <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '24px', color: '#0F172A' }}>🚀 How to Run the Project</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#475569', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Prerequisites</h3>
              {['Docker Desktop (running)', 'Python 3.11+', 'Node.js 18+'].map(item => (
                <div key={item} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ color: '#059669', fontWeight: '700' }}>✓</span>
                  <span style={{ fontSize: '14px', color: '#334155' }}>{item}</span>
                </div>
              ))}
            </div>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#475569', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Commands</h3>
              {[
                { step: '1', cmd: 'cd s:\\idea-project\\InventAI', desc: 'Open project folder' },
                { step: '2', cmd: 'docker compose up -d --build', desc: 'Start all 15 services' },
                { step: '3', cmd: 'Open http://localhost:8080', desc: 'Access the app' },
              ].map(item => (
                <div key={item.step} style={{ display: 'flex', gap: '12px', marginBottom: '12px', alignItems: 'flex-start' }}>
                  <span style={{ background: '#2563EB', color: 'white', width: '22px', height: '22px', borderRadius: '50%', fontSize: '11px', fontWeight: '700', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: '1px' }}>{item.step}</span>
                  <div>
                    <code style={{ display: 'block', fontSize: '12px', background: '#F1F5F9', padding: '4px 8px', borderRadius: '5px', color: '#0F172A', marginBottom: '2px' }}>{item.cmd}</code>
                    <span style={{ fontSize: '12px', color: '#64748B' }}>{item.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
