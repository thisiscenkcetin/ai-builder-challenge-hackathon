"""Unit Converter module for Calculator Agent"""

from src.modules.base_module import BaseModule
from src.schemas.models import CalculationResult
from src.utils.logger import setup_logger
from typing import Dict, Any

logger = setup_logger()

# Conversion factors
CONVERSION_FACTORS: Dict[str, Dict[str, float]] = {
    "length": {
        "m_to_km": 0.001,
        "m_to_cm": 100,
        "m_to_mm": 1000,
        "m_to_inch": 39.3701,
        "m_to_ft": 3.28084,
        "m_to_yd": 1.09361,
        "m_to_mile": 0.000621371,
        "km_to_m": 1000,
        "cm_to_m": 0.01,
        "mm_to_m": 0.001,
        "inch_to_m": 0.0254,
        "ft_to_m": 0.3048,
        "yd_to_m": 0.9144,
        "mile_to_m": 1609.34,
    },
    "weight": {
        "kg_to_g": 1000,
        "kg_to_mg": 1000000,
        "kg_to_lb": 2.20462,
        "kg_to_oz": 35.274,
        "kg_to_ton": 0.001,
        "g_to_kg": 0.001,
        "mg_to_kg": 0.000001,
        "lb_to_kg": 0.453592,
        "oz_to_kg": 0.0283495,
        "ton_to_kg": 1000,
    },
    "temperature": {
        "celsius_to_fahrenheit": lambda c: (c * 9/5) + 32,
        "fahrenheit_to_celsius": lambda f: (f - 32) * 5/9,
        "celsius_to_kelvin": lambda c: c + 273.15,
        "kelvin_to_celsius": lambda k: k - 273.15,
    },
    "currency": {
        "usd_to_try": 33.50,
        "eur_to_try": 36.75,
        "gbp_to_try": 42.50,
        "try_to_usd": 0.0299,
        "try_to_eur": 0.0272,
        "try_to_gbp": 0.0235,
    }
}

UNIT_CONVERTER_PROMPT = """
Sen bir birim cevirme uzmanisisin. Aşağıdaki dönüşümü yaparak sonucu JSON formatında dön.
JSON format:
{{
    "result": <numerik_sonuc>,
    "steps": [
        "Giriş: {{value}} {{from_unit}}",
        "Dönüşüm faktörü: {{factor}}",
        "Çıkış: {{result}} {{to_unit}}"
    ],
    "visualization_needed": false,
    "domain": "unit_converter",
    "confidence_score": 1.0,
    "from_unit": "{{from_unit}}",
    "to_unit": "{{to_unit}}"
}}

İfade: {{expression}}
"""


class UnitConverterModule(BaseModule):
    """Birim çevirici modülü (uzunluk, ağırlık, sıcaklık, döviz kuru)"""
    
    def _get_domain_prompt(self) -> str:
        """Unit converter prompt'unu döndürür"""
        return UNIT_CONVERTER_PROMPT
    
    async def calculate(
        self,
        expression: str,
        **kwargs
    ) -> CalculationResult:
        """Birim çevirme işlemi yapar
        
        Args:
            expression: Çevirme ifadesi (ornek: "100 km to miles", "25 celsius to fahrenheit")
            **kwargs: Ek parametreler
            
        Returns:
            CalculationResult objesi
        """
        self.validate_input(expression)
        
        logger.info(f"Unit conversion: {expression}")
        
        try:
            # Doğal dili parse et
            value, from_unit, to_unit = self._parse_conversion_expression(expression)
            
            # Dönüştür
            result = self._convert_units(value, from_unit, to_unit)
            
            # CalculationResult oluştur
            calculation_result = CalculationResult(
                result=result,
                steps=[
                    f"Giriş: {value} {from_unit}",
                    f"Dönüşüm: {from_unit} → {to_unit}",
                    f"Çıkış: {result} {to_unit}"
                ],
                confidence_score=1.0,
                domain="unit_converter",
                metadata={
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "input_value": value
                }
            )
            
            logger.info(f"Unit conversion successful: {value} {from_unit} = {result} {to_unit}")
            return calculation_result
            
        except Exception as e:
            logger.error(f"Unit conversion error: {e}")
            raise
    
    def _parse_conversion_expression(self, expression: str) -> tuple:
        """Dönüştürme ifadesini parse eder
        
        Args:
            expression: "100 km to miles" formatında ifade
            
        Returns:
            (value, from_unit, to_unit) tuple'ı
        """
        # Farklı format desenleri
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(\w+)\s+(?:to|into|as)\s+(\w+)',  # "100 km to miles"
            r'(\d+(?:\.\d+)?)\s+(\w+)\s+(?:kaç|ne kadar)\s+(\w+)',  # "100 km kaç mile"
            r'(\d+(?:\.\d+)?)\s*(\w+)→(\w+)',  # "100 km→mile"
        ]
        
        import re
        expression_lower = expression.lower()
        
        for pattern in patterns:
            match = re.search(pattern, expression_lower)
            if match:
                value = float(match.group(1))
                from_unit = match.group(2).strip()
                to_unit = match.group(3).strip()
                return value, from_unit, to_unit
        
        # Varsayılan: ilk 3 kelimeyi kullan
        parts = expression.split()
        if len(parts) >= 3:
            try:
                value = float(parts[0])
                from_unit = parts[1]
                to_unit = parts[-1]
                return value, from_unit, to_unit
            except ValueError:
                pass
        
        raise ValueError(f"Geçersiz dönüştürme ifadesi: {expression}")
    
    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> float:
        """Birimler arasında dönüştürme yapar
        
        Args:
            value: Dönüştürülecek değer
            from_unit: Kaynak birim
            to_unit: Hedef birim
            
        Returns:
            Dönüştürülmüş değer
        """
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        
        # Uzunluk dönüşümleri
        if self._is_length_unit(from_unit) and self._is_length_unit(to_unit):
            return self._convert_length(value, from_unit, to_unit)
        
        # Ağırlık dönüşümleri
        if self._is_weight_unit(from_unit) and self._is_weight_unit(to_unit):
            return self._convert_weight(value, from_unit, to_unit)
        
        # Sıcaklık dönüşümleri
        if self._is_temperature_unit(from_unit) and self._is_temperature_unit(to_unit):
            return self._convert_temperature(value, from_unit, to_unit)
        
        # Döviz kuru dönüşümleri
        if self._is_currency(from_unit) and self._is_currency(to_unit):
            return self._convert_currency(value, from_unit, to_unit)
        
        raise ValueError(f"Bilinmeyen birim dönüşümü: {from_unit} → {to_unit}")
    
    def _convert_length(self, value: float, from_unit: str, to_unit: str) -> float:
        """Uzunluk birimlerini dönüştürür"""
        # Tüm birimleri metre'ye dönüştür
        length_aliases = {
            "m": "m", "meter": "m", "metre": "m", "metres": "m", "meters": "m",
            "km": "km", "kilometer": "km", "kilometre": "km", "kilometres": "km", "kilometers": "km",
            "cm": "cm", "centimeter": "cm", "centimetre": "cm", "centimetres": "cm", "centimeters": "cm",
            "mm": "mm", "millimeter": "mm", "millimetre": "mm", "millimetres": "mm", "millimeters": "mm",
            "inch": "inch", "inches": "inch", "in": "inch",
            "ft": "ft", "foot": "ft", "feet": "ft",
            "yd": "yd", "yard": "yd", "yards": "yd",
            "mile": "mile", "miles": "mile", "mi": "mile",
        }
        
        from_unit = length_aliases.get(from_unit, from_unit)
        to_unit = length_aliases.get(to_unit, to_unit)
        
        # Metre'ye dönüştür
        to_meters = {
            "m": 1, "km": 0.001, "cm": 100, "mm": 1000,
            "inch": 39.3701, "ft": 3.28084, "yd": 1.09361, "mile": 0.000621371
        }
        
        if from_unit not in to_meters or to_unit not in to_meters:
            raise ValueError(f"Tanınmayan uzunluk birimi")
        
        # Metre cinsine dönüştür ve hedef birime dönüştür
        meters = value / to_meters[from_unit]
        result = meters * to_meters[to_unit]
        
        return round(result, 6)
    
    def _convert_weight(self, value: float, from_unit: str, to_unit: str) -> float:
        """Ağırlık birimlerini dönüştürür"""
        weight_aliases = {
            "kg": "kg", "kilogram": "kg", "kilograms": "kg", "kilogramme": "kg",
            "g": "g", "gram": "g", "grams": "g", "gramme": "g",
            "mg": "mg", "milligram": "mg", "milligrams": "mg", "milligramme": "mg",
            "lb": "lb", "pound": "lb", "pounds": "lb", "lbs": "lb",
            "oz": "oz", "ounce": "oz", "ounces": "oz",
            "ton": "ton", "tons": "ton", "tonne": "ton", "tonnes": "ton",
        }
        
        from_unit = weight_aliases.get(from_unit, from_unit)
        to_unit = weight_aliases.get(to_unit, to_unit)
        
        # KG cinsine dönüştür
        to_kg = {
            "kg": 1, "g": 1000, "mg": 1000000,
            "lb": 0.453592, "oz": 0.0283495, "ton": 0.001
        }
        
        if from_unit not in to_kg or to_unit not in to_kg:
            raise ValueError(f"Tanınmayan ağırlık birimi")
        
        kg = value / to_kg[from_unit]
        result = kg * to_kg[to_unit]
        
        return round(result, 6)
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Sıcaklık birimlerini dönüştürür"""
        temp_aliases = {
            "c": "celsius", "celsius": "celsius", "°c": "celsius",
            "f": "fahrenheit", "fahrenheit": "fahrenheit", "°f": "fahrenheit",
            "k": "kelvin", "kelvin": "kelvin",
        }
        
        from_unit = temp_aliases.get(from_unit, from_unit)
        to_unit = temp_aliases.get(to_unit, to_unit)
        
        # Celsius'a dönüştür
        if from_unit == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        else:
            celsius = value
        
        # Hedef birime dönüştür
        if to_unit == "fahrenheit":
            result = (celsius * 9/5) + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        else:
            result = celsius
        
        return round(result, 2)
    
    def _convert_currency(self, value: float, from_currency: str, to_currency: str) -> float:
        """Döviz kuru dönüştürür"""
        currency_aliases = {
            "usd": "usd", "dollar": "usd", "dolar": "usd", "$": "usd",
            "eur": "eur", "euro": "eur", "€": "eur",
            "gbp": "gbp", "pound": "gbp", "sterlin": "gbp", "£": "gbp",
            "try": "try", "tl": "try", "lira": "try", "₺": "try",
        }
        
        from_currency = currency_aliases.get(from_currency.lower(), from_currency.lower())
        to_currency = currency_aliases.get(to_currency.lower(), to_currency.lower())
        
        # USD'ye dönüştür
        to_usd = {
            "usd": 1, "eur": 1.1, "gbp": 1.27, "try": 0.0299
        }
        
        if from_currency not in to_usd or to_currency not in to_usd:
            raise ValueError(f"Tanınmayan döviz kuru: {from_currency} → {to_currency}")
        
        usd = value / to_usd[from_currency]
        result = usd * to_usd[to_currency]
        
        return round(result, 2)
    
    def _is_length_unit(self, unit: str) -> bool:
        """Uzunluk birimi mi kontrol eder"""
        length_units = {"m", "km", "cm", "mm", "inch", "ft", "yd", "mile", "in", "meter", "metre", "kilometer", "kilometre", "centimeter", "centimetre", "millimeter", "millimetre", "foot", "feet", "yard", "yards"}
        return unit.lower() in length_units
    
    def _is_weight_unit(self, unit: str) -> bool:
        """Ağırlık birimi mi kontrol eder"""
        weight_units = {"kg", "g", "mg", "lb", "oz", "ton", "kilogram", "gram", "milligram", "pound", "ounce", "tonne"}
        return unit.lower() in weight_units
    
    def _is_temperature_unit(self, unit: str) -> bool:
        """Sıcaklık birimi mi kontrol eder"""
        temp_units = {"c", "f", "k", "celsius", "fahrenheit", "kelvin", "°c", "°f"}
        return unit.lower() in temp_units
    
    def _is_currency(self, unit: str) -> bool:
        """Döviz kuru mu kontrol eder"""
        currencies = {"usd", "eur", "gbp", "try", "dollar", "dolar", "euro", "pound", "sterlin", "lira", "$", "€", "£", "₺"}
        return unit.lower() in currencies
