import os
import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from services.physics_service.materials.database import MaterialDatabase

class MaterialProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> Optional[Dict[str, Any]]:
        pass

class MaterialsProjectProvider(MaterialProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            # Query Materials Project via REST
            headers = {"X-API-KEY": self.api_key}
            
            # Map common names to elements for the query
            elements_query = "Al"
            if query.lower() == "titanium":
                elements_query = "Ti"
                
            response = requests.get(
                f"https://api.materialsproject.org/materials/summary/?elements={elements_query}&is_stable=true&limit=1",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    doc = data["data"][0]
                    return {
                        "name": doc.get("formula_pretty", query.capitalize()),
                        "E": doc.get("density", 2.7) * 10, # Mock mapping for demo since MP doesn't always have E
                        "nu": 0.33,
                        "yield_strength": 276.0
                    }
            else:
                logging.warning(f"Materials Project API returned status {response.status_code}")
        except Exception as e:
            logging.warning(f"Materials Project API failed: {e}")
            
        return None

class DemoMaterialProvider(MaterialProvider):
    def search(self, query: str) -> Optional[Dict[str, Any]]:
        return MaterialDatabase.get_material(query)

def get_provider() -> MaterialProvider:
    """Factory to get the correct material provider based on configuration."""
    use_demo = os.getenv("USE_DEMO_MATERIALS", "false").lower() == "true"
    mp_api_key = os.getenv("MP_API_KEY", "").strip()
    
    if not use_demo and mp_api_key:
        return MaterialsProjectProvider(api_key=mp_api_key)
    else:
        return DemoMaterialProvider()
