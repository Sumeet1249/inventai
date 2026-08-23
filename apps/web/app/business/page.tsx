'use client';

import { useState, useEffect } from 'react';
import { businessApi } from '../../services/businessApi';
import type { BusinessAnalysis } from '../../types/business';

// Components
import { KPICards } from '../../components/business/KPICards';
import { BOMTable } from '../../components/business/BOMTable';
import { CostBreakdownChart, CostConcentration } from '../../components/business/CostAnalysis';
import { PricingSimulator } from '../../components/business/PricingSimulator';
import { BreakEvenAnalysis } from '../../components/business/BreakEvenAnalysis';
import { FinancialProjections, ScenarioSimulator } from '../../components/business/FinancialProjections';
import {
  SensitivityHeatmap,
  MarketSizingVisualization,
  SupplierAnalysis,
  RiskAlerts,
  ExportCenter,
} from '../../components/business/AdvancedAnalytics';

interface LoadingStep {
  label: string;
  completed: boolean;
}

export default function BusinessPage() {
  const [analysis, setAnalysis] = useState<BusinessAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingSteps, setLoadingSteps] = useState<LoadingStep[]>([
    { label: 'Extracting components from CAD', completed: false },
    { label: 'Resolving BOM from component database', completed: false },
    { label: 'Fetching supplier prices', completed: false },
    { label: 'Calculating financial model', completed: false },
    { label: 'Analyzing market opportunity', completed: false },
    { label: 'Generating reports', completed: false },
  ]);

  const annualVolume = 500; // Default assumption

  // Auto-trigger analysis on mount if project context available
  useEffect(() => {
    const triggerAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        // Mock project data — in real app this comes from project context
        const mockAnalysis = await businessApi.analyzeBusiness(
          {
            project_id: 'demo-project',
            invention_prompt: 'Foldable quadcopter for bridge inspection',
            target_msrp: 12000,
            target_annual_volume: annualVolume,
          },
          (status) => {
            // Update loading steps based on status
            const steps = [...loadingSteps];
            if (status.includes('component')) steps[0].completed = true;
            if (status.includes('BOM') || status.includes('component')) steps[1].completed = true;
            if (status.includes('price') || status.includes('supplier')) steps[2].completed = true;
            if (status.includes('financial')) steps[3].completed = true;
            if (status.includes('market')) steps[4].completed = true;
            if (status.includes('report')) steps[5].completed = true;
            setLoadingSteps(steps);
          }
        );

        setAnalysis(mockAnalysis);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Analysis failed');
      } finally {
        setLoading(false);
      }
    };

    // Uncomment to auto-trigger on mount
    // triggerAnalysis();
  }, []);

  // Retry handler
  const handleRetry = async () => {
    try {
      setLoading(true);
      setError(null);
      setLoadingSteps(loadingSteps.map((s) => ({ ...s, completed: false })));

      const mockAnalysis = await businessApi.analyzeBusiness(
        {
          project_id: 'demo-project',
          invention_prompt: 'Foldable quadcopter for bridge inspection',
          target_msrp: 12000,
          target_annual_volume: annualVolume,
        },
        (status) => {
          const steps = [...loadingSteps];
          if (status.includes('component')) steps[0].completed = true;
          if (status.includes('BOM')) steps[1].completed = true;
          if (status.includes('price')) steps[2].completed = true;
          if (status.includes('financial')) steps[3].completed = true;
          if (status.includes('market')) steps[4].completed = true;
          if (status.includes('report')) steps[5].completed = true;
          setLoadingSteps(steps);
        }
      );

      setAnalysis(mockAnalysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // ── LOADING STATE ──
  if (loading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: '#F8FAFC',
          padding: '40px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            background: '#fff',
            borderRadius: '16px',
            padding: '40px',
            maxWidth: '500px',
            width: '100%',
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                border: '3px solid #E2E8F0',
                borderTop: '3px solid #2563EB',
                borderRadius: '50%',
                animation: 'spin 0.7s linear infinite',
              }}
            />
          </div>

          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', textAlign: 'center', margin: '0 0 24px 0' }}>
            Analyzing Business Opportunity
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {loadingSteps.map((step, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '13px' }}>
                <div
                  style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: step.completed ? '#10B981' : '#E2E8F0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: step.completed ? '#fff' : '#94A3B8',
                    fontWeight: '700',
                    fontSize: '11px',
                    flexShrink: 0,
                  }}
                >
                  {step.completed ? '✓' : idx + 1}
                </div>
                <span style={{ color: step.completed ? '#10B981' : '#64748B', fontWeight: step.completed ? '600' : '500' }}>
                  {step.label}
                </span>
              </div>
            ))}
          </div>

          <style>{`
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    );
  }

  // ── ERROR STATE ──
  if (error) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: '#F8FAFC',
          padding: '40px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            background: '#fff',
            borderRadius: '16px',
            padding: '40px',
            maxWidth: '500px',
            width: '100%',
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          }}
        >
          <div style={{ fontSize: '40px', marginBottom: '16px' }}>⚠️</div>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
            Analysis Failed
          </h2>
          <p style={{ fontSize: '13px', color: '#64748B', margin: '0 0 24px 0', lineHeight: '1.5' }}>
            {error}
          </p>
          <button
            onClick={handleRetry}
            style={{
              width: '100%',
              padding: '10px 16px',
              background: '#2563EB',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#1D4ED8';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#2563EB';
            }}
          >
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  // ── EMPTY STATE ──
  if (!analysis) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: '#F8FAFC',
          padding: '40px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            background: '#fff',
            borderRadius: '16px',
            padding: '40px',
            maxWidth: '500px',
            width: '100%',
            textAlign: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>💼</div>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', margin: '0 0 12px 0' }}>
            No Business Analysis Yet
          </h2>
          <p style={{ fontSize: '13px', color: '#64748B', margin: '0 0 24px 0', lineHeight: '1.5' }}>
            Run Business Analysis to extract the BOM, estimate component costs, analyze pricing, and generate financial projections.
          </p>
          <button
            onClick={handleRetry}
            style={{
              padding: '10px 24px',
              background: '#2563EB',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#1D4ED8';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#2563EB';
            }}
          >
            Analyze Project
          </button>
        </div>
      </div>
    );
  }

  // ── MAIN DASHBOARD ──
  return (
    <div style={{ minHeight: '100vh', background: '#F8FAFC', padding: '32px 24px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0F172A', margin: '0 0 6px 0' }}>
            Business & Analytics
          </h1>
          <p style={{ fontSize: '14px', color: '#64748B', margin: 0 }}>
            Turn engineering specifications into actionable cost, pricing, market and profitability intelligence.
          </p>
        </div>

        {/* KPI Cards */}
        <KPICards
          bomSummary={analysis.bom_summary}
          annualVolume={annualVolume}
          bomHealthScore={analysis.bom_health_score}
        />

        {/* Risk Alerts */}
        {analysis.risk_alerts && analysis.risk_alerts.length > 0 && (
          <RiskAlerts alerts={analysis.risk_alerts} />
        )}

        {/* Cost Analysis Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px', marginBottom: '24px' }}>
          <CostBreakdownChart breakdown={analysis.cost_breakdown} />
          <CostConcentration items={analysis.itemized_bom} />
        </div>

        {/* Pricing & Break-Even */}
        <PricingSimulator
          unitCost={analysis.bom_summary.total_unit_cost_usd}
          targetMSRP={analysis.bom_summary.target_msrp_usd}
          annualVolume={annualVolume}
        />

        <BreakEvenAnalysis
          unitCost={analysis.bom_summary.total_unit_cost_usd}
          msrp={analysis.bom_summary.target_msrp_usd}
        />

        {/* Market & Financial */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px', marginBottom: '24px' }}>
          <MarketSizingVisualization market={analysis.market_sizing} />
          <SupplierAnalysis suppliers={analysis.supplier_analysis} />
        </div>

        {/* Financial Projections & Scenarios */}
        <FinancialProjections
          projections={analysis.financial_projections_3yr}
          unitCost={analysis.bom_summary.total_unit_cost_usd}
          msrp={analysis.bom_summary.target_msrp_usd}
        />

        <ScenarioSimulator
          baseAnalysis={{
            unitCost: analysis.bom_summary.total_unit_cost_usd,
            msrp: analysis.bom_summary.target_msrp_usd,
          }}
        />

        {/* Sensitivity Analysis */}
        <SensitivityHeatmap
          msrp={analysis.bom_summary.target_msrp_usd}
          unitCost={analysis.bom_summary.total_unit_cost_usd}
        />

        {/* BOM Table */}
        <div
          style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '24px',
          }}
        >
          <BOMTable items={analysis.itemized_bom} />
        </div>

        {/* Exports */}
        <ExportCenter projectId="demo-project" exportFiles={analysis.export_files} />
      </div>
    </div>
  );
}
