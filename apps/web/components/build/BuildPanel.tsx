'use client';

import React, { useState, useEffect } from 'react';
import { BOMTable } from './BOMTable';
import { ProductCard } from './ProductCard';
import { ShoppingList } from './ShoppingList';
import { BuildSummary } from './BuildSummary';
import { ComponentExplainer } from './ComponentExplainer';
import { DesignLinking } from './DesignLinking';

interface BuildPanelProps {
  projectId: string;
  designId: string;
  circuitData?: any;
  cadData?: any;
}

export const BuildPanel: React.FC<BuildPanelProps> = ({
  projectId,
  designId,
  circuitData,
  cadData,
}) => {
  const [tab, setTab] = useState<'summary' | 'bom' | 'products' | 'shopping'>('summary');
  const [loading, setLoading] = useState(false);
  const [bom, setBOM] = useState<any>(null);
  const [products, setProducts] = useState<any>({});
  const [shoppingList, setShoppingList] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const generateBOM = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/bom/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          design_id: designId,
          circuit_data: circuitData,
          cad_data: cadData,
        }),
      });

      if (!res.ok) throw new Error('BOM generation failed');

      const data = await res.json();
      setBOM(data);
      setTab('bom');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const searchProducts = async () => {
    if (!bom) return;

    setLoading(true);
    setError(null);

    try {
      const productsMap: any = {};

      for (const item of bom.items) {
        const res = await fetch('/api/products/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            category: item.component.category,
            name: item.component.name,
            variant: item.component.variant,
            voltage: item.component.voltage,
            interface: item.component.interface,
            package: item.component.package,
            specs: item.component.specs,
          }),
        });

        if (res.ok) {
          const data = await res.json();
          productsMap[item.id] = data.products || [];
        }
      }

      setProducts(productsMap);
      setTab('products');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateShoppingList = async () => {
    // Implementation for shopping list generation
    setTab('shopping');
  };

  return (
    <div
      style={{
        background: 'rgba(255, 255, 255, 0.6)',
        border: '1px solid rgba(147, 197, 253, 0.3)',
        borderRadius: '16px',
        backdropFilter: 'blur(10px)',
        padding: '24px',
        boxShadow: '0 8px 32px rgba(59, 130, 246, 0.08)',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3
            style={{
              fontSize: '18px',
              fontWeight: '700',
              color: '#0F172A',
              margin: 0,
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            🛠️ BUILD IT
            {bom && (
              <span
                style={{
                  background: 'rgba(34, 197, 94, 0.1)',
                  color: '#15803D',
                  padding: '4px 12px',
                  borderRadius: '100px',
                  fontSize: '12px',
                  fontWeight: '600',
                }}
              >
                {bom.total_components} components
              </span>
            )}
          </h3>

          {!bom && (
            <button
              onClick={generateBOM}
              disabled={loading}
              style={{
                background: loading ? '#93C5FD' : 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '700',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {loading ? '⟳ Generating...' : '⚡ Generate BOM'}
            </button>
          )}
        </div>

        {error && (
          <div
            style={{
              background: '#FEE2E2',
              border: '1px solid #FECACA',
              color: '#DC2626',
              padding: '12px 16px',
              borderRadius: '8px',
              fontSize: '13px',
            }}
          >
            ❌ {error}
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      {bom && (
        <div
          style={{
            display: 'flex',
            gap: '8px',
            borderBottom: '1px solid rgba(147, 197, 253, 0.3)',
            marginBottom: '16px',
          }}
        >
          {['summary', 'bom', 'products', 'shopping'].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t as any)}
              style={{
                padding: '10px 16px',
                border: 'none',
                borderBottom: tab === t ? '2px solid #2563EB' : '2px solid transparent',
                background: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: tab === t ? '600' : '500',
                color: tab === t ? '#2563EB' : '#64748B',
                textTransform: 'capitalize',
              }}
            >
              {t === 'summary' && '📊 Summary'}
              {t === 'bom' && '📋 BOM'}
              {t === 'products' && '📦 Products'}
              {t === 'shopping' && '🛒 Shopping'}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      <div>
        {tab === 'summary' && bom && <BuildSummary bom={bom} onStart={searchProducts} loading={loading} />}
        {tab === 'bom' && bom && <BOMTable bom={bom} />}
        {tab === 'products' && Object.keys(products).length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
            {bom.items.map((item: any) => (
              <div key={item.id}>
                <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A', marginBottom: '8px' }}>
                  {item.component.name}
                </h4>
                {products[item.id]?.map((product: any) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ))}
          </div>
        )}
        {tab === 'shopping' && shoppingList && <ShoppingList shoppingList={shoppingList} />}
      </div>
    </div>
  );
};
