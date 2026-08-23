import type { BusinessAnalysis, Scenario, PricingSimulatorResult, BreakEvenAnalysis } from '../types/business';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

interface AnalyzeBusinessRequest {
  project_id: string;
  invention_prompt: string;
  target_msrp?: number;
  target_annual_volume?: number;
}

interface ScenarioRequest {
  project_id: string;
  scenario: Scenario;
}

interface OptimizeRequest {
  project_id: string;
  optimization_type: 'cost' | 'supplier' | 'lead_time';
}

export const businessApi = {
  /**
   * Stream business analysis for a project
   * Uses Server-Sent Events for long-running analysis
   */
  async analyzeBusiness(
    request: AnalyzeBusinessRequest,
    onProgress?: (status: string) => void
  ): Promise<BusinessAnalysis> {
    const response = await fetch(`${API_BASE}/business/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Business analysis failed: ${response.statusText}`);
    }

    // Parse SSE stream
    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    let analysis: BusinessAnalysis | null = null;
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();

          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6);
              const data = JSON.parse(jsonStr);

              if (data.status && onProgress) {
                onProgress(data.status);
              }

              if (data.bom_summary) {
                analysis = data;
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }

        buffer = lines[lines.length - 1];
      }

      buffer += decoder.decode();
      if (buffer.trim().startsWith('data: ')) {
        try {
          const jsonStr = buffer.slice(6).trim();
          analysis = JSON.parse(jsonStr);
        } catch (e) {
          // Last parse attempt
        }
      }
    } finally {
      reader.releaseLock();
    }

    if (!analysis) {
      throw new Error('No valid analysis received from server');
    }

    return analysis;
  },

  /**
   * Get BOM data for a project
   */
  async getBOM(projectId: string): Promise<BusinessAnalysis['itemized_bom']> {
    const response = await fetch(`${API_BASE}/business/${projectId}/bom`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch BOM: ${response.statusText}`);
    }

    const data = await response.json();
    return data.itemized_bom || [];
  },

  /**
   * Get supplier information for a project
   */
  async getSuppliers(projectId: string) {
    const response = await fetch(`${API_BASE}/business/${projectId}/suppliers`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch suppliers: ${response.statusText}`);
    }

    const data = await response.json();
    return data.suppliers || [];
  },

  /**
   * Get market sizing data
   */
  async getMarketSizing(projectId: string) {
    const response = await fetch(`${API_BASE}/business/${projectId}/market`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch market sizing: ${response.statusText}`);
    }

    const data = await response.json();
    return data.market_sizing || null;
  },

  /**
   * Get financial projections
   */
  async getProjections(projectId: string) {
    const response = await fetch(`${API_BASE}/business/${projectId}/projections`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch projections: ${response.statusText}`);
    }

    const data = await response.json();
    return data.projections || null;
  },

  /**
   * Analyze a pricing scenario
   */
  async analyzeScenario(request: ScenarioRequest): Promise<Scenario> {
    const response = await fetch(`${API_BASE}/business/scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Scenario analysis failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.scenario || request.scenario;
  },

  /**
   * Get cost optimization suggestions
   */
  async getOptimizations(request: OptimizeRequest) {
    const response = await fetch(`${API_BASE}/business/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Optimization analysis failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.opportunities || [];
  },

  /**
   * Generate and download business report
   */
  async generateReport(projectId: string) {
    const response = await fetch(`${API_BASE}/business/${projectId}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Report generation failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.report_url || null;
  },

  /**
   * Local calculation: Pricing simulator
   * No API call needed — all client-side
   */
  calculatePricing(
    unitCost: number,
    msrp: number,
    annualVolume: number
  ): PricingSimulatorResult {
    const grossProfit = msrp - unitCost;
    const grossMarginPercentage = msrp > 0 ? (grossProfit / msrp) * 100 : 0;
    const annualRevenue = msrp * annualVolume;
    const annualGrossProfit = grossProfit * annualVolume;

    return {
      msrp,
      unitCost,
      grossProfit,
      grossMarginPercentage,
      annualRevenue,
      annualGrossProfit,
    };
  },

  /**
   * Local calculation: Recommended MSRP from target margin
   */
  calculateRecommendedMSRP(unitCost: number, targetMargin: number): number {
    if (targetMargin >= 1) {
      return unitCost * 2; // Fallback if invalid margin
    }
    return unitCost / (1 - targetMargin);
  },

  /**
   * Local calculation: Break-even analysis
   */
  calculateBreakEven(
    fixedCosts: number,
    unitSellingPrice: number,
    unitVariableCost: number
  ): BreakEvenAnalysis {
    const contributionMargin = unitSellingPrice - unitVariableCost;
    const breakEvenUnits =
      contributionMargin > 0 ? Math.ceil(fixedCosts / contributionMargin) : 0;
    const breakEvenRevenue = breakEvenUnits * unitSellingPrice;

    return {
      fixed_costs_usd: fixedCosts,
      unit_selling_price: unitSellingPrice,
      unit_variable_cost: unitVariableCost,
      contribution_margin: contributionMargin,
      breakeven_units: breakEvenUnits,
      breakeven_revenue: breakEvenRevenue,
    };
  },

  /**
   * Local calculation: What-if scenarios
   */
  calculateWhatIf(
    baseAnalysis: BusinessAnalysis,
    adjustments: {
      componentCostDelta: number;
      msrpDelta: number;
      volumeDelta: number;
      laborCostDelta: number;
    }
  ) {
    const baseCOGS = baseAnalysis.bom_summary.total_unit_cost_usd;
    const baseMSRP = baseAnalysis.bom_summary.target_msrp_usd;
    const baseVolume = 500; // Assumption if not available

    const adjustedCOGS = baseCOGS * (1 + adjustments.componentCostDelta / 100);
    const adjustedMSRP = baseMSRP * (1 + adjustments.msrpDelta / 100);
    const adjustedVolume = baseVolume * (1 + adjustments.volumeDelta / 100);

    const result = this.calculatePricing(adjustedCOGS, adjustedMSRP, adjustedVolume);

    return {
      ...result,
      baseCOGS,
      baseMSRP,
      baseVolume,
      adjustedCOGS,
      adjustedMSRP,
      adjustedVolume,
    };
  },

  /**
   * Local calculation: Sensitivity heatmap grid
   * Generate matrix of margin % for different MSRP and COGS combinations
   */
  generateSensitivityGrid(baseMSRP: number, baseCOGS: number) {
    const msrpRange = [];
    const cogsRange = [];
    const margins: number[][] = [];

    // MSRP range: ±30% of base
    for (let i = -30; i <= 30; i += 5) {
      msrpRange.push(baseMSRP * (1 + i / 100));
    }

    // COGS range: ±30% of base
    for (let i = -30; i <= 30; i += 5) {
      cogsRange.push(baseCOGS * (1 + i / 100));
    }

    // Calculate margins
    for (let i = 0; i < cogsRange.length; i++) {
      const row: number[] = [];
      for (let j = 0; j < msrpRange.length; j++) {
        const margin =
          msrpRange[j] > 0
            ? ((msrpRange[j] - cogsRange[i]) / msrpRange[j]) * 100
            : 0;
        row.push(Math.max(0, Math.min(100, margin))); // Clamp 0-100
      }
      margins.push(row);
    }

    return {
      msrpRange: msrpRange.map((v) => Math.round(v)),
      cogsRange: cogsRange.map((v) => Math.round(v)),
      margins,
    };
  },
};
