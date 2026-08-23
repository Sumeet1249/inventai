'use client';

import React, { useState } from 'react';
import { ComponentExplainer } from './ComponentExplainer';
import { DesignLinking } from './DesignLinking';

interface ProductCardProps {
  product: {
    id: string;
    product_name: string;
    seller: string;
    price: number;
    match_score: number;
    availability: boolean;
    url: string;
    specifications?: Record<string, any>;
  };
  bomItem?: any;
  cadModel?: any;
  circuitData?: any;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  bomItem,
  cadModel,
  circuitData,
}) => {
  const [expanded, setExpanded] = useState(false);
  
  const getScoreColor = (score: number) => {
    if (score >= 95) return '#15803D';
    if (score >= 90) return '#2563EB';
    if (score >= 80) return '#F59E0B';
    return '#DC2626';
  };

  return (
    <div>
      <div
        style={{
          background: 'rgba(255, 255, 255, 0.5)',
          border: '1px solid rgba(147, 197, 253, 0.3)',
          borderRadius: '10px',
          padding: '12px',
          marginBottom: '8px',
          transition: 'all 0.3s',
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
        onMouseEnter={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.background = 'rgba(255, 255, 255, 0.7)';
          el.style.boxShadow = '0 8px 24px rgba(59, 130, 246, 0.1)';
        }}
        onMouseLeave={(e) => {
          const el = e.currentTarget as HTMLElement;
          el.style.background = 'rgba(255, 255, 255, 0.5)';
          el.style.boxShadow = 'none';
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#0F172A', marginBottom: '2px' }}>
              {product.product_name}
            </div>
            <div style={{ fontSize: '11px', color: '#64748B' }}>
              {product.seller}
              {product.availability ? (
                <span style={{ color: '#15803D', fontWeight: '600', marginLeft: '8px' }}>✓ In Stock</span>
              ) : (
                <span style={{ color: '#DC2626', fontWeight: '600', marginLeft: '8px' }}>⨯ Unavailable</span>
              )}
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', fontWeight: '800', color: '#0F172A' }}>₹{product.price}</div>
            <div
              style={{
                fontSize: '11px',
                fontWeight: '700',
                color: getScoreColor(product.match_score),
                marginTop: '2px',
              }}
            >
              {product.match_score}% match
            </div>
          </div>
        </div>

        {/* Specs */}
        {product.specifications && Object.keys(product.specifications).length > 0 && (
          <div style={{ fontSize: '10px', color: '#94A3B8', marginBottom: '8px' }}>
            {Object.entries(product.specifications)
              .slice(0, 2)
              .map(([key, value]) => (
                <div key={key}>
                  {key}: {String(value)}
                </div>
              ))}
          </div>
        )}

        {/* Action */}
        <a
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#2563EB',
            textDecoration: 'none',
            display: 'inline-block',
            marginTop: '4px',
          }}
        >
          View Product ↗
        </a>
      </div>

      {/* Expanded details */}
      {expanded && bomItem && (
        <div style={{ marginBottom: '12px' }}>
          <ComponentExplainer bomItem={bomItem} />
          <DesignLinking bomItem={bomItem} cadModel={cadModel} circuitData={circuitData} />
        </div>
      )}
    </div>
  );
};
