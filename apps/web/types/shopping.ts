/**
 * Shopping List Type Definitions
 */

export interface ShoppingItem {
  bom_item_id: string;
  component_name: string;
  quantity: number;
  product_id: string;
  product_name: string;
  seller: string;
  price: number;
  total_price: number;
  match_score: number;
  availability: boolean;
  url: string;
  is_required: boolean;
  already_have: boolean;
}

export interface ShoppingList {
  project_id: string;
  design_id: string;
  timestamp: string;
  items: ShoppingItem[];
  subtotal: number;
  estimated_shipping: number;
  estimated_total: number;
  currency: string;
  seller_count: number;
  availability_status: string;
  optimization_applied: string;
}

export interface OptimizationResult {
  original_cost: number;
  optimized_cost: number;
  savings: number;
  savings_percent: number;
  changes: string[];
  seller_consolidation: number;
}

export interface OptimizationOption {
  type: 'cost' | 'delivery' | 'compatibility' | 'best_overall';
  label: string;
  description: string;
  icon: string;
}

export type OptimizationType = 'cost' | 'delivery' | 'compatibility' | 'base';
