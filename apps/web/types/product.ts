/**
 * Product Sourcing Type Definitions
 */

export interface ProductSpec {
  id: string;
  component: string;
  product_name: string;
  seller: string;
  price: number;
  currency: string;
  availability: boolean;
  url: string;
  image?: string;
  match_score: number;  // 0-100
  specifications: Record<string, any>;
  in_stock_qty?: number;
  last_updated?: string;
}

export interface ProductMatch {
  bom_item_id: string;
  product: ProductSpec;
  match_score: number;
  reasons: string[];
}

export interface ProductSearchResult {
  requirement: ComponentRequirement;
  search_query: SearchQuery;
  products: ProductSpec[];
  total_found: number;
  matching_count: number;
}

export interface ProductSubstitution {
  original: ProductSpec;
  substitute: ProductSpec;
  compatibility_score: number;  // 0-100
  compatibility_notes: string;
  missing_features: string[];
  extra_features: string[];
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
