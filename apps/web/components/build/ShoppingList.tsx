'use client';

import React, { useState } from 'react';

interface ShoppingListProps {
  shoppingList: any;
}

export const ShoppingList: React.FC<ShoppingListProps> = ({ shoppingList }) => {
  const [selectedItems, setSelectedItems] = useState(
    new Set(shoppingList.items.filter((i: any) => i.is_required).map((i: any) => i.bom_item_id))
  );

  const getTotalPrice = () => {
    return shoppingList.items
      .filter((i: any) => selectedItems.has(i.bom_item_id))
      .reduce((sum: number, item: any) => sum + item.total_price, 0);
  };

  const exportList = () => {
    const text = shoppingList.items
      .filter((i: any) => selectedItems.has(i.bom_item_id))
      .map(
        (i: any) =>
          `${i.component_name} x${i.quantity} - ₹${i.total_price} - ${i.seller} - ${i.url}`
      )
      .join('\n');

    navigator.clipboard.writeText(text);
  };

  const openAllLinks = () => {
    shoppingList.items
      .filter((i: any) => selectedItems.has(i.bom_item_id))
      .forEach((i: any) => window.open(i.url, '_blank'));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%)',
          border: '1px solid rgba(147, 197, 253, 0.3)',
          borderRadius: '10px',
          padding: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <div style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', marginBottom: '4px' }}>
            {selectedItems.size} items in shopping list
          </div>
          <div style={{ fontSize: '12px', color: '#64748B' }}>
            Across {new Set(shoppingList.items.map((i: any) => i.seller)).size} sellers
          </div>
        </div>
        <div style={{ fontSize: '20px', fontWeight: '800', color: '#1D4ED8' }}>
          ₹{getTotalPrice().toLocaleString()}
        </div>
      </div>

      {/* Items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {shoppingList.items.map((item: any) => (
          <div
            key={item.bom_item_id}
            style={{
              background: 'rgba(255, 255, 255, 0.4)',
              border: '1px solid rgba(147, 197, 253, 0.2)',
              borderRadius: '8px',
              padding: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              opacity: selectedItems.has(item.bom_item_id) ? 1 : 0.6,
              transition: 'opacity 0.2s',
            }}
          >
            <input
              type="checkbox"
              checked={selectedItems.has(item.bom_item_id)}
              onChange={(e) => {
                const newSet = new Set(selectedItems);
                if (e.target.checked) {
                  newSet.add(item.bom_item_id);
                } else {
                  newSet.delete(item.bom_item_id);
                }
                setSelectedItems(newSet);
              }}
              style={{ cursor: 'pointer', width: '16px', height: '16px' }}
            />

            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '12px', fontWeight: '600', color: '#0F172A' }}>
                {item.component_name} x{item.quantity}
              </div>
              <div style={{ fontSize: '11px', color: '#64748B', marginTop: '2px' }}>
                {item.product_name} • {item.seller}
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '13px', fontWeight: '700', color: '#0F172A' }}>
                ₹{item.total_price}
              </div>
              <div
                style={{
                  fontSize: '10px',
                  color: '#94A3B8',
                  marginTop: '2px',
                  fontWeight: '500',
                }}
              >
                {item.match_score}% match
              </div>
            </div>

            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontSize: '11px',
                color: '#2563EB',
                textDecoration: 'none',
                fontWeight: '600',
                whiteSpace: 'nowrap',
              }}
            >
              View ↗
            </a>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div
        style={{
          background: 'rgba(59, 130, 246, 0.05)',
          border: '1px solid rgba(147, 197, 253, 0.2)',
          borderRadius: '10px',
          padding: '16px',
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px',
        }}
      >
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Subtotal
          </div>
          <div style={{ fontSize: '16px', fontWeight: '800', color: '#0F172A', marginTop: '4px' }}>
            ₹{getTotalPrice().toLocaleString()}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Est. Shipping
          </div>
          <div style={{ fontSize: '16px', fontWeight: '800', color: '#0F172A', marginTop: '4px' }}>
            ₹{Math.round(shoppingList.estimated_shipping).toLocaleString()}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: '600', textTransform: 'uppercase' }}>
            Total
          </div>
          <div style={{ fontSize: '16px', fontWeight: '800', color: '#1D4ED8', marginTop: '4px' }}>
            ₹{(getTotalPrice() + shoppingList.estimated_shipping).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button
          onClick={exportList}
          style={{
            background: 'rgba(255, 255, 255, 0.5)',
            border: '1px solid rgba(147, 197, 253, 0.3)',
            color: '#1D4ED8',
            padding: '10px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            backdropFilter: 'blur(10px)',
          }}
        >
          📋 Copy List
        </button>

        <button
          onClick={openAllLinks}
          style={{
            background: 'rgba(255, 255, 255, 0.5)',
            border: '1px solid rgba(147, 197, 253, 0.3)',
            color: '#1D4ED8',
            padding: '10px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            backdropFilter: 'blur(10px)',
          }}
        >
          🔗 Open All
        </button>

        <button
          style={{
            background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
            color: 'white',
            border: 'none',
            padding: '10px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: '700',
            cursor: 'pointer',
            marginLeft: 'auto',
          }}
        >
          🛒 Buy All
        </button>
      </div>
    </div>
  );
};
