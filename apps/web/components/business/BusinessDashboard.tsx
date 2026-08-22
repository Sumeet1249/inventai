'use client';

import React, { useState } from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Area, AreaChart,
  BarChart, Bar, Legend,
} from 'recharts';
import { TrendingUp, DollarSign, Users, BarChart3, Target } from 'lucide-react';

interface BusinessDashboardProps {
  data: any;
}

// ────────── Card Wrapper ──────────
const BizCard = ({ title, icon: Icon, children, span = 1 }: any) => (
  <div style={{
    background: '#fff', border: '1px solid #E2E8F0', borderRadius: '12px',
    padding: '20px', gridColumn: `span ${span}`,
    display: 'flex', flexDirection: 'column', gap: '12px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ width: '28px', height: '28px', background: '#EFF6FF', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon style={{ width: '14px', height: '14px', color: '#2563EB' }} />
      </div>
      <span style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A' }}>{title}</span>
    </div>
    {children}
  </div>
);

// ────────── TAM/SAM/SOM Funnel ──────────
const MarketFunnel = ({ tam, sam, som }: { tam: number; sam: number; som: number }) => {
  const layers = [
    { label: 'TAM', value: tam, width: '100%', color: '#BFDBFE', textColor: '#1E40AF' },
    { label: 'SAM', value: sam, width: '70%', color: '#93C5FD', textColor: '#1E40AF' },
    { label: 'SOM', value: som, width: '40%', color: '#2563EB', textColor: '#FFFFFF' },
  ];
  const formatB = (n: number) => n >= 1e9 ? `$${(n / 1e9).toFixed(1)}B` : n >= 1e6 ? `$${(n / 1e6).toFixed(0)}M` : `$${n.toLocaleString()}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', padding: '8px 0' }}>
      {layers.map(l => (
        <div key={l.label} style={{
          width: l.width, background: l.color, borderRadius: '8px', padding: '10px 16px',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          transition: 'all 0.3s ease',
        }}>
          <span style={{ fontSize: '11px', fontWeight: '700', color: l.textColor, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{l.label}</span>
          <span style={{ fontSize: '16px', fontWeight: '800', color: l.textColor, fontFamily: 'Space Grotesk, monospace' }}>{formatB(l.value)}</span>
        </div>
      ))}
    </div>
  );
};

const PIE_COLORS = ['#2563EB', '#059669', '#D97706', '#DC2626', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

export default function BusinessDashboard({ data }: BusinessDashboardProps) {
  // Parse data from the business agent response
  const marketSize = data?.market_size_est || '$8.2B';
  const msrp = data?.suggested_msrp || '$12,000';
  const tam = data?.tam || 8_200_000_000;
  const sam = data?.sam || 2_400_000_000;
  const som = data?.som || 180_000_000;

  // BOM breakdown
  const bomItems = data?.bom_breakdown || [
    { name: 'CFRP Frame', cost: 1800 },
    { name: 'Motors (4x)', cost: 1200 },
    { name: 'Battery 6S', cost: 800 },
    { name: 'Flight Controller', cost: 350 },
    { name: 'Cameras', cost: 2200 },
    { name: 'LiDAR', cost: 3500 },
    { name: 'Jetson Orin NX', cost: 700 },
    { name: 'Other', cost: 450 },
  ];
  const totalBom = bomItems.reduce((s: number, b: any) => s + b.cost, 0);

  // Competitor data
  const competitors = data?.competitors || [
    { name: 'InventAI Drone', price: 12000, range: 8, payload: 9, autonomy: 10, inspection: 9 },
    { name: 'DJI Matrice', price: 15000, range: 9, payload: 7, autonomy: 5, inspection: 6 },
    { name: 'Skydio X10', price: 11000, range: 7, payload: 6, autonomy: 8, inspection: 7 },
    { name: 'Flyability Elios', price: 18000, range: 5, payload: 5, autonomy: 6, inspection: 8 },
  ];

  const radarData = ['price', 'range', 'payload', 'autonomy', 'inspection'].map(k => ({
    feature: k.charAt(0).toUpperCase() + k.slice(1),
    ...Object.fromEntries(competitors.map((c: any) => [c.name, c[k]])),
  }));

  // Break-even chart
  const unitCost = totalBom * 1.15; // 15% overhead
  const price = parseFloat(msrp.replace(/[^0-9.]/g, '')) || 12000;
  const fixedCosts = data?.fixed_costs || 2_000_000;
  const breakEvenData = Array.from({ length: 20 }, (_, i) => {
    const units = (i + 1) * 50;
    return {
      units,
      revenue: units * price,
      cost: fixedCosts + units * unitCost,
    };
  });

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
      {/* Market Size Card */}
      <BizCard title="Market Size (TAM/SAM/SOM)" icon={Target}>
        <MarketFunnel tam={tam} sam={sam} som={som} />
        <div style={{ fontSize: '11px', color: '#64748B', textAlign: 'center', marginTop: '4px' }}>
          Total Addressable → Serviceable Addressable → Serviceable Obtainable
        </div>
      </BizCard>

      {/* BOM Cost Breakdown */}
      <BizCard title="BOM Cost Breakdown" icon={DollarSign}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ width: '140px', height: '140px', flexShrink: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={bomItems} dataKey="cost" nameKey="name" cx="50%" cy="50%" innerRadius={35} outerRadius={60} paddingAngle={2}>
                  {bomItems.map((_: any, i: number) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '3px', maxHeight: '160px', overflowY: 'auto' }}>
            {bomItems.map((b: any, i: number) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '3px 0', borderBottom: '1px solid #F8FAFC' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: PIE_COLORS[i % PIE_COLORS.length] }} />
                  <span style={{ fontSize: '11px', color: '#475569' }}>{b.name}</span>
                </div>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#0F172A', fontFamily: 'monospace' }}>${b.cost.toLocaleString()}</span>
              </div>
            ))}
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '6px', borderTop: '1px solid #E2E8F0', marginTop: '4px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', color: '#0F172A' }}>Total BOM</span>
              <span style={{ fontSize: '13px', fontWeight: '800', color: '#2563EB', fontFamily: 'monospace' }}>${totalBom.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </BizCard>

      {/* Competitor Comparison Radar */}
      <BizCard title="Competitor Analysis" icon={Users}>
        <div style={{ width: '100%', height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} outerRadius="70%">
              <PolarGrid stroke="#E2E8F0" />
              <PolarAngleAxis dataKey="feature" tick={{ fontSize: 10, fill: '#64748B' }} />
              <PolarRadiusAxis angle={30} domain={[0, 10]} tick={false} />
              {competitors.slice(0, 3).map((c: any, i: number) => (
                <Radar key={c.name} name={c.name} dataKey={c.name} stroke={PIE_COLORS[i]} fill={PIE_COLORS[i]} fillOpacity={i === 0 ? 0.3 : 0.05} strokeWidth={i === 0 ? 2 : 1} />
              ))}
              <Legend wrapperStyle={{ fontSize: '10px' }} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </BizCard>

      {/* Break-Even Chart */}
      <BizCard title="Break-Even Analysis" icon={TrendingUp}>
        <div style={{ width: '100%', height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={breakEvenData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="units" tick={{ fontSize: 10, fill: '#94A3B8' }} label={{ value: 'Units Sold', position: 'insideBottom', offset: -5, fontSize: 10, fill: '#94A3B8' }} />
              <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} tickFormatter={(v: number) => `$${(v / 1e6).toFixed(1)}M`} />
              <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
              <Area type="monotone" dataKey="revenue" stroke="#059669" fill="#D1FAE5" fillOpacity={0.5} name="Revenue" />
              <Area type="monotone" dataKey="cost" stroke="#DC2626" fill="#FEE2E2" fillOpacity={0.3} name="Total Cost" />
              <Legend wrapperStyle={{ fontSize: '10px' }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div style={{ fontSize: '11px', color: '#64748B', textAlign: 'center' }}>
          Break-even at ~{Math.ceil(fixedCosts / (price - unitCost))} units | MSRP: {msrp} | Unit Cost: ${Math.round(unitCost).toLocaleString()}
        </div>
      </BizCard>

      {/* Unit Economics Summary (full width) */}
      <BizCard title="Unit Economics Summary" icon={BarChart3} span={2}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          {[
            { label: 'Market Size', value: marketSize, color: '#059669' },
            { label: 'Suggested MSRP', value: msrp, color: '#2563EB' },
            { label: 'BOM Cost', value: `$${totalBom.toLocaleString()}`, color: '#D97706' },
            { label: 'Gross Margin', value: `${((1 - totalBom / price) * 100).toFixed(0)}%`, color: price > totalBom ? '#059669' : '#DC2626' },
          ].map(m => (
            <div key={m.label} style={{ background: '#F8FAFC', borderRadius: '8px', padding: '14px', textAlign: 'center' }}>
              <div style={{ fontSize: '22px', fontWeight: '800', color: m.color, fontFamily: 'Space Grotesk, monospace' }}>{m.value}</div>
              <div style={{ fontSize: '10px', fontWeight: '600', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '4px' }}>{m.label}</div>
            </div>
          ))}
        </div>
      </BizCard>
    </div>
  );
}
