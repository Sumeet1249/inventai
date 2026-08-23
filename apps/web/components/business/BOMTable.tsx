'use client';

import { useState, useMemo } from 'react';
import type { BOMItem } from '../../types/business';

interface BOMTableProps {
  items: BOMItem[];
  onRowClick?: (item: BOMItem) => void;
}

type SortField = 'unit_cost' | 'extended_cost' | 'quantity' | 'risk_level' | 'price_confidence';
type SortDir = 'asc' | 'desc';

const PriceSourceBadge = ({ source }: { source?: string }) => {
  const badges: Record<string, { bg: string; color: string; label: string }> = {
    'Live API': { bg: '#EFF6FF', color: '#0EA5E9', label: '🔵 Live' },
    'Cache': { bg: '#F0FDF4', color: '#10B981', label: '💚 Cached' },
    'Historical': { bg: '#FFF7ED', color: '#D97706', label: '⏱️ Historical' },
    'Estimated': { bg: '#FEF3C7', color: '#CA8A04', label: '❓ Estimated' },
    'Fallback': { bg: '#FEE2E2', color: '#DC2626', label: '⚠️ Fallback' },
  };

  const badge = badges[source || 'Fallback'] || badges['Fallback'];
  return (
    <span
      style={{
        background: badge.bg,
        color: badge.color,
        padding: '4px 8px',
        borderRadius: '6px',
        fontSize: '11px',
        fontWeight: '700',
        whiteSpace: 'nowrap',
      }}
    >
      {badge.label}
    </span>
  );
};

const RiskBadge = ({ level }: { level?: string }) => {
  const colors: Record<string, string> = {
    low: '#10B981',
    medium: '#D97706',
    high: '#DC2626',
  };
  const bg: Record<string, string> = {
    low: '#F0FDF4',
    medium: '#FFF7ED',
    high: '#FEE2E2',
  };
  const lvl = (level || 'low').toLowerCase();
  return (
    <span
      style={{
        background: bg[lvl] || bg.low,
        color: colors[lvl] || colors.low,
        padding: '4px 8px',
        borderRadius: '6px',
        fontSize: '11px',
        fontWeight: '700',
        textTransform: 'capitalize',
      }}
    >
      {lvl}
    </span>
  );
};

const ConfidenceDot = ({ confidence }: { confidence?: number }) => {
  let color = '#94A3B8';
  if (confidence !== undefined) {
    if (confidence >= 0.85) color = '#10B981';
    else if (confidence >= 0.7) color = '#D97706';
    else color = '#DC2626';
  }
  return (
    <div
      style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        background: color,
        display: 'inline-block',
        marginRight: '6px',
      }}
    />
  );
};

export const BOMTable: React.FC<BOMTableProps> = ({ items, onRowClick }) => {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [supplierFilter, setSupplierFilter] = useState<string | null>(null);
  const [riskFilter, setRiskFilter] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<string | null>(null);
  const [sortField, setSortField] = useState<SortField>('extended_cost');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  // Extract unique filter options
  const categories = useMemo(
    () => Array.from(new Set(items.map((i) => i.category).filter(Boolean))),
    [items]
  );
  const suppliers = useMemo(
    () => Array.from(new Set(items.map((i) => i.supplier).filter(Boolean))),
    [items]
  );
  const sources = useMemo(
    () => Array.from(new Set(items.map((i) => i.data_source).filter(Boolean))),
    [items]
  );

  // Filter and sort
  const filtered = useMemo(() => {
    let result = [...items];

    // Search
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (item) =>
          item.component_name.toLowerCase().includes(q) ||
          item.part_number?.toLowerCase().includes(q) ||
          item.supplier?.toLowerCase().includes(q)
      );
    }

    // Category
    if (categoryFilter) {
      result = result.filter((item) => item.category === categoryFilter);
    }

    // Supplier
    if (supplierFilter) {
      result = result.filter((item) => item.supplier === supplierFilter);
    }

    // Risk
    if (riskFilter) {
      result = result.filter((item) => item.risk_level === riskFilter);
    }

    // Source
    if (sourceFilter) {
      result = result.filter((item) => item.data_source === sourceFilter);
    }

    // Sort
    result.sort((a, b) => {
      let aVal: any = sortField === 'unit_cost' ? a.unit_cost_usd : sortField === 'extended_cost' ? a.extended_cost_usd : sortField === 'quantity' ? a.quantity : sortField === 'risk_level' ? a.risk_level : a.price_confidence;
      let bVal: any = sortField === 'unit_cost' ? b.unit_cost_usd : sortField === 'extended_cost' ? b.extended_cost_usd : sortField === 'quantity' ? b.quantity : sortField === 'risk_level' ? b.risk_level : b.price_confidence;

      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();

      if (aVal === undefined || aVal === null) aVal = sortField === 'extended_cost' ? 0 : '';
      if (bVal === undefined || bVal === null) bVal = sortField === 'extended_cost' ? 0 : '';

      let cmp = 0;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        cmp = aVal - bVal;
      } else {
        cmp = String(aVal).localeCompare(String(bVal));
      }

      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [items, search, categoryFilter, supplierFilter, riskFilter, sourceFilter, sortField, sortDir]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const totalCost = filtered.reduce((sum, item) => sum + item.extended_cost_usd, 0);
  const totalQty = filtered.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div style={{ marginBottom: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
          Bill of Materials ({filtered.length} items)
        </h3>

        {/* Search & Filters */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '12px' }}>
          {/* Search */}
          <input
            type="text"
            placeholder="Search by component, part number, or supplier…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              fontSize: '13px',
              fontFamily: 'inherit',
            }}
          />

          {/* Filter Row */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            {/* Category */}
            {categories.length > 0 && (
              <select
                value={categoryFilter || ''}
                onChange={(e) => setCategoryFilter(e.target.value || null)}
                style={{
                  padding: '6px 10px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontFamily: 'inherit',
                  background: '#fff',
                  cursor: 'pointer',
                }}
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            )}

            {/* Supplier */}
            {suppliers.length > 0 && (
              <select
                value={supplierFilter || ''}
                onChange={(e) => setSupplierFilter(e.target.value || null)}
                style={{
                  padding: '6px 10px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontFamily: 'inherit',
                  background: '#fff',
                  cursor: 'pointer',
                }}
              >
                <option value="">All Suppliers</option>
                {suppliers.map((sup) => (
                  <option key={sup} value={sup}>
                    {sup}
                  </option>
                ))}
              </select>
            )}

            {/* Risk */}
            <select
              value={riskFilter || ''}
              onChange={(e) => setRiskFilter(e.target.value || null)}
              style={{
                padding: '6px 10px',
                border: '1px solid #E2E8F0',
                borderRadius: '6px',
                fontSize: '12px',
                fontFamily: 'inherit',
                background: '#fff',
                cursor: 'pointer',
              }}
            >
              <option value="">All Risk Levels</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>

            {/* Source */}
            {sources.length > 0 && (
              <select
                value={sourceFilter || ''}
                onChange={(e) => setSourceFilter(e.target.value || null)}
                style={{
                  padding: '6px 10px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontFamily: 'inherit',
                  background: '#fff',
                  cursor: 'pointer',
                }}
              >
                <option value="">All Sources</option>
                {sources.map((src) => (
                  <option key={src} value={src}>
                    {src}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>
      </div>

      {/* Summary */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          background: '#F8FAFC',
          padding: '10px 14px',
          borderRadius: '8px',
          marginBottom: '12px',
          fontSize: '13px',
          fontWeight: '600',
          color: '#475569',
        }}
      >
        <span>Total Cost: ${totalCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        <span>Total Qty: {totalQty.toLocaleString()}</span>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '12px',
            background: '#fff',
          }}
        >
          <thead>
            <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
              <th
                style={{
                  padding: '10px 12px',
                  textAlign: 'left',
                  color: '#64748B',
                  fontWeight: '700',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => handleSort('unit_cost')}
              >
                Component {sortField === 'unit_cost' && (sortDir === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{
                  padding: '10px 12px',
                  textAlign: 'center',
                  color: '#64748B',
                  fontWeight: '700',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => handleSort('quantity')}
              >
                Qty {sortField === 'quantity' && (sortDir === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{
                  padding: '10px 12px',
                  textAlign: 'right',
                  color: '#64748B',
                  fontWeight: '700',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => handleSort('unit_cost')}
              >
                Unit Cost {sortField === 'unit_cost' && (sortDir === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{
                  padding: '10px 12px',
                  textAlign: 'right',
                  color: '#64748B',
                  fontWeight: '700',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => handleSort('extended_cost')}
              >
                Extended {sortField === 'extended_cost' && (sortDir === 'asc' ? '↑' : '↓')}
              </th>
              <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748B', fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Supplier
              </th>
              <th style={{ padding: '10px 12px', textAlign: 'center', color: '#64748B', fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Source
              </th>
              <th style={{ padding: '10px 12px', textAlign: 'center', color: '#64748B', fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Confidence
              </th>
              <th
                style={{
                  padding: '10px 12px',
                  textAlign: 'center',
                  color: '#64748B',
                  fontWeight: '700',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => handleSort('risk_level')}
              >
                Risk {sortField === 'risk_level' && (sortDir === 'asc' ? '↑' : '↓')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ padding: '24px', textAlign: 'center', color: '#94A3B8', fontSize: '13px' }}>
                  No components match your filters
                </td>
              </tr>
            ) : (
              filtered.map((item, idx) => (
                <tr
                  key={idx}
                  style={{
                    borderBottom: '1px solid #F8FAFC',
                    cursor: onRowClick ? 'pointer' : 'default',
                  }}
                  onClick={() => onRowClick?.(item)}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.background = '#FAFBFF';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.background = 'transparent';
                  }}
                >
                  <td style={{ padding: '10px 12px', color: '#0F172A', fontWeight: '600' }}>
                    {item.ref && <span style={{ color: '#3B82F6', fontFamily: 'monospace', fontWeight: '700', marginRight: '6px' }}>{item.ref}</span>}
                    {item.component_name}
                  </td>
                  <td style={{ padding: '10px 12px', textAlign: 'center', color: '#475569' }}>{item.quantity}</td>
                  <td style={{ padding: '10px 12px', textAlign: 'right', color: '#0F172A', fontWeight: '600', fontFamily: 'monospace' }}>
                    ${item.unit_cost_usd.toFixed(2)}
                  </td>
                  <td style={{ padding: '10px 12px', textAlign: 'right', color: '#0F172A', fontWeight: '700' }}>
                    ${item.extended_cost_usd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td style={{ padding: '10px 12px', color: '#64748B', fontSize: '12px' }}>{item.supplier || '—'}</td>
                  <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                    <PriceSourceBadge source={item.data_source} />
                  </td>
                  <td style={{ padding: '10px 12px', textAlign: 'center', fontWeight: '600' }}>
                    <ConfidenceDot confidence={item.price_confidence} />
                    {item.price_confidence ? `${(item.price_confidence * 100).toFixed(0)}%` : 'N/A'}
                  </td>
                  <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                    <RiskBadge level={item.risk_level} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
