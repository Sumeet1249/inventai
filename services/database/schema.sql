-- ============================================================================
-- DATABASE SCHEMA FOR BOM & PRODUCT SOURCING
-- ============================================================================

-- Projects table (reference)
CREATE TABLE IF NOT EXISTS projects (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================================
-- BOM TABLES
-- ============================================================================

-- BOM (Bill of Materials) records
CREATE TABLE IF NOT EXISTS boms (
  id VARCHAR(255) PRIMARY KEY,
  project_id VARCHAR(255) NOT NULL,
  design_id VARCHAR(255) NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  total_components INT NOT NULL DEFAULT 0,
  required_count INT NOT NULL DEFAULT 0,
  optional_count INT NOT NULL DEFAULT 0,
  estimated_cost DECIMAL(12, 2),
  cost_currency VARCHAR(10) DEFAULT 'INR',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  INDEX idx_project_id (project_id),
  INDEX idx_design_id (design_id)
);

-- BOM Items (individual components in BOM)
CREATE TABLE IF NOT EXISTS bom_items (
  id VARCHAR(255) PRIMARY KEY,
  bom_id VARCHAR(255) NOT NULL,
  component_name VARCHAR(255) NOT NULL,
  component_category VARCHAR(100) NOT NULL,
  component_variant VARCHAR(255),
  voltage VARCHAR(50),
  interface VARCHAR(255),  -- JSON: ["I2C", "SPI"]
  package_type VARCHAR(100),
  quantity INT NOT NULL DEFAULT 1,
  is_required BOOLEAN NOT NULL DEFAULT TRUE,
  description TEXT,
  specs JSON,  -- Detailed specifications
  design_ref VARCHAR(255),  -- Reference in circuit/PCB
  pin_mapping JSON,  -- Pin configuration if applicable
  position_x DECIMAL(10, 3),  -- PCB position
  position_y DECIMAL(10, 3),
  position_z DECIMAL(10, 3),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (bom_id) REFERENCES boms(id) ON DELETE CASCADE,
  INDEX idx_bom_id (bom_id),
  INDEX idx_category (component_category)
);

-- ============================================================================
-- PRODUCT TABLES
-- ============================================================================

-- Product sources (sellers)
CREATE TABLE IF NOT EXISTS product_sources (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) UNIQUE NOT NULL,  -- "Robu", "Amazon", "Flipkart"
  url VARCHAR(255) NOT NULL,
  api_endpoint VARCHAR(255),
  enabled BOOLEAN DEFAULT TRUE,
  priority INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products (actual product listings)
CREATE TABLE IF NOT EXISTS products (
  id VARCHAR(255) PRIMARY KEY,
  source_id INT NOT NULL,
  component_id VARCHAR(255),  -- Link to component if applicable
  product_name VARCHAR(255) NOT NULL,
  product_url VARCHAR(500) NOT NULL,
  product_sku VARCHAR(100),
  image_url VARCHAR(500),
  price DECIMAL(12, 2) NOT NULL,
  currency VARCHAR(10) DEFAULT 'INR',
  availability BOOLEAN DEFAULT TRUE,
  in_stock_qty INT,
  specifications JSON,  -- {"voltage": "3.3V", "interface": ["I2C"]}
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (source_id) REFERENCES product_sources(id),
  INDEX idx_source_id (source_id),
  INDEX idx_product_name (product_name),
  INDEX idx_sku (product_sku)
);

-- Product matches (scoring between BOM items and products)
CREATE TABLE IF NOT EXISTS product_matches (
  id INT PRIMARY KEY AUTO_INCREMENT,
  bom_item_id VARCHAR(255) NOT NULL,
  product_id VARCHAR(255) NOT NULL,
  match_score DECIMAL(5, 2) NOT NULL,  -- 0-100
  name_match DECIMAL(5, 2),
  spec_match DECIMAL(5, 2),
  voltage_match DECIMAL(5, 2),
  interface_match DECIMAL(5, 2),
  availability_match DECIMAL(5, 2),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (bom_item_id) REFERENCES bom_items(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  UNIQUE KEY unique_match (bom_item_id, product_id),
  INDEX idx_bom_item_id (bom_item_id),
  INDEX idx_product_id (product_id),
  INDEX idx_match_score (match_score)
);

-- ============================================================================
-- CACHING & OPTIMIZATION
-- ============================================================================

-- Product search cache (avoid repeated searches)
CREATE TABLE IF NOT EXISTS product_search_cache (
  id INT PRIMARY KEY AUTO_INCREMENT,
  query_hash VARCHAR(64) UNIQUE NOT NULL,  -- MD5 hash of search query
  query TEXT NOT NULL,
  results JSON,  -- Cached search results
  result_count INT,
  hit_count INT DEFAULT 0,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_query_hash (query_hash),
  INDEX idx_expires_at (expires_at)
);

-- Shopping lists generated for users
CREATE TABLE IF NOT EXISTS shopping_lists (
  id VARCHAR(255) PRIMARY KEY,
  project_id VARCHAR(255) NOT NULL,
  design_id VARCHAR(255) NOT NULL,
  user_id VARCHAR(255),  -- Optional: if user auth is added
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  subtotal DECIMAL(12, 2),
  estimated_shipping DECIMAL(12, 2),
  estimated_total DECIMAL(12, 2),
  currency VARCHAR(10) DEFAULT 'INR',
  seller_count INT,
  availability_status VARCHAR(100),
  optimization_type VARCHAR(50),  -- "cost", "delivery", "compatibility"
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  INDEX idx_project_id (project_id),
  INDEX idx_user_id (user_id)
);

-- Shopping list items
CREATE TABLE IF NOT EXISTS shopping_list_items (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shopping_list_id VARCHAR(255) NOT NULL,
  bom_item_id VARCHAR(255) NOT NULL,
  product_id VARCHAR(255) NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  price DECIMAL(12, 2) NOT NULL,
  total_price DECIMAL(12, 2) NOT NULL,
  seller VARCHAR(100),
  is_selected BOOLEAN DEFAULT TRUE,
  already_have BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE,
  FOREIGN KEY (bom_item_id) REFERENCES bom_items(id),
  FOREIGN KEY (product_id) REFERENCES products(id),
  INDEX idx_shopping_list_id (shopping_list_id)
);

-- Component substitutions (alternatives)
CREATE TABLE IF NOT EXISTS component_substitutions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  original_component_id VARCHAR(255) NOT NULL,
  substitute_component_id VARCHAR(255) NOT NULL,
  compatibility_score DECIMAL(5, 2),  -- 0-100 compatibility percentage
  compatibility_notes TEXT,
  missing_features TEXT,  -- Features not supported by substitute
  extra_features TEXT,    -- Features added by substitute
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (original_component_id) REFERENCES bom_items(id),
  FOREIGN KEY (substitute_component_id) REFERENCES bom_items(id),
  INDEX idx_original (original_component_id),
  INDEX idx_substitute (substitute_component_id)
);

-- ============================================================================
-- INDICES FOR COMMON QUERIES
-- ============================================================================

-- Common searches
CREATE INDEX idx_product_name_source ON products(product_name, source_id);
CREATE INDEX idx_bom_project ON boms(project_id);
CREATE INDEX idx_match_score_bom ON product_matches(bom_item_id, match_score);

-- ============================================================================
-- INSERT DEFAULT PRODUCT SOURCES
-- ============================================================================

INSERT IGNORE INTO product_sources (id, name, url, priority) VALUES
  (1, 'Robu', 'https://robu.in', 1),
  (2, 'Amazon', 'https://amazon.in', 2),
  (3, 'Flipkart', 'https://flipkart.com', 3);

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================
-- Run this schema on:
-- - PostgreSQL: Adjust TIMESTAMP syntax if needed
-- - MySQL: No changes needed
-- - SQLite: Remove AUTO_INCREMENT, use AUTOINCREMENT
-- - MongoDB: Convert to document structure
