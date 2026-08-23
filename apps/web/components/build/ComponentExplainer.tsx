'use client';

import React, { useState } from 'react';

interface ComponentExplainerProps {
  bomItem: any;
  onSubstitute?: () => void;
}

export const ComponentExplainer: React.FC<ComponentExplainerProps> = ({ bomItem, onSubstitute }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [substitutions, setSubstitutions] = useState<any>(null);
  const [loadingSubstitutions, setLoadingSubstitutions] = useState(false);

  const getWhyNeeded = (component: any): string => {
    const componentType = component.category;

    const explanations: Record<string, string> = {
      MCU: `The main microcontroller that runs your embedded software. Controls all other components and processes sensor data in real-time.`,
      Sensor: `Measures environmental or physical parameters. Essential for your design's input and feedback systems.`,
      Display: `Shows output information to users. Provides visual feedback and enables interactive control.`,
      Power: `Manages and distributes electrical power safely. Ensures stable voltage supply to all components.`,
      Resistor: `Limits current flow and protects components. Prevents damage from overcurrent and ensures proper signal levels.`,
      Capacitor: `Stores electrical charge temporarily. Filters noise, stabilizes voltage, and enables timing functions.`,
      Connector: `Allows physical and electrical connections. Enables component integration and troubleshooting.`,
    };

    return explanations[componentType] || `Necessary component for your ${componentType.toLowerCase()} subsystem.`;
  };

  const searchSubstitutions = async () => {
    setLoadingSubstitutions(true);
    try {
      const res = await fetch('/api/substitutions/find', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          component_name: bomItem.component.name,
          component_specs: {
            voltage: bomItem.component.voltage,
            interface: bomItem.component.interface,
            package: bomItem.component.package,
          },
          reason: 'availability',
          max_suggestions: 3,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setSubstitutions(data);
      }
    } catch (err) {
      console.error('Failed to fetch substitutions:', err);
    } finally {
      setLoadingSubstitutions(false);
    }
  };

  return (
    <div
      style={{
        background: 'rgba(255, 255, 255, 0.5)',
        border: '1px solid rgba(147, 197, 253, 0.3)',
        borderRadius: '10px',
        padding: '14px',
        backdropFilter: 'blur(10px)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'start',
          marginBottom: '10px',
        }}
      >
        <div>
          <div style={{ fontSize: '12px', fontWeight: '600', color: '#0F172A' }}>
            {bomItem.component.name}
          </div>
          <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '2px' }}>
            {bomItem.component.category} • Qty: {bomItem.component.quantity}
          </div>
        </div>

        <button
          onClick={() => setShowDetails(!showDetails)}
          style={{
            background: 'none',
            border: 'none',
            color: '#2563EB',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: '600',
            textDecoration: 'underline',
          }}
        >
          {showDetails ? 'Hide' : 'Why?'}
        </button>
      </div>

      {/* Explanation */}
      {showDetails && (
        <div
          style={{
            background: 'rgba(37, 99, 235, 0.05)',
            border: '1px solid rgba(37, 99, 235, 0.2)',
            borderRadius: '6px',
            padding: '10px 12px',
            marginBottom: '10px',
            fontSize: '11px',
            color: '#334155',
            lineHeight: '1.5',
          }}
        >
          <span style={{ fontWeight: '600', color: '#1D4ED8' }}>💡 Why you need this:</span>
          <div style={{ marginTop: '4px' }}>{getWhyNeeded(bomItem.component)}</div>

          {/* Specs */}
          {(bomItem.component.voltage || bomItem.component.interface) && (
            <div style={{ marginTop: '8px', fontSize: '10px', color: '#64748B' }}>
              <span style={{ fontWeight: '600' }}>Specs:</span>
              {bomItem.component.voltage && ` ${bomItem.component.voltage}`}
              {bomItem.component.interface && ` • ${bomItem.component.interface.join(', ')}`}
            </div>
          )}

          {/* Substitute Option */}
          {!substitutions && (
            <button
              onClick={searchSubstitutions}
              disabled={loadingSubstitutions}
              style={{
                marginTop: '10px',
                background: 'rgba(37, 99, 235, 0.1)',
                border: '1px solid rgba(37, 99, 235, 0.3)',
                color: '#1D4ED8',
                padding: '6px 10px',
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: '600',
                cursor: loadingSubstitutions ? 'not-allowed' : 'pointer',
                opacity: loadingSubstitutions ? 0.6 : 1,
              }}
            >
              {loadingSubstitutions ? '⟳ Finding alternatives...' : '🔄 Find alternatives'}
            </button>
          )}
        </div>
      )}

      {/* Substitutions */}
      {substitutions && (
        <div style={{ marginTop: '10px', borderTop: '1px solid rgba(147, 197, 253, 0.2)', paddingTop: '10px' }}>
          <div style={{ fontSize: '10px', fontWeight: '700', color: '#0F172A', marginBottom: '8px' }}>
            ⚡ Compatible Alternatives:
          </div>

          {substitutions.alternatives?.slice(0, 2).map((alt: any, i: number) => (
            <div
              key={i}
              style={{
                background: alt.can_substitute
                  ? 'rgba(34, 197, 94, 0.05)'
                  : 'rgba(220, 38, 38, 0.05)',
                border: alt.can_substitute
                  ? '1px solid rgba(34, 197, 94, 0.2)'
                  : '1px solid rgba(220, 38, 38, 0.2)',
                borderRadius: '6px',
                padding: '8px',
                marginBottom: '6px',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '4px',
                }}
              >
                <div style={{ fontSize: '10px', fontWeight: '600', color: '#0F172A' }}>
                  {alt.substitute_component}
                </div>
                <div
                  style={{
                    fontSize: '9px',
                    fontWeight: '700',
                    color: alt.compatibility_score >= 90 ? '#15803D' : '#F59E0B',
                  }}
                >
                  {alt.compatibility_score.toFixed(0)}% match
                </div>
              </div>

              {alt.missing_features?.length > 0 && (
                <div style={{ fontSize: '9px', color: '#DC2626', marginTop: '2px' }}>
                  Missing: {alt.missing_features.join(', ')}
                </div>
              )}

              <div style={{ fontSize: '9px', color: '#64748B', marginTop: '2px' }}>
                {alt.impact_level === 'low' && '✓ Drop-in replacement'}
                {alt.impact_level === 'medium' && '⚠ Minor changes needed'}
                {alt.impact_level === 'high' && '✕ Significant redesign'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
