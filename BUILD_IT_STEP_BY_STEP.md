# 🚀 BUILD IT - Step-by-Step Rollout Plan

## STEP 1: Verify & Test BOM Service ✅

### 1.1 Prerequisites Check
- [x] BOM Service exists: `services/bom-service/main.py`
- [x] Requirements file exists: `services/bom-service/requirements.txt`
- [x] Dockerfile exists: `services/bom-service/Dockerfile`
- [x] Port 8009 available

### 1.2 BOM Service Overview
```
Service: Bill of Materials Generation
Port: 8009
Components:
  - BOMExtractor: Parses circuit/CAD data
  - BOMGenerator: Creates complete BOMs
  - Normalizer: Auto-categorizes components
  
Endpoints:
  POST /api/bom/generate - Generate BOM from circuit+CAD
  GET /api/bom/{project_id} - Retrieve saved BOM
```

### 1.3 Test Plan for BOM Service

#### A. Installation Test
```bash
cd services/bom-service
pip install -r requirements.txt
```

**Expected:** All packages installed without errors

#### B. Startup Test
```bash
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8009
INFO:     Application startup complete
```

#### C. API Test - BOM Generation
```bash
curl -X POST http://localhost:8009/api/bom/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-001",
    "design_id": "design-001",
    "circuit_data": {
      "components": [
        {"name": "ESP32", "value": "WROOM-32", "quantity": 1, "voltage": "3.3V"},
        {"name": "BME280", "value": "I2C", "quantity": 1},
        {"name": "Resistor", "value": "330Ω", "quantity": 4},
        {"name": "LED", "value": "5mm", "quantity": 2}
      ]
    }
  }'
```

**Expected Response:**
```json
{
  "project_id": "test-001",
  "design_id": "design-001",
  "timestamp": "2026-08-23T...",
  "items": [
    {
      "id": "bom_item_0",
      "component": {
        "category": "MCU",
        "name": "ESP32",
        "voltage": "3.3V",
        "quantity": 1,
        "is_required": true
      }
    }
    // ... more items
  ],
  "total_components": 4,
  "required_count": 4,
  "optional_count": 0
}
```

**Verification:**
- ✓ Returns 4 components (merged resistors + LED)
- ✓ Categories correctly identified
- ✓ Quantities preserved

#### D. Edge Cases Test

**Test 1: Duplicate Components**
```bash
# Send resistors with different values
curl -X POST http://localhost:8009/api/bom/generate \
  -d '{"circuit_data": {"components": [
    {"name": "Resistor", "value": "330Ω", "quantity": 2},
    {"name": "Resistor", "value": "470Ω", "quantity": 3}
  ]}}'
```
**Expected:** 2 separate items (different values)

**Test 2: Empty Input**
```bash
curl -X POST http://localhost:8009/api/bom/generate \
  -d '{"circuit_data": {"components": []}}'
```
**Expected:** Empty items array with count = 0

**Test 3: Mixed Circuit + CAD**
```bash
curl -X POST http://localhost:8009/api/bom/generate \
  -d '{
    "circuit_data": {"components": [{"name": "ESP32"}]},
    "cad_data": {"bom": [{"name": "Enclosure"}]}
  }'
```
**Expected:** 2 items total (1 MCU + 1 Mechanical)

### 1.4 Success Criteria

✅ Service starts without errors
✅ API responds to requests
✅ BOM generation works correctly
✅ Component categorization accurate
✅ Quantity merging works
✅ JSON response valid
✅ Error handling functional

### 1.5 Troubleshooting

**Issue: Port 8009 already in use**
```bash
# Find process using port
lsof -i :8009
# Kill it
kill -9 <PID>
```

**Issue: Module not found**
```bash
# Check Python version (3.8+)
python --version
# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt
```

**Issue: Service crashes after startup**
```bash
# Check for syntax errors
python -m py_compile main.py
# Run with verbose logging
PYTHONUNBUFFERED=1 python main.py
```

---

## STEP 2: Verify & Test Product Service ⏳

**When ready, we'll test:**
- Product search query generation
- Multi-seller search abstraction
- Product matching algorithm
- Caching mechanism

---

## STEP 3: Verify & Test Shopping Service ⏳

**When ready, we'll test:**
- Shopping list generation
- Cost optimization
- Seller consolidation
- Export functionality

---

## STEP 4: Verify & Test Substitution Service ⏳

**When ready, we'll test:**
- Compatibility checking
- Alternative suggestions
- Impact assessment

---

## STEP 5: Full Integration Test ⏳

**When ready, we'll test:**
- Complete BOM → Products → Shopping workflow
- All 4 services working together
- Database integration
- Frontend connection

---

## Ready to Start STEP 1?

**Current Status: READY FOR TESTING**

```bash
cd services/bom-service
pip install -r requirements.txt
python main.py
```

Then in another terminal:
```bash
# Run the verification test
bash BUILD_IT_TEST.sh
```

Let me know when you want to proceed! 🚀
