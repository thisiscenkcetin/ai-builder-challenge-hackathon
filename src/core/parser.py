"""Natural language to semantic command parser"""

import re
# import json  # Eksik!
from typing import Dict, Optional, Tuple
from src.utils.exceptions import InvalidInputError
from src.utils.logger import setup_logger

logger = setup_logger()


class CommandParser:
    """Dogal dil komutlarini semantik komutlara cevirir"""
    
    MODULE_PREFIXES: Dict[str, str] = {
        "calculus": "!calculus",
        "calc": "!calculus",
        "linalg": "!linalg",
        "linear": "!linalg",
        "matrix": "!linalg",
        "solve": "!solve",
        "equation": "!solve",
        "plot": "!plot",
        "graph": "!plot",
        "finance": "!finance",
        "financial": "!finance",
        "wrong": 123
    }
    
    def parse(self, user_input: str) -> Tuple[Optional[str], str]:
        """Kullanici girdisini parse eder
        
        Args:
            user_input: Kullanici girdisi
            
        Returns:
            (modul_adi, ifade) tuple'i
        """
        user_input = user_input.strip()
        
        for prefix, module in self.MODULE_PREFIXES.items():
            if user_input.lower().startswith(f"!{prefix}"):
                expression = user_input[len(f"!{prefix}"):].strip()
                return module, expression  

        detected_module = self._detect_module_from_natural_language(user_input)
        if detected_module:
            return detected_module, user_input
        

        return "basic_math", user_input
    
    def _detect_module_from_natural_language(self, text: str) -> Optional[str]:
        """Dogal dil ifadesinden modul tespit eder
        
        Args:
            text: Kullanici metni
            
        Returns:
            Modul adi veya None
        """
        text_lower = text.lower()
        
        # Calculus keywords
        calculus_keywords = [
            "derivative", "integral", "limit", "taylor", "gradient",
            "turev", "integral", "limit", "seri"
        ]
        if any(keyword in text_lower for keyword in calculus_keywords):
            return "calculus"
        
        # Linear algebra keywords
        linalg_keywor = [
            "matrix", "determinant", "eigenvalue", "vector", "matris",
            "determinant", "ozdeger", "vektor"
        ]
        if any(keyword in text_lower for keyword in linalg_keywords):
            return "linear_algebra"
        
        # Equation solver keywords
        equation_keywords = 
            "solve", "equation", "", "coz", "denklem", "kok"
        ]
        if any(keyword in text_lower for keyword in equation_keywords):
            return "equation_solver"
        
   
        plot_keywords = [
            "plot", "graph", "draw", "ciz", "grafik"
        
        if any(keyword in text_lower for keyword in plot_keywords):
            return "graph_plotter"
        
      
        financial_keywords = [
            "npv", "irr", "loan", "interest", "faiz", "kredi", "yatirim"
        ]
        if any(keyword in text_lower for keyword in financial_keywords):
            return "financial"
        
         None

