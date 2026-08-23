"""
Shopping Service - Shopping List Generation & Cost Optimization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responsibilities:
1. Generate shopping lists from BOM
2. Optimize for cost, delivery, compatibility
3. Handle alternative products
4. Calculate build cost
5. Manage quantities
6. Support component substitutions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Shopping & Optimization Service")


# ────────────── DATA MODELS ──────────────
class ShoppingItem(BaseModel):
    """Item in shopping list"""
    bom_item_id: str
    component_name: str
    quantity: int
    product_id: str
    product_name: str
    seller: str
    price: float
    total_price: float
    match_score: float
    availability: bool
    url: str
    is_required: bool = True
    already_have: bool = False


class ShoppingList(BaseModel):
    """Complete shopping list"""
    project_id: str
    design_id: str
    timestamp: str
    items: List[ShoppingItem]
    subtotal: float
    estimated_shipping: float
    estimated_total: float
    currency: str = "INR"
    seller_count: int
    availability_status: str  # "All available", "Some unavailable", etc.
    optimization_applied: str = "Base Case"


class OptimizationResult(BaseModel):
    """Result of cost optimization"""
    original_cost: float
    optimized_cost: float
    savings: float
    savings_percent: float
    changes: List[str]  # Description of changes made
    seller_consolidation: int  # Number of sellers after optimization


class ShoppingListRequest(BaseModel):
    """Request model for shopping list generation"""
    project_id: str
    design_id: str
    bom_items: List[Dict[str, Any]]
    product_selections: Dict[str, str]


class OptimizationRequest(BaseModel):
    """Request model for optimization"""
    shopping_list: Dict[str, Any]
    optimization_type: str = "cost"
    all_product_options: Dict[str, List[Dict]] = {}


# ────────────── SHOPPING LIST GENERATOR ──────────────
class ShoppingListGenerator:
    """Generate shopping lists from BOM"""

    async def generate_shopping_list(self,
                                     project_id: str,
                                     design_id: str,
                                     bom_items: List[Dict[str, Any]],
                                     product_selections: Dict[str, str]) -> ShoppingList:
        """Generate shopping list from BOM and product selections"""
        
        shopping_items = []
        subtotal = 0.0
        sellers = set()
        unavailable_count = 0
        
        for bom_item in bom_items:
            product_id = product_selections.get(bom_item["id"])
            
            if not product_id:
                logger.warning(f"No product selected for BOM item {bom_item['id']}")
                continue
            
            # Get product details (would fetch from product service in real implementation)
            product = await self._get_product_details(product_id)
            
            if not product:
                unavailable_count += 1
                continue
            
            quantity = bom_item.get("quantity", 1)
            total_price = product["price"] * quantity
            
            shopping_item = ShoppingItem(
                bom_item_id=bom_item["id"],
                component_name=bom_item.get("name", "Unknown"),
                quantity=quantity,
                product_id=product_id,
                product_name=product["product_name"],
                seller=product["seller"],
                price=product["price"],
                total_price=total_price,
                match_score=product["match_score"],
                availability=product["availability"],
                url=product["url"],
                is_required=bom_item.get("is_required", True),
                already_have=False
            )
            
            shopping_items.append(shopping_item)
            subtotal += total_price
            sellers.add(product["seller"])
        
        # Estimate shipping (placeholder)
        estimated_shipping = self._estimate_shipping(subtotal, len(sellers))
        estimated_total = subtotal + estimated_shipping
        
        # Determine availability status
        if unavailable_count == 0:
            availability_status = "All components available"
        elif unavailable_count < len(bom_items) * 0.2:
            availability_status = f"Most available ({len(shopping_items)}/{len(bom_items)})"
        else:
            availability_status = f"Some unavailable ({unavailable_count} missing)"
        
        shopping_list = ShoppingList(
            project_id=project_id,
            design_id=design_id,
            timestamp=datetime.now().isoformat(),
            items=shopping_items,
            subtotal=subtotal,
            estimated_shipping=estimated_shipping,
            estimated_total=estimated_total,
            seller_count=len(sellers),
            availability_status=availability_status
        )
        
        logger.info(f"Generated shopping list with {len(shopping_items)} items from {len(sellers)} sellers")
        return shopping_list

    async def _get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product details (placeholder for API call)"""
        # In real implementation, fetch from product service/database
        return None

    def _estimate_shipping(self, subtotal: float, seller_count: int) -> float:
        """Estimate shipping cost"""
        base_shipping = 50.0  # Base shipping in INR
        
        # Multi-seller shipping multiplier
        if seller_count > 1:
            base_shipping += (seller_count - 1) * 20.0
        
        # Free shipping over 500 INR per seller
        if subtotal > 500 * seller_count:
            return 0.0
        
        return base_shipping


# ────────────── COST OPTIMIZER ──────────────
class CostOptimizer:
    """Optimize shopping list for cost, delivery, etc."""

    async def optimize_for_cost(self,
                                shopping_list: ShoppingList,
                                all_product_options: Dict[str, List[Dict]]) -> OptimizationResult:
        """Optimize shopping list for minimum cost"""
        
        original_cost = shopping_list.estimated_total
        optimized_items = []
        changes = []
        
        for item in shopping_list.items:
            alternatives = all_product_options.get(item.bom_item_id, [])
            
            if not alternatives:
                optimized_items.append(item)
                continue
            
            # Find cheapest alternative
            cheapest = min(alternatives, key=lambda x: x["price"] * item.quantity)
            current_cost = item.total_price
            new_cost = cheapest["price"] * item.quantity
            
            if new_cost < current_cost:
                savings = current_cost - new_cost
                changes.append(f"Switched {item.component_name} from {item.seller} (₹{current_cost}) to {cheapest['seller']} (₹{new_cost}) - Save ₹{savings}")
                
                item.price = cheapest["price"]
                item.total_price = new_cost
                item.seller = cheapest["seller"]
                item.match_score = cheapest["match_score"]
            
            optimized_items.append(item)
        
        # Recalculate totals
        new_subtotal = sum(item.total_price for item in optimized_items)
        new_shipping = ShoppingListGenerator()._estimate_shipping(
            new_subtotal,
            len(set(item.seller for item in optimized_items))
        )
        optimized_total = new_subtotal + new_shipping
        
        savings = original_cost - optimized_total
        savings_percent = (savings / original_cost * 100) if original_cost > 0 else 0
        
        seller_count = len(set(item.seller for item in optimized_items))
        
        result = OptimizationResult(
            original_cost=original_cost,
            optimized_cost=optimized_total,
            savings=savings,
            savings_percent=savings_percent,
            changes=changes,
            seller_consolidation=seller_count
        )
        
        logger.info(f"Optimization: ₹{original_cost} → ₹{optimized_total} (save ₹{savings})")
        return result

    async def optimize_for_delivery(self,
                                    shopping_list: ShoppingList,
                                    all_product_options: Dict[str, List[Dict]]) -> OptimizationResult:
        """Optimize for fastest delivery (fewest sellers)"""
        
        changes = []
        
        # Prioritize single seller for faster consolidated delivery
        sellers_with_all = self._find_sellers_with_all_items(shopping_list, all_product_options)
        
        if sellers_with_all:
            best_seller = sellers_with_all[0]  # First seller with all items
            changes.append(f"Consolidated purchases to {best_seller} for faster delivery")
        
        return OptimizationResult(
            original_cost=shopping_list.estimated_total,
            optimized_cost=shopping_list.estimated_total,
            savings=0,
            savings_percent=0,
            changes=changes,
            seller_consolidation=1 if sellers_with_all else shopping_list.seller_count
        )

    async def optimize_for_compatibility(self,
                                         shopping_list: ShoppingList,
                                         all_product_options: Dict[str, List[Dict]]) -> OptimizationResult:
        """Optimize for highest component compatibility"""
        
        original_cost = shopping_list.estimated_total
        optimized_items = []
        changes = []
        
        for item in shopping_list.items:
            alternatives = all_product_options.get(item.bom_item_id, [])
            
            if not alternatives:
                optimized_items.append(item)
                continue
            
            # Find highest match score
            best_match = max(alternatives, key=lambda x: x["match_score"])
            
            if best_match["match_score"] > item.match_score:
                changes.append(f"Selected {best_match['product_name']} for better compatibility ({best_match['match_score']}% match)")
                item.match_score = best_match["match_score"]
            
            optimized_items.append(item)
        
        return OptimizationResult(
            original_cost=original_cost,
            optimized_cost=shopping_list.estimated_total,
            savings=0,
            savings_percent=0,
            changes=changes,
            seller_consolidation=shopping_list.seller_count
        )

    def _find_sellers_with_all_items(self,
                                     shopping_list: ShoppingList,
                                     all_product_options: Dict[str, List[Dict]]) -> List[str]:
        """Find sellers that have all required items"""
        
        sellers_inventory = {}
        
        for bom_id, products in all_product_options.items():
            for product in products:
                seller = product["seller"]
                if seller not in sellers_inventory:
                    sellers_inventory[seller] = set()
                sellers_inventory[seller].add(bom_id)
        
        # Find sellers with all items
        required_items = set(item.bom_item_id for item in shopping_list.items if item.is_required)
        complete_sellers = [
            seller for seller, items in sellers_inventory.items()
            if required_items.issubset(items)
        ]
        
        return complete_sellers


# ────────────── API ENDPOINTS ──────────────
@app.post("/api/shopping-list/generate")
async def generate_shopping_list(request: ShoppingListRequest) -> ShoppingList:
    """Generate shopping list from BOM"""
    try:
        generator = ShoppingListGenerator()
        shopping_list = await generator.generate_shopping_list(
            project_id=request.project_id,
            design_id=request.design_id,
            bom_items=request.bom_items,
            product_selections=request.product_selections
        )
        return shopping_list
    except Exception as e:
        logger.error(f"Shopping list generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/build/optimize")
async def optimize_shopping_list(request: OptimizationRequest) -> OptimizationResult:
    """Optimize shopping list"""
    try:
        optimizer = CostOptimizer()
        
        if request.optimization_type == "cost":
            result = await optimizer.optimize_for_cost(request.shopping_list, request.all_product_options)
        elif request.optimization_type == "delivery":
            result = await optimizer.optimize_for_delivery(request.shopping_list, request.all_product_options)
        elif request.optimization_type == "compatibility":
            result = await optimizer.optimize_for_compatibility(request.shopping_list, request.all_product_options)
        else:
            original_total = request.shopping_list.get("estimated_total", 0)
            result = OptimizationResult(
                original_cost=original_total,
                optimized_cost=original_total,
                savings=0,
                savings_percent=0,
                changes=["No optimization applied"],
                seller_consolidation=request.shopping_list.get("seller_count", 1)
            )
        
        return result
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
