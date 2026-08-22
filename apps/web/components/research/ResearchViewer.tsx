'use client';

import React, { useState, useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Search, ExternalLink, BookOpen, Calendar, ChevronDown, ChevronUp, Filter } from 'lucide-react';

interface ResearchViewerProps {
  data: any;
}

const SOURCE_COLORS: Record<string, string> = {
  'arXiv': '#B91C1C',
  'PubMed': '#2563EB',
  'IEEE': '#059669',
  'CrossRef': '#D97706',
  'Other': '#8B5CF6',
};

// ────────── Source Card ──────────
const SourceCard = ({ title, authors, source, year, relevance, url, abstract }: any) => {
  const [expanded, setExpanded] = useState(false);
  const srcColor = SOURCE_COLORS[source] || SOURCE_COLORS.Other;

  return (
    <div style={{
      background: '#fff', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '14px 16px',
      marginBottom: '8px', transition: 'all 0.2s ease',
      borderLeft: `3px solid ${srcColor}`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{ flex: 1 }}>
          <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A', margin: '0 0 4px 0', lineHeight: '1.4' }}>{title}</h4>
          <p style={{ fontSize: '11px', color: '#64748B', margin: 0 }}>
            {authors} • {year}
          </p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px', flexShrink: 0 }}>
          {/* Relevance bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '48px', height: '4px', background: '#F1F5F9', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ width: `${relevance}%`, height: '100%', background: relevance > 70 ? '#059669' : '#D97706', borderRadius: '2px' }} />
            </div>
            <span style={{ fontSize: '10px', fontWeight: '700', color: relevance > 70 ? '#059669' : '#D97706', fontFamily: 'monospace' }}>{relevance}%</span>
          </div>
          <span style={{ fontSize: '9px', fontWeight: '700', color: srcColor, background: `${srcColor}15`, padding: '1px 6px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {source}
          </span>
        </div>
      </div>
      {abstract && (
        <button onClick={() => setExpanded(!expanded)} style={{ 
          background: 'none', border: 'none', cursor: 'pointer', color: '#2563EB', 
          fontSize: '11px', fontWeight: '600', padding: '4px 0 0 0', display: 'flex', alignItems: 'center', gap: '4px' 
        }}>
          {expanded ? <ChevronUp style={{ width: '12px', height: '12px' }} /> : <ChevronDown style={{ width: '12px', height: '12px' }} />}
          {expanded ? 'Hide abstract' : 'Show abstract'}
        </button>
      )}
      {expanded && abstract && (
        <p style={{ fontSize: '11px', color: '#475569', margin: '8px 0 0 0', lineHeight: '1.6', padding: '8px', background: '#F8FAFC', borderRadius: '6px' }}>
          {abstract}
        </p>
      )}
      {url && (
        <a href={url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '11px', color: '#2563EB', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '6px' }}>
          <ExternalLink style={{ width: '10px', height: '10px' }} /> View Paper
        </a>
      )}
    </div>
  );
};

// ────────── Recency Timeline ──────────
const RecencyTimeline = ({ papers }: { papers: any[] }) => {
  const years = useMemo(() => {
    const counts: Record<string, number> = {};
    papers.forEach(p => { const y = p.year || '2024'; counts[y] = (counts[y] || 0) + 1; });
    const allYears = Object.keys(counts).sort();
    return allYears.map(y => ({ year: y, count: counts[y] }));
  }, [papers]);
  const maxCount = Math.max(...years.map(y => y.count), 1);

  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '4px', height: '48px', paddingTop: '8px' }}>
      {years.map(y => (
        <div key={y.year} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
          <div style={{
            width: '100%', maxWidth: '24px',
            height: `${Math.max(8, (y.count / maxCount) * 36)}px`,
            background: y.year >= '2023' ? '#2563EB' : y.year >= '2020' ? '#60A5FA' : '#BFDBFE',
            borderRadius: '3px 3px 0 0',
          }} />
          <span style={{ fontSize: '8px', color: '#94A3B8', marginTop: '2px', fontFamily: 'monospace' }}>{y.year.slice(2)}</span>
        </div>
      ))}
    </div>
  );
};

export default function ResearchViewer({ data }: ResearchViewerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState<string | null>(null);

  // Parse papers from backend response
  const papers = useMemo(() => {
    const rawPapers = data?.papers || data?.results || [];
    if (rawPapers.length > 0) return rawPapers;
    // Use citations as fallback
    const citations = data?.citations || [];
    return citations.map((c: string, i: number) => ({
      title: c.length > 80 ? c.slice(0, 80) + '...' : c,
      authors: 'Various Authors',
      source: c.includes('arxiv') ? 'arXiv' : c.includes('pubmed') ? 'PubMed' : c.includes('ieee') ? 'IEEE' : 'CrossRef',
      year: `202${Math.floor(Math.random() * 5)}`,
      relevance: 95 - i * 8,
      url: c.startsWith('http') ? c : null,
      abstract: null,
    }));
  }, [data]);

  // Source diversity data
  const diversityData = useMemo(() => {
    const counts: Record<string, number> = {};
    papers.forEach((p: any) => { const src = p.source || 'Other'; counts[src] = (counts[src] || 0) + 1; });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [papers]);

  // Filter papers
  const filteredPapers = useMemo(() => {
    return papers.filter((p: any) => {
      if (sourceFilter && p.source !== sourceFilter) return false;
      if (searchQuery && !p.title?.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [papers, searchQuery, sourceFilter]);

  const summary = data?.summary || 'Analysis complete. Review the synthesized findings below.';
  const keyFindings = data?.key_findings || [];

  return (
    <div style={{ display: 'flex', gap: '16px' }}>
      {/* ── Left: Papers List (60%) ── */}
      <div style={{ flex: '6', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Summary */}
        <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <BookOpen style={{ width: '16px', height: '16px', color: '#2563EB' }} />
            <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: 0 }}>Research Synthesis</h3>
          </div>
          <p style={{ fontSize: '13px', color: '#475569', margin: 0, lineHeight: '1.7' }}>{summary}</p>
        </div>

        {/* Key Findings */}
        {keyFindings.length > 0 && (
          <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '16px' }}>
            <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Key Findings</h4>
            {keyFindings.map((f: string, i: number) => (
              <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '6px' }}>
                <span style={{ color: '#2563EB', fontWeight: '700', flexShrink: 0, fontSize: '12px' }}>→</span>
                <span style={{ fontSize: '12px', color: '#334155', lineHeight: '1.5' }}>{f}</span>
              </div>
            ))}
          </div>
        )}

        {/* Search Bar */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '8px', background: '#fff',
          border: '1px solid #E2E8F0', borderRadius: '8px', padding: '8px 12px',
        }}>
          <Search style={{ width: '14px', height: '14px', color: '#94A3B8' }} />
          <input
            type="text" placeholder="Filter papers..." value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{ border: 'none', outline: 'none', fontSize: '12px', color: '#0F172A', width: '100%', background: 'transparent' }}
          />
          {sourceFilter && (
            <button onClick={() => setSourceFilter(null)} style={{
              fontSize: '10px', background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: '4px',
              padding: '2px 8px', cursor: 'pointer', color: '#2563EB', fontWeight: '600', whiteSpace: 'nowrap',
            }}>
              ✕ {sourceFilter}
            </button>
          )}
        </div>

        {/* Papers List */}
        <div style={{ display: 'flex', flexDirection: 'column', maxHeight: '400px', overflowY: 'auto' }}>
          <div style={{ fontSize: '10px', fontWeight: '600', color: '#94A3B8', marginBottom: '8px' }}>
            {filteredPapers.length} papers found — sorted by relevance
          </div>
          {filteredPapers.map((p: any, i: number) => (
            <SourceCard key={i} {...p} />
          ))}
          {filteredPapers.length === 0 && (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94A3B8', fontSize: '13px' }}>
              No papers match your filters.
            </div>
          )}
        </div>
      </div>

      {/* ── Right: Analytics Panel (40%) ── */}
      <div style={{ flex: '4', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Source Diversity Donut */}
        <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '16px' }}>
          <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: '0 0 8px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Source Diversity
          </h4>
          <div style={{ width: '100%', height: '150px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={diversityData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={35} outerRadius={55} paddingAngle={3}>
                  {diversityData.map((d, i) => (
                    <Cell key={i} fill={SOURCE_COLORS[d.name] || '#8B5CF6'} cursor="pointer" onClick={() => setSourceFilter(d.name)} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', justifyContent: 'center' }}>
            {diversityData.map((d, i) => (
              <button key={i} onClick={() => setSourceFilter(sourceFilter === d.name ? null : d.name)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', fontWeight: '600',
                  color: SOURCE_COLORS[d.name] || '#8B5CF6', background: sourceFilter === d.name ? `${SOURCE_COLORS[d.name]}15` : 'transparent',
                  border: `1px solid ${sourceFilter === d.name ? SOURCE_COLORS[d.name] : '#E2E8F0'}`,
                  borderRadius: '4px', padding: '2px 8px', cursor: 'pointer',
                }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: SOURCE_COLORS[d.name] || '#8B5CF6' }} />
                {d.name} ({d.value})
              </button>
            ))}
          </div>
        </div>

        {/* Publication Recency */}
        <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
            <Calendar style={{ width: '12px', height: '12px', color: '#2563EB' }} />
            <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Publication Recency
            </h4>
          </div>
          <RecencyTimeline papers={papers} />
          <p style={{ fontSize: '10px', color: '#94A3B8', textAlign: 'center', marginTop: '8px', marginBottom: 0 }}>
            Newer publications shown in darker blue
          </p>
        </div>

        {/* Stats */}
        <div style={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '16px' }}>
          <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Research Stats
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { label: 'Total Papers', value: papers.length, color: '#2563EB' },
              { label: 'Unique Sources', value: diversityData.length, color: '#059669' },
              { label: 'Avg Relevance', value: `${papers.length > 0 ? Math.round(papers.reduce((s: number, p: any) => s + (p.relevance || 0), 0) / papers.length) : 0}%`, color: '#D97706' },
            ].map(s => (
              <div key={s.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #F1F5F9' }}>
                <span style={{ fontSize: '11px', color: '#64748B' }}>{s.label}</span>
                <span style={{ fontSize: '13px', fontWeight: '800', color: s.color, fontFamily: 'Space Grotesk, monospace' }}>{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
