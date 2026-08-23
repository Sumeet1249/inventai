// Business Analysis Types
export interface BOMItem {
  ref?: string;
  category?: string;
  component_name: string;
  part_number?: string;
  quantity: number;
  unit_cost_usd: number;
  extended_cost_usd: number;
  supplier?: string;
  data_source?: 'Live API' | 'Cache' | 'Historical' | 'Estimated' | 'Fallback';
  price_confidence?: number; // 0-1
  availability_status?: 'available' | 'limited' | 'discontinued';
  lead_time_days?: number;
  alternatives?: BOMItem[];
  risk_level?: 'low' | 'medium' | 'high';
}

export interface BOMSummary {
  total_hardware_cogs_usd: number;
  assembly_labor_overhead_usd: number;
  total_unit_cost_usd: number;
  target_msrp_usd: number;
  unit_gross_profit_usd: number;
  gross_margin_percentage: number;
  component_count?: number;
  supplier_count?: number;
}

export interface CostBreakdown {
  hardware_cogs: number;
  assembly_labor: number;
  manufacturing_overhead: number;
  packaging: number;
  testing_qa: number;
  shipping_allowance: number;
  warranty_reserve: number;
  total_unit_cost: number;
}

export interface MarketSizing {
  tam_usd: number; // Total Addressable Market
  sam_usd: number; // Serviceable Available Market
  som_usd: number; // Serviceable Obtainable Market
  target_market?: string;
  customer_segments?: string[];
  methodology?: string;
  assumptions?: string;
  confidence?: number; // 0-100
}

export interface FinancialYear {
  year: number;
  units_sold: number;
  revenue_usd: number;
  cogs_usd: number;
  gross_profit_usd: number;
  gross_margin_percentage: number;
}

export interface FinancialProjection {
  year_1: FinancialYear;
  year_2: FinancialYear;
  year_3: FinancialYear;
}

export interface Scenario {
  name: string;
  units_sold: number;
  msrp_usd: number;
  unit_cogs_reduction_percent: number;
  revenue_usd?: number;
  gross_profit_usd?: number;
  gross_margin_percentage?: number;
}

export interface SupplierInfo {
  name: string;
  component_count: number;
  spend_usd: number;
  availability?: string;
  lead_time_days?: number;
  risk_level?: string;
  concentration_percentage?: number;
}

export interface RiskAlert {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  title: string;
  description: string;
  type: 'cost' | 'supplier' | 'component' | 'availability' | 'lead_time' | 'concentration';
  relatedComponentRef?: string;
  actionable: boolean;
}

export interface BusinessAnalysis {
  status: 'success' | 'partial' | 'error';
  project_id: string;

  bom_summary: BOMSummary;
  itemized_bom: BOMItem[];
  cost_breakdown?: CostBreakdown;

  market_sizing: MarketSizing;
  financial_projections_3yr: FinancialProjection;

  supplier_analysis?: SupplierInfo[];
  risk_alerts?: RiskAlert[];
  bom_health_score?: number; // 0-100

  cost_concentration?: {
    top_components: Array<{ ref?: string; component: string; cost: number; percentage: number }>;
    top_5_percentage: number;
  };

  optimization_opportunities?: Array<{
    current_component: string;
    current_cost: number;
    alternative_component?: string;
    alternative_cost?: number;
    potential_savings_per_unit?: number;
    annual_savings?: number;
    trade_offs?: string;
  }>;

  export_files?: {
    bom_csv_url?: string;
    financial_proforma_excel_url?: string;
    business_report_pdf_url?: string;
    cost_analysis_url?: string;
  };

  metadata?: {
    generated_at: string;
    data_source: string;
    fallback_pricing_used: boolean;
    api_response_time_ms: number;
  };
}

export interface BusinessAnalyticsState {
  loading: boolean;
  error: string | null;

  analysis: BusinessAnalysis | null;

  selectedScenario: 'conservative' | 'base' | 'aggressive' | 'custom';
  scenarios: Record<string, Scenario>;

  pricing: {
    msrp: number;
    targetMargin: number; // 0-1
  };

  filters: {
    category?: string;
    supplier?: string;
    risk?: string;
    source?: string;
    search?: string;
  };

  sort: {
    field: 'unit_cost' | 'extended_cost' | 'quantity' | 'risk' | 'confidence';
    direction: 'asc' | 'desc';
  };

  whatIfAdjustments: {
    componentCostDelta: number; // percentage
    msrpDelta: number; // percentage
    volumeDelta: number; // percentage
    laborCostDelta: number; // percentage
  };
}

export interface PricingSimulatorResult {
  msrp: number;
  unitCost: number;
  grossProfit: number;
  grossMarginPercentage: number;
  annualRevenue: number;
  annualGrossProfit: number;
}

export interface BreakEvenAnalysis {
  fixed_costs_usd: number;
  unit_selling_price: number;
  unit_variable_cost: number;
  contribution_margin: number;
  breakeven_units: number;
  breakeven_revenue: number;
}
