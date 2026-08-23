/**
 * BOM (Bill of Materials) Type Definitions
 */

export interface ComponentSpec {
  category: string;
  name: string;
  variant?: string;
  voltage?: string;
  interface?: string[];
  package?: string;
  quantity: number;
  is_required: boolean;
  description?: string;
  specs: Record<string, any>;
}

export interface BOMItem {
  id: string;
  component: ComponentSpec;
  design_ref?: string;
  pin_mapping?: Record<string, string>;
  position?: {
    x: number;
    y: number;
    z?: number;
  };
  notes?: string;
}

export interface BOM {
  project_id: string;
  design_id: string;
  timestamp: string;
  items: BOMItem[];
  total_components: number;
  required_count: number;
  optional_count: number;
  estimated_cost?: number;
  cost_currency: string;
}

export interface ComponentRequirement {
  category: string;
  name: string;
  variant?: string;
  voltage?: string;
  interface?: string[];
  package?: string;
  specs: Record<string, any>;
}

export interface SearchQuery {
  base_query: string;
  enhanced_query: string;
  filters: Record<string, any>;
}
