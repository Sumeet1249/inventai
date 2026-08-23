'use client';

import React, { useState } from 'react';

interface DesignLinkingProps {
  bomItem: any;
  cadModel?: any;
  circuitData?: any;
  onHighlight?: (componentRef: string) => void;
}

export const DesignLinking: React.FC<DesignLinkingProps> = ({
  bomItem,
  cadModel,
  circuitData,
  onHighlight,
}) => {
  const [showPosition, setShowPosition] = useState(false);
  const [showCircuitRef, setShowCircuitRef] = useState(false);

  // Extract circuit reference from circuit data
  const getCircuitReference = (): any => {
    if (!circuitData?.components) return null;

    return circuitData.components.find(
      (c: any) => c.name === bomItem.component.name || c.value?.includes(bomItem.component.name)
    );
  };

  // Get PCB position information
  const getPositionInfo = (): any => {
    if (!bomItem.position) return null;

    return {
      x: bomItem.position.x?.toFixed(1),
      y: bomItem.position.y?.toFixed(1),
      layer: bomItem.position.z ? 'Top' : 'Bottom',
    };
  };

  const circuitRef = getCircuitReference();
  const positionInfo = getPositionInfo();

  return (
    <div
      style={{
        background: 'rgba(99, 102, 241, 0.05)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        borderRadius: '8px',
        padding: '10px',
        marginTop: '8px',
        fontSize: '11px',
      }}
    >
      {/* Header */}
      <div style={{ fontWeight: '600', color: '#4F46E5', marginBottom: '8px' }}>
        🔗 Design References
      </div>

      {/* Circuit Reference */}
      {circuitRef && (
        <div
          style={{
            background: 'rgba(59, 130, 246, 0.05)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: '6px',
            padding: '8px',
            marginBottom: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
            e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
            e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.2)';
          }}
          onClick={() => {
            setShowCircuitRef(!showCircuitRef);
            onHighlight?.(circuitRef.id || circuitRef.name);
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>
              📋 <strong>Circuit Reference:</strong> {circuitRef.id || circuitRef.ref || 'U1'}
            </span>
            <span style={{ color: '#64748B', fontSize: '10px' }}>
              {showCircuitRef ? '▼' : '▶'}
            </span>
          </div>

          {showCircuitRef && (
            <div style={{ marginTop: '6px', fontSize: '10px', color: '#64748B' }}>
              <div>Value: {circuitRef.value || '—'}</div>
              {circuitRef.pins && (
                <div style={{ marginTop: '4px' }}>
                  <strong>Pins:</strong>
                  <div style={{ marginLeft: '12px', marginTop: '2px' }}>
                    {Object.entries(circuitRef.pins || {})
                      .slice(0, 4)
                      .map(([pin, signal]: any) => (
                        <div key={pin}>
                          {pin} → {signal}
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* PCB Position */}
      {positionInfo && (
        <div
          style={{
            background: 'rgba(6, 182, 212, 0.05)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '6px',
            padding: '8px',
            marginBottom: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(6, 182, 212, 0.1)';
            e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(6, 182, 212, 0.05)';
            e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.2)';
          }}
          onClick={() => setShowPosition(!showPosition)}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>
              📍 <strong>PCB Position:</strong> ({positionInfo.x}, {positionInfo.y}) mm
            </span>
            <span style={{ color: '#64748B', fontSize: '10px' }}>
              {showPosition ? '▼' : '▶'}
            </span>
          </div>

          {showPosition && (
            <div style={{ marginTop: '6px', fontSize: '10px', color: '#64748B' }}>
              <div>X: {positionInfo.x} mm</div>
              <div>Y: {positionInfo.y} mm</div>
              <div>Layer: {positionInfo.layer}</div>
              <button
                style={{
                  marginTop: '6px',
                  background: 'rgba(6, 182, 212, 0.1)',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  color: '#0E7490',
                  padding: '4px 8px',
                  borderRadius: '3px',
                  fontSize: '9px',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                View in CAD ↗
              </button>
            </div>
          )}
        </div>
      )}

      {/* Design Integration Note */}
      {!circuitRef && !positionInfo && (
        <div style={{ color: '#94A3B8', fontSize: '10px', fontStyle: 'italic' }}>
          ℹ Design reference data not available
        </div>
      )}
    </div>
  );
};
