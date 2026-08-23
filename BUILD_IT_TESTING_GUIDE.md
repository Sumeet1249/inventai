# 🧪 BUILD IT - Integration Testing & Demo Guide

## Quick Start Testing

### Prerequisites
- Docker & Docker Compose installed
- InventAI services running (`docker-compose up`)
- Web interface accessible at `http://localhost:3001`

---

## Part 1: Local Service Testing

### 1. Start the Services

```bash
# Terminal 1: BOM Service
cd services/bom-service
python main.py
# Runs on http://localhost:8009

# Terminal 2: Product Service
cd services/product-service
python main.py
# Runs on http://localhost:8010

# Terminal 3: Shopping Service
cd services/shopping-service
python main.py
# Runs on http://localhost:8011

# Terminal 4: Substitution Service
cd services/substitution-service
python main.py
# Runs on http://localhost:8012
```

Or use Docker:
```bash
docker-compose -f docker-compose.yml up bom-service product-service shopping-service substitution-service
```

### 2. Test BOM Generation

**Request:**
```bash
curl -X POST http://localhost:8009/api/bom/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-test-123",
    "design_id": "design-456",
    "circuit_data": {
      "components": [
        {
          "name": "ESP32",
          "value": "WROOM-32",
          "quantity": 1,
          "voltage": "3.3V",
          "interface": ["WiFi", "BLE"],
          "required": true
        },
        {
          "name": "BME280",
          "value": "I2C Module",
          "quantity": 1,
          "voltage": "3.3V",
          "interface": ["I2C"],
          "required": true
        },
        {
          "name": "SSD1306",
          "value": "0.96 inch OLED",
          "quantity": 1,
          "voltage": "3.3V",
          "interface": ["I2C"],
          "required": true
        },
        {
          "name": "Resistor",
          "value": "330Ω 1/4W",
          "quantity": 4,
          "package": "axial",
          "required": true
        },
        {
          "name": "LED",
          "value": "5mm Red",
          "quantity": 2,
          "required": false
        }
      ]
    }
  }'
```

**Expected Response:**
```json
{
  "project_id": "proj-test-123",
  "design_id": "design-456",
  "timestamp": "2026-08-23T12:30:00",
  "items": [
    {
      "id": "bom_item_0",
      "component": {
        "category": "MCU",
        "name": "ESP32",
        "variant": "WROOM-32",
        "voltage": "3.3V",
        "interface": ["WiFi", "BLE"],
        "quantity": 1,
        "is_required": true
      }
    }
    // ... more items
  ],
  "total_components": 5,
  "required_count": 4,
  "optional_count": 1
}
```

**Verification:**
- ✓ Returns 5 components
- ✓ 4 required, 1 optional
- ✓ Categories correctly identified (MCU, Sensor, Display, Resistor, LED)

---

### 3. Test Product Searching

**Request:**
```bash
curl -X POST http://localhost:8010/api/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "category": "MCU",
    "name": "ESP32",
    "variant": "WROOM-32",
    "voltage": "3.3V",
    "interface": ["WiFi", "BLE"],
    "package": "DIP",
    "specs": {}
  }'
```

**Expected Response:**
```json
{
  "requirement": {
    "category": "MCU",
    "name": "ESP32",
    "variant": "WROOM-32",
    "voltage": "3.3V",
    "interface": ["WiFi", "BLE"],
    "package": "DIP",
    "specs": {}
  },
  "search_query": {
    "base_query": "ESP32",
    "enhanced_query": "ESP32 WROOM-32 3.3V WiFi BLE DIP",
    "filters": {
      "category": "MCU",
      "voltage": "3.3V",
      "interface": ["WiFi", "BLE"]
    }
  },
  "products": [
    // Placeholder: Add real products when APIs integrated
  ],
  "total_found": 0,
  "matching_count": 0
}
```

**Notes:**
- Products list is empty until e-commerce APIs are integrated
- Search query generation works correctly
- Real integration next step

---

### 4. Test Product Matching

**Request:**
```bash
curl -X POST http://localhost:8010/api/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Sensor",
    "name": "BME280",
    "voltage": "3.3V",
    "interface": ["I2C"],
    "specs": {}
  }'
```

**Expected Behavior:**
- Search query: "BME280 3.3V I2C"
- Matcher scores products (80%+ threshold)
- Results sorted by compatibility

---

### 5. Test Substitutions

**Request:**
```bash
curl -X POST http://localhost:8012/api/substitutions/find \
  -H "Content-Type: application/json" \
  -d '{
    "component_name": "ESP32",
    "component_specs": {
      "voltage": "3.3V",
      "interface": ["WiFi", "BLE"],
      "package": "DIP"
    },
    "reason": "unavailable",
    "max_suggestions": 3
  }'
```

**Expected Response:**
```json
{
  "original": "ESP32",
  "alternatives": [
    {
      "original_component": "ESP32",
      "substitute_component": "ESP32-S3",
      "compatibility_score": 95,
      "compatibility_notes": "Drop-in replacement, better performance",
      "missing_features": [],
      "extra_features": ["More GPIO", "USB OTG"],
      "impact_level": "low",
      "can_substitute": true
    },
    {
      "original_component": "ESP32",
      "substitute_component": "Arduino Nano",
      "compatibility_score": 45,
      "compatibility_notes": "Different architecture, no wireless",
      "missing_features": ["WiFi", "BLE"],
      "extra_features": [],
      "impact_level": "high",
      "can_substitute": false,
      "warnings": ["Voltage incompatible", "Missing wireless"]
    }
  ],
  "best_option": {
    "substitute_component": "ESP32-S3",
    "compatibility_score": 95
  },
  "explanation": "ESP32 is unavailable. Best alternative: ESP32-S3 (95% compatible). Drop-in replacement, better performance",
  "design_impact": "Low impact - drop-in replacement"
}
```

**Verification:**
- ✓ ESP32-S3 scored 95% (drop-in replacement)
- ✓ Arduino Nano scored 45% (not suitable)
- ✓ Best option correctly identified

---

### 6. Test Shopping List Generation

**Request:**
```bash
curl -X POST http://localhost:8011/api/shopping-list/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj-test-123",
    "design_id": "design-456",
    "bom_items": [
      {
        "id": "bom_item_0",
        "name": "ESP32",
        "quantity": 1,
        "is_required": true
      },
      {
        "id": "bom_item_1",
        "name": "BME280",
        "quantity": 1,
        "is_required": true
      }
    ],
    "product_selections": {
      "bom_item_0": "prod_esp32_robu_001",
      "bom_item_1": "prod_bme280_robu_002"
    }
  }'
```

**Expected Response:**
```json
{
  "project_id": "proj-test-123",
  "design_id": "design-456",
  "timestamp": "2026-08-23T12:35:00",
  "items": [
    {
      "bom_item_id": "bom_item_0",
      "component_name": "ESP32",
      "quantity": 1,
      "product_id": "prod_esp32_robu_001",
      "product_name": "ESP32 DevKit V1",
      "seller": "Robu",
      "price": 399,
      "total_price": 399,
      "match_score": 98,
      "availability": true,
      "url": "https://robu.in/product/...",
      "is_required": true,
      "already_have": false
    }
  ],
  "subtotal": 798,
  "estimated_shipping": 50,
  "estimated_total": 848,
  "currency": "INR",
  "seller_count": 1,
  "availability_status": "All components available",
  "optimization_applied": "Base Case"
}
```

---

## Part 2: Frontend Integration Testing

### Access the BUILD IT Feature

1. **Navigate to Project:**
   - Go to `http://localhost:3001/projects/new`
   - Enter: "ESP32 Weather Station with OLED display"
   - Click "Launch 6 AI Agents"

2. **Wait for Design Generation:**
   - CAD generation: ~10s
   - Physics simulation: ~15s
   - Business analysis: ~7s
   - Total: ~40s

3. **Click "Build It" Tab:**
   - Located in the tab bar at top of page
   - Shows 🛠️ icon

4. **Generate BOM:**
   - Click "⚡ Generate BOM"
   - Wait for extraction
   - See summary: "X components required"

5. **Search for Products:**
   - Click "🔍 Search for Products"
   - Waits for product search across sellers
   - Shows matched products

6. **View Details:**
   - Click product to expand
   - See "Why do I need this?" explanation
   - View design references (circuit, PCB position)
   - Click "Find alternatives" for substitutions

7. **Optimize Shopping List:**
   - See cost breakdown
   - Select optimization type (cost/delivery/compatibility)
   - View savings calculation

8. **Copy or Open:**
   - Click "📋 Copy List" to clipboard
   - Click "🔗 Open All" to open all product links

---

## Part 3: Full Integration Test Scenario

### Test Case: Complete Workflow

**Setup:**
```
User Idea: "Modular vertical farming unit with AI crop monitoring"
```

**Steps:**

1. **Design Phase** (Backend AI agents)
   ```
   CAD Agent: Generates modular frame design
   Physics Agent: Verifies structural integrity
   Circuit Agent: Generates sensor circuit
   ```

2. **BOM Extraction Phase** (BOM Service)
   ```
   Expected Components:
   - ESP32 (main controller)
   - 4x DHT22 (humidity sensors)
   - 2x Light sensors
   - 4x Soil moisture sensors
   - 4x Relay modules (water control)
   - Power supply
   - Cabling and connectors
   ```

3. **Product Search Phase** (Product Service)
   ```
   For each component:
   - Generate optimized search query
   - Query Robu, Amazon, Flipkart
   - Calculate match scores
   - Filter by 80%+ threshold
   ```

4. **Shopping List Phase** (Shopping Service)
   ```
   - Select best product for each component
   - Calculate total cost
   - Estimate shipping
   - Show availability
   ```

5. **Optimization Phase** (Cost Optimizer)
   ```
   - Find cost-optimized combination
   - Calculate savings
   - Show seller consolidation
   ```

6. **User Decision**
   ```
   - View final shopping list
   - Copy to clipboard
   - Open all product links in browser
   - Proceed to purchase
   ```

---

## Part 4: Error Handling & Edge Cases

### Test Case 1: Unavailable Component

**Scenario:** BME280 sensor is out of stock

**Expected Behavior:**
1. Substitution Service offers BMP280 as alternative
2. Shows compatibility: 87% (missing humidity)
3. Allows user to choose substitution
4. Recalculates shopping list

**Test:**
```bash
# Manually test substitution
curl -X POST http://localhost:8012/api/substitutions/find \
  -H "Content-Type: application/json" \
  -d '{
    "component_name": "BME280",
    "component_specs": {
      "voltage": "3.3V",
      "interface": ["I2C"]
    },
    "reason": "unavailable"
  }'
```

---

### Test Case 2: No Exact Match Found

**Scenario:** Exotic component not available anywhere

**Expected Behavior:**
1. Search returns "Product not found" instead of fake data
2. Shows search queries for manual lookup
3. Allows "Mark as already available"
4. Continues with other components

**Verification:**
- ✓ No fabricated product data
- ✓ Fallback search links provided
- ✓ User can override

---

### Test Case 3: Multi-Seller Optimization

**Scenario:** Components spread across 5 sellers

**Expected Behavior:**
1. Base case: 5 sellers, ₹1,500 + shipping
2. Optimized: 2 sellers, ₹1,340 + shipping
3. Shows consolidation strategy
4. Calculates shipping savings

**Test:**
```bash
curl -X POST http://localhost:8011/api/build/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "shopping_list": { /* ... */ },
    "optimization_type": "cost",
    "all_product_options": { /* ... */ }
  }'
```

---

## Part 5: Performance Testing

### Load Test: Large BOM

**Scenario:** 50+ components

**Expected:**
- BOM extraction: <500ms
- Product search: <5s (5 components × 1s parallel)
- Shopping list generation: <500ms
- **Total: <6s**

**Test:**
```bash
# Generate large BOM
curl -X POST http://localhost:8009/api/bom/generate \
  -d '{ 50 components ... }'

# Measure response time
time curl ...
```

---

### Cache Hit Test

**Scenario:** Search same component twice

**Expected:**
- First search: ~1s (API call + cache miss)
- Second search: <100ms (cache hit)

**Test:**
```bash
# First search (cache miss)
curl -X POST http://localhost:8010/api/products/search ...
# Response time: ~1s

# Second search (cache hit)
curl -X POST http://localhost:8010/api/products/search ...
# Response time: ~100ms
```

---

## Part 6: Database Integration Test

### Schema Validation

```sql
-- Verify tables exist
SELECT name FROM sqlite_master WHERE type='table';

-- Expected tables:
-- boms
-- bom_items
-- products
-- product_matches
-- shopping_lists
-- shopping_list_items
-- component_substitutions
-- product_search_cache
```

### Data Insertion Test

```sql
-- Insert test BOM
INSERT INTO boms (id, project_id, design_id, total_components, required_count)
VALUES ('bom_001', 'proj_001', 'design_001', 5, 4);

-- Insert test component
INSERT INTO bom_items (id, bom_id, component_name, component_category, quantity)
VALUES ('item_001', 'bom_001', 'ESP32', 'MCU', 1);

-- Verify
SELECT * FROM bom_items WHERE bom_id = 'bom_001';
```

---

## Part 7: E-Commerce API Integration Checklist

### Before going live with real products:

- [ ] Implement Robu.in API integration
- [ ] Implement Amazon India API integration
- [ ] Implement Flipkart API integration
- [ ] Add product image URLs
- [ ] Add inventory management
- [ ] Add price tracking
- [ ] Add affiliate links (if applicable)
- [ ] Add proper error handling for API failures
- [ ] Add rate limiting
- [ ] Add authentication for paid APIs

### Integration Template

```python
class RealRobuProvider(ProductProvider):
    async def search(self, query: str) -> List[ProductSpec]:
        cache_key = self._get_cache_key(query)
        
        # Check cache first
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if self._is_cache_valid(cached["timestamp"]):
                return cached["results"]
        
        # Call real Robu API
        response = await self.robu_client.search(query)
        results = self._normalize_results(response)
        
        # Cache results
        self.cache[cache_key] = {
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return results
```

---

## Part 8: Demo Script for Hackathon

### "From Idea to Shopping Cart in 2 Minutes"

1. **Show Idea Entry** (5 sec)
   - "ESP32 Weather Station"

2. **Show Design Generation** (15 sec)
   - CAD frame rendering
   - Physics validation (safety factor)
   - Circuit diagram

3. **Click BUILD IT** (2 sec)
   - "Your design is ready to build"

4. **Generate BOM** (3 sec)
   - "8 components required"

5. **Search Products** (10 sec)
   - "Searching Robu, Amazon, Flipkart..."
   - Products appear with match scores

6. **Show Optimization** (5 sec)
   - "Save ₹214 by using Robu for 6 items"

7. **Final Shopping List** (3 sec)
   - ₹1,248 total
   - "All from verified sellers"

8. **Key Moment**
   - Click "Open All" → All product tabs open
   - Or "Copy List" → List ready to manually add to carts

**Total Time: 2 minutes**

**Impact Message:**
"InventAI doesn't just design—it connects your ideas directly to components you can buy today."

---

## Troubleshooting

### Service Port Conflicts

```bash
# Check if port is in use
lsof -i :8009  # BOM Service

# Kill process if needed
kill -9 <PID>
```

### Database Issues

```bash
# Reset database
rm services/database/inventai.db

# Reinitialize schema
sqlite3 services/database/inventai.db < services/database/schema.sql
```

### API Response Issues

```bash
# Check service logs
docker logs bom-service
docker logs product-service
docker logs shopping-service
```

### Frontend Not Showing BUILD IT

```bash
# Rebuild web service
docker-compose build web
docker-compose up web
```

---

## Success Criteria

- ✓ BOM generated with correct component count
- ✓ Product search returns results (placeholder or real)
- ✓ Shopping list calculated with correct pricing
- ✓ Substitutions offered for unavailable items
- ✓ Optimization shows cost savings
- ✓ Design linking shows circuit/PCB references
- ✓ Component explanations display correctly
- ✓ All links are verified (no fabricated URLs)
- ✓ Performance <6s for 50-component BOM
- ✓ Caching reduces repeat searches by 90%+

---

## Next Steps

1. **Integrate real e-commerce APIs** - Robu, Amazon, Flipkart
2. **Add affiliate links** - Enable monetization
3. **Build admin dashboard** - Monitor search volume, popular components
4. **Add user accounts** - Save shopping lists and projects
5. **Add cart synchronization** - Direct integration with seller carts
6. **Add price history** - Track and notify on price drops
7. **Build community** - Share successful BOMs and recommendations

---

**BUILD IT is production-ready for local testing. E-commerce API integration is the next major phase.**
