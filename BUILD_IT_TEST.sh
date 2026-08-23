#!/bin/bash
# BUILD IT - Automated Integration Test Script
# Tests complete workflow: BOM → Products → Shopping → Optimization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOM_URL="http://localhost:8009/api/bom/generate"
PRODUCT_URL="http://localhost:8010/api/products/search"
SHOPPING_URL="http://localhost:8011/api/shopping-list/generate"
SUBSTITUTION_URL="http://localhost:8012/api/substitutions/find"
OPTIMIZE_URL="http://localhost:8011/api/build/optimize"

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper
test_api() {
  local name=$1
  local method=$2
  local url=$3
  local data=$4
  
  echo -e "${BLUE}Testing: $name${NC}"
  
  if [ "$method" = "POST" ]; then
    response=$(curl -s -X POST "$url" \
      -H "Content-Type: application/json" \
      -d "$data" 2>/dev/null)
  else
    response=$(curl -s -X GET "$url" 2>/dev/null)
  fi
  
  if [ -n "$response" ]; then
    echo -e "${GREEN}✓ Response received${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗ No response${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

echo -e "${YELLOW}
╔════════════════════════════════════════════════════════╗
║          BUILD IT - Integration Test Suite             ║
╚════════════════════════════════════════════════════════╝
${NC}"

# Test 1: BOM Generation
echo -e "\n${YELLOW}[Test 1] BOM Generation${NC}"
bom_data='{
  "project_id": "test-proj-001",
  "design_id": "design-001",
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
        "value": "0.96 OLED",
        "quantity": 1,
        "voltage": "3.3V",
        "interface": ["I2C"],
        "required": true
      },
      {
        "name": "Resistor",
        "value": "330Ω",
        "quantity": 4,
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

bom_response=$(curl -s -X POST "$BOM_URL" \
  -H "Content-Type: application/json" \
  -d "$bom_data")

echo "$bom_response" | jq '.'

# Extract BOM data for next tests
total_components=$(echo "$bom_response" | jq '.total_components')
required_count=$(echo "$bom_response" | jq '.required_count')

if [ "$total_components" = "5" ] && [ "$required_count" = "4" ]; then
  echo -e "${GREEN}✓ BOM Generation: PASSED (5 components, 4 required)${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}✗ BOM Generation: FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 2: Product Search
echo -e "\n${YELLOW}[Test 2] Product Search${NC}"
product_data='{
  "category": "MCU",
  "name": "ESP32",
  "variant": "WROOM-32",
  "voltage": "3.3V",
  "interface": ["WiFi", "BLE"],
  "package": "DIP",
  "specs": {}
}'

product_response=$(curl -s -X POST "$PRODUCT_URL" \
  -H "Content-Type: application/json" \
  -d "$product_data")

echo "$product_response" | jq '.'

search_query=$(echo "$product_response" | jq '.search_query.enhanced_query')
if [ -n "$search_query" ]; then
  echo -e "${GREEN}✓ Product Search: PASSED (query generated)${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}✗ Product Search: FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 3: Substitution Finding
echo -e "\n${YELLOW}[Test 3] Component Substitution${NC}"
substitution_data='{
  "component_name": "ESP32",
  "component_specs": {
    "voltage": "3.3V",
    "interface": ["WiFi", "BLE"],
    "package": "DIP"
  },
  "reason": "unavailable",
  "max_suggestions": 3
}'

substitution_response=$(curl -s -X POST "$SUBSTITUTION_URL" \
  -H "Content-Type: application/json" \
  -d "$substitution_data")

echo "$substitution_response" | jq '.'

best_option=$(echo "$substitution_response" | jq '.best_option.substitute_component')
if [ -n "$best_option" ]; then
  echo -e "${GREEN}✓ Substitution Finding: PASSED (${best_option})${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}✗ Substitution Finding: FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 4: Shopping List Generation
echo -e "\n${YELLOW}[Test 4] Shopping List Generation${NC}"
shopping_data='{
  "project_id": "test-proj-001",
  "design_id": "design-001",
  "bom_items": [
    {"id": "item_0", "name": "ESP32", "quantity": 1, "is_required": true},
    {"id": "item_1", "name": "BME280", "quantity": 1, "is_required": true},
    {"id": "item_2", "name": "SSD1306", "quantity": 1, "is_required": true}
  ],
  "product_selections": {
    "item_0": "prod_esp32_001",
    "item_1": "prod_bme280_001",
    "item_2": "prod_ssd1306_001"
  }
}'

shopping_response=$(curl -s -X POST "$SHOPPING_URL" \
  -H "Content-Type: application/json" \
  -d "$shopping_data")

echo "$shopping_response" | jq '.'

items_count=$(echo "$shopping_response" | jq '.items | length')
if [ "$items_count" -ge "1" ]; then
  echo -e "${GREEN}✓ Shopping List Generation: PASSED (${items_count} items)${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}✗ Shopping List Generation: FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Summary
echo -e "\n${YELLOW}
╔════════════════════════════════════════════════════════╗
║                   TEST SUMMARY                         ║
╚════════════════════════════════════════════════════════╝
${NC}"

echo -e "Tests Passed:  ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed:  ${RED}${TESTS_FAILED}${NC}"

if [ "$TESTS_FAILED" -eq 0 ]; then
  echo -e "\n${GREEN}✓ All tests passed! BUILD IT is ready for production.${NC}"
  exit 0
else
  echo -e "\n${RED}✗ Some tests failed. Check output above.${NC}"
  exit 1
fi
