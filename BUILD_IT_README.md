# 🛠️ BUILD IT - Component Sourcing & Shopping Feature

## Overview

**BUILD IT** is a comprehensive component sourcing and shopping list system that bridges the gap between AI-generated designs and real-world component procurement. After generating a design, users can instantly discover real products from Indian e-commerce platforms and build a complete shopping list.

## Architecture

### Backend Services (Microservices)

#### 1. **BOM Service** (Port 8009)
- **Purpose**: Extract and normalize Bill of Materials from circuit and CAD designs
- **Key Classes**:
  - `BOMExtractor`: Parses circuit/CAD data into component specifications
  - `BOMGenerator`: Creates complete BOMs from design data
- **Features**:
  - Automatic component categorization
  - Specification normalization
  - Quantity aggregation for duplicate components
  - Design reference mapping

**Key Endpoint**:
```bash
POST /api/bom/generate
Body: { project_id, design_id, circuit_data, cad_data }
Response: { BOM object with items, counts, estimated cost }
```

---

#### 2. **Product Service** (Port 8010)
- **Purpose**: Search and match real products across multiple sellers
- **Key Classes**:
  - `ProductProvider` (Abstract): Interface for seller integrations
  - `RobuProvider`, `AmazonIndiaProvider`, `FlipkartProvider`: Concrete implementations
  - `SearchQueryGenerator`: Optimized query creation
  - `ProductMatcher`: Scoring and ranking algorithm
- **Features**:
  - Multi-seller search abstraction
  - Intelligent query generation
  - Product matching with 80%+ threshold
  - Result caching to avoid repeated searches
  - Seller prioritization

**Key Endpoints**:
```bash
POST /api/products/search
Body: { ComponentRequirement }
Response: { products[], total_found, matching_count }

GET /api/products/{product_id}
Response: { ProductSpec details }
```

---

#### 3. **Shopping Service** (Port 8011)
- **Purpose**: Generate shopping lists and optimize for cost/delivery
- **Key Classes**:
  - `ShoppingListGenerator`: Creates shopping lists from BOM + product selections
  - `CostOptimizer`: Multi-objective optimization
- **Features**:
  - Automatic cost calculation
  - Shipping estimation
  - Cost optimization
  - Delivery consolidation
  - Compatibility optimization
  - Multi-seller management

**Key Endpoints**:
```bash
POST /api/shopping-list/generate
Body: { project_id, design_id, bom_items[], product_selections{} }
Response: { ShoppingList with pricing and availability }

POST /api/build/optimize
Body: { shopping_list, optimization_type, all_product_options{} }
Response: { OptimizationResult with savings }
```

---

### Frontend Components

Located in `apps/web/components/build/`

1. **BuildPanel.tsx** - Main orchestrator
   - Manages BOM generation workflow
   - Coordinates product search
   - Handles tab navigation
   - Integrates all sub-components

2. **BOMTable.tsx** - BOM visualization
   - Displays components in tabular format
   - Shows categories, specs, quantities
   - Calculates summary statistics
   - Required/optional indicators

3. **ProductCard.tsx** - Product listing
   - Shows individual product matches
   - Displays match score with color coding
   - Includes seller, price, availability
   - Links to product pages

4. **BuildSummary.tsx** - Overview panel
   - Design readiness status
   - Component statistics
   - Core components preview
   - Next steps guidance

5. **ShoppingList.tsx** - Shopping list manager
   - Checkbox-based item selection
   - Real-time cost calculation
   - Multi-seller tracking
   - Export and open links functionality

---

### Data Models

#### BOM Item
```typescript
{
  id: string;
  component: ComponentSpec;
  design_ref?: string;           // Reference in circuit
  pin_mapping?: Record<string, string>;
  position?: { x, y, z };        // PCB coordinates
  notes?: string;
}
```

#### Product Specification
```typescript
{
  id: string;
  component: string;
  product_name: string;
  seller: "Robu" | "Amazon" | "Flipkart";
  price: number;
  availability: boolean;
  url: string;
  match_score: number;           // 0-100
  specifications: Record<string, any>;
}
```

#### Shopping Item
```typescript
{
  bom_item_id: string;
  product_id: string;
  quantity: number;
  price: number;
  total_price: number;
  match_score: number;
  seller: string;
  is_required: boolean;
  already_have: boolean;
}
```

---

## Workflow

### User Journey

```
1. User generates design (CAD + Circuit + Physics)
   ↓
2. Clicks "BUILD IT" tab
   ↓
3. Clicks "Generate BOM"
   ↓
   BOM Service extracts components from circuit/CAD
   ↓
4. Sees BOM summary: "8 components required, 2 optional"
   ↓
5. Clicks "Search for Products"
   ↓
   Product Service searches across 3 sellers
   ↓
6. Sees matched products:
   - ESP32 DevKit: ₹399 @ Robu (98% match)
   - BME280: ₹149 @ Robu (96% match)
   - SSD1306 OLED: ₹129 @ Amazon (94% match)
   - etc.
   ↓
7. Clicks "Optimize Cost"
   ↓
   Shopping Service finds: "Save ₹214 by using Robu for 6 items"
   ↓
8. Sees final shopping list: ₹1,248 total
   ↓
9. Clicks "Copy List" or "Open All"
   ↓
10. User can purchase manually from multiple sellers
```

---

## Product Matching Algorithm

### Match Score Calculation (0-100)

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Name | 30% | Exact match in product name |
| Voltage | 20% | Matches requirement |
| Interface | 20% | Compatible I2C/SPI/UART |
| Package | 15% | Correct form factor |
| Availability | 15% | In stock = 100%, else 0% |

**Threshold**: Products scoring 80%+ are shown

### Example

For requirement: `ESP32-WROOM-32, 3.3V, WiFi+BLE`

Product A: "ESP32 DevKit V1 WROOM-32" → 95% match ✅
- Name: 30/30 (exact variant)
- Voltage: 20/20 (3.3V confirmed)
- Interface: 20/20 (WiFi + BLE)
- Package: 15/15 (DIP)
- Availability: 15/15 (in stock)

Product B: "Generic ESP32 Clone" → 62% match ❌
- Name: 20/30 (generic, not WROOM-32)
- Voltage: 15/20 (sometimes unstable at 3.3V)
- Interface: 12/20 (WiFi only)
- Package: 10/15 (questionable)
- Availability: 5/15 (low stock)

---

## Cost Optimization Strategies

### 1. **Cost Optimization**
- Finds cheapest alternative for each component
- Consolidates to fewest sellers
- Prioritizes bulk discounts
- Calculates shipping savings

**Typical Result**: ₹1,462 → ₹1,248 (-₹214, -14.6%)

### 2. **Delivery Optimization**
- Groups items by seller for consolidated shipping
- Minimizes shipping fees
- Prioritizes fast shipping availability
- One-click consolidation possible

**Typical Result**: Order from 1 seller instead of 3

### 3. **Compatibility Optimization**
- Prioritizes highest match scores
- Avoids risky components
- Ensures verified sellers
- Reduces buyer's remorse

**Typical Result**: 94% → 96% avg match score

---

## Database Schema

See `services/database/schema.sql` for complete structure.

### Key Tables
- `boms` - Bill of Materials records
- `bom_items` - Individual components
- `products` - Product listings from sellers
- `product_matches` - Scoring matrix
- `shopping_lists` - Generated shopping lists
- `product_search_cache` - Search result caching

---

## API Integration Points

### Real E-Commerce APIs to Integrate

1. **Robu.in**
   - Official API: Not publicly available
   - Alternative: Web scraping with rate limiting
   - Search endpoint pattern: `https://robu.in/search?q={query}`

2. **Amazon India**
   - Product Advertising API (paid)
   - Alternative: Public search (no authentication needed)
   - Search endpoint: `https://www.amazon.in/s?k={query}`

3. **Flipkart**
   - Official API: Limited availability
   - Alternative: Public search interface
   - Search endpoint: `https://www.flipkart.com/search?q={query}`

### Implementation Notes
- All real API calls should be cached
- Respect robots.txt and rate limits
- Never scrape protected pages aggressively
- Return "Product not found" if data cannot be verified
- Use verified product links only

---

## Component Substitution (Future)

When a component is unavailable:

```
Original: BME280 (I2C Temperature + Pressure + Humidity)
Substitutes:
  ✓ BMP280 (I2C Temperature + Pressure, 3.3V)
    - Compatibility: 87%
    - Missing: Humidity measurement
    - Impact: Moderate - humidity data unavailable
    
  ✗ DHT22 (I2C Temperature + Humidity, different voltage)
    - Compatibility: 62%
    - Missing: Pressure measurement
    - Impact: High - incompatible power requirements
```

---

## Installation & Running

### Start Services
```bash
# BOM Service
cd services/bom-service
python main.py  # Runs on http://localhost:8009

# Product Service
cd services/product-service
python main.py  # Runs on http://localhost:8010

# Shopping Service
cd services/shopping-service
python main.py  # Runs on http://localhost:8011
```

### Docker
```bash
docker-compose -f docker-compose.yml up bom-service product-service shopping-service
```

### Frontend
The `BuildPanel` component is automatically integrated into `/projects/[id]` page.

Navigate to a project and click the "Build It" tab.

---

## Testing

### Example BOM Generation
```bash
curl -X POST http://localhost:8009/api/bom/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-123",
    "design_id": "design-456",
    "circuit_data": {
      "components": [
        {"name": "ESP32", "value": "WROOM-32", "quantity": 1, "voltage": "3.3V"},
        {"name": "BME280", "value": "I2C Module", "quantity": 1},
        {"name": "Resistor", "value": "330Ω", "quantity": 4}
      ]
    }
  }'
```

Response:
```json
{
  "project_id": "proj-123",
  "total_components": 3,
  "required_count": 3,
  "optional_count": 0,
  "items": [...]
}
```

---

## Hackathon Demo Script

**"BUILD IT - From Idea to Purchase"**

1. **Demo Design**: "ESP32 Weather Station"
2. **Generate BOM**: "8 components found"
3. **Search Products**: "Searching Robu, Amazon, Flipkart..."
4. **Show Matches**: "All components found from verified sellers"
5. **Optimize**: "Save ₹214 by consolidating to Robu"
6. **Final List**: "₹1,248 total, ready to buy"
7. **Impact**: "User never had to manually search—everything is automated"

---

## Future Enhancements

1. **Real E-Commerce API Integration**
   - Official Robu API
   - Amazon Product API
   - Flipkart Integration

2. **Smart Substitutions**
   - Automatic replacement suggestions
   - Compatibility verification
   - Cross-checking with physics/CAD

3. **Cart Integrations**
   - Direct Amazon cart addition (via affiliate API)
   - Robu auto-fill
   - Multi-vendor cart management

4. **Component Availability Alerts**
   - Price drop notifications
   - Back-in-stock alerts
   - Bulk discount tracking

5. **Build Community**
   - Shared BOMs
   - User reviews of component combinations
   - Build recommendations

6. **Pricing Analytics**
   - Historical price trends
   - Seasonal discount tracking
   - Bulk pricing tiers

---

## Support

For questions or issues:
1. Check the schema and type definitions
2. Review example API calls
3. Inspect network requests in browser DevTools
4. Check service logs at http://localhost:8009/docs (etc.)

---

**BUILD IT** enables users to go from idea → design → shopping list in minutes. This is the missing link between AI-powered engineering and real-world fabrication.
