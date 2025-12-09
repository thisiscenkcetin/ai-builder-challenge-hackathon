"""Unit Converter Module Tests"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.modules.unit_converter import UnitConverterModule
from src.schemas.models import CalculationResult


@pytest.fixture
def mock_gemini_agent():
    """Mock Gemini Agent for testing"""
    mock = AsyncMock()
    mock.generate_json_response = AsyncMock(
        return_value={
            "result": 0.621371,
            "steps": ["1 km = 0.621371 miles"],
            "confidence_score": 1.0
        }
    )
    return mock


@pytest.fixture
def unit_converter_module(mock_gemini_agent):
    """Unit Converter Module instance for testing"""
    return UnitConverterModule(mock_gemini_agent)


class TestUnitConverterParsing:
    """Test expression parsing"""
    
    def test_parse_km_to_miles(self, unit_converter_module):
        """Test parsing 'km to miles' format"""
        value, from_unit, to_unit = unit_converter_module._parse_conversion_expression(
            "100 km to miles"
        )
        assert value == 100
        assert from_unit == "km"
        assert to_unit == "miles"
    
    def test_parse_celsius_to_fahrenheit(self, unit_converter_module):
        """Test parsing temperature conversion"""
        value, from_unit, to_unit = unit_converter_module._parse_conversion_expression(
            "25 celsius to fahrenheit"
        )
        assert value == 25
        assert from_unit == "celsius"
        assert to_unit == "fahrenheit"
    
    def test_parse_decimal_values(self, unit_converter_module):
        """Test parsing decimal values"""
        value, from_unit, to_unit = unit_converter_module._parse_conversion_expression(
            "3.5 kg to lb"
        )
        assert value == 3.5
        assert from_unit == "kg"
        assert to_unit == "lb"
    
    def test_parse_invalid_expression(self, unit_converter_module):
        """Test parsing invalid expression raises error"""
        with pytest.raises(ValueError):
            unit_converter_module._parse_conversion_expression("invalid input")


class TestLengthConversions:
    """Test length unit conversions"""
    
    def test_km_to_miles(self, unit_converter_module):
        """Test km to miles conversion"""
        result = unit_converter_module._convert_length(1, "km", "mile")
        assert abs(result - 0.621371) < 0.01
    
    def test_m_to_cm(self, unit_converter_module):
        """Test m to cm conversion"""
        result = unit_converter_module._convert_length(1, "m", "cm")
        assert result == 100
    
    def test_inch_to_cm(self, unit_converter_module):
        """Test inch to cm conversion"""
        result = unit_converter_module._convert_length(1, "inch", "cm")
        assert abs(result - 2.54) < 0.01
    
    def test_ft_to_m(self, unit_converter_module):
        """Test feet to meters conversion"""
        result = unit_converter_module._convert_length(1, "ft", "m")
        assert abs(result - 0.3048) < 0.001
    
    def test_invalid_length_units(self, unit_converter_module):
        """Test invalid length units raise error"""
        with pytest.raises(ValueError):
            unit_converter_module._convert_length(1, "invalid", "m")


class TestWeightConversions:
    """Test weight unit conversions"""
    
    def test_kg_to_lb(self, unit_converter_module):
        """Test kg to pounds conversion"""
        result = unit_converter_module._convert_weight(1, "kg", "lb")
        assert abs(result - 2.20462) < 0.01
    
    def test_g_to_mg(self, unit_converter_module):
        """Test g to mg conversion"""
        result = unit_converter_module._convert_weight(1, "g", "mg")
        assert result == 1000
    
    def test_lb_to_kg(self, unit_converter_module):
        """Test pounds to kg conversion"""
        result = unit_converter_module._convert_weight(1, "lb", "kg")
        assert abs(result - 0.453592) < 0.01
    
    def test_ton_to_kg(self, unit_converter_module):
        """Test ton to kg conversion"""
        result = unit_converter_module._convert_weight(1, "ton", "kg")
        assert abs(result - 1000) < 1
    
    def test_invalid_weight_units(self, unit_converter_module):
        """Test invalid weight units raise error"""
        with pytest.raises(ValueError):
            unit_converter_module._convert_weight(1, "invalid", "kg")


class TestTemperatureConversions:
    """Test temperature conversions"""
    
    def test_celsius_to_fahrenheit(self, unit_converter_module):
        """Test Celsius to Fahrenheit conversion"""
        result = unit_converter_module._convert_temperature(0, "celsius", "fahrenheit")
        assert result == 32
    
    def test_fahrenheit_to_celsius(self, unit_converter_module):
        """Test Fahrenheit to Celsius conversion"""
        result = unit_converter_module._convert_temperature(32, "fahrenheit", "celsius")
        assert result == 0
    
    def test_celsius_to_kelvin(self, unit_converter_module):
        """Test Celsius to Kelvin conversion"""
        result = unit_converter_module._convert_temperature(0, "celsius", "kelvin")
        assert abs(result - 273.15) < 0.01
    
    def test_kelvin_to_celsius(self, unit_converter_module):
        """Test Kelvin to Celsius conversion"""
        result = unit_converter_module._convert_temperature(273.15, "kelvin", "celsius")
        assert abs(result - 0) < 0.01
    
    def test_boiling_point_conversion(self, unit_converter_module):
        """Test water boiling point conversion"""
        result = unit_converter_module._convert_temperature(100, "celsius", "fahrenheit")
        assert result == 212


class TestUnitDetection:
    """Test unit type detection"""
    
    def test_is_length_unit(self, unit_converter_module):
        """Test length unit detection"""
        assert unit_converter_module._is_length_unit("km")
        assert unit_converter_module._is_length_unit("mile")
        assert not unit_converter_module._is_length_unit("kg")
    
    def test_is_weight_unit(self, unit_converter_module):
        """Test weight unit detection"""
        assert unit_converter_module._is_weight_unit("kg")
        assert unit_converter_module._is_weight_unit("lb")
        assert not unit_converter_module._is_weight_unit("km")
    
    def test_is_temperature_unit(self, unit_converter_module):
        """Test temperature unit detection"""
        assert unit_converter_module._is_temperature_unit("celsius")
        assert unit_converter_module._is_temperature_unit("fahrenheit")
        assert not unit_converter_module._is_temperature_unit("km")
    
    def test_is_currency(self, unit_converter_module):
        """Test currency detection"""
        assert unit_converter_module._is_currency("usd")
        assert unit_converter_module._is_currency("try")
        assert not unit_converter_module._is_currency("km")


class TestCurrencyConversions:
    """Test currency conversions"""
    
    def test_usd_to_try(self, unit_converter_module):
        """Test USD to TRY conversion"""
        result = unit_converter_module._convert_currency(1, "usd", "try")
        assert isinstance(result, float)
        assert result > 30  # Should be around 33.50
    
    def test_eur_to_gbp(self, unit_converter_module):
        """Test EUR to GBP conversion"""
        result = unit_converter_module._convert_currency(1, "eur", "gbp")
        assert isinstance(result, float)
    
    def test_currency_aliases(self, unit_converter_module):
        """Test currency alias resolution"""
        result1 = unit_converter_module._convert_currency(1, "usd", "try")
        result2 = unit_converter_module._convert_currency(1, "dollar", "lira")
        assert abs(result1 - result2) < 0.01


@pytest.mark.asyncio
async def test_calculate_length_conversion(unit_converter_module):
    """Test async calculate method for length conversion"""
    result = await unit_converter_module.calculate("100 km to miles")
    
    assert isinstance(result, CalculationResult)
    assert result.domain == "unit_converter"
    assert result.confidence_score == 1.0
    assert len(result.steps) > 0


@pytest.mark.asyncio
async def test_calculate_temperature_conversion(unit_converter_module):
    """Test async calculate method for temperature conversion"""
    result = await unit_converter_module.calculate("25 celsius to fahrenheit")
    
    assert isinstance(result, CalculationResult)
    assert result.domain == "unit_converter"
    assert result.confidence_score == 1.0


@pytest.mark.asyncio
async def test_calculate_with_invalid_input(unit_converter_module):
    """Test calculate method with invalid input"""
    with pytest.raises(Exception):
        await unit_converter_module.calculate("invalid input")


class TestUnitConverterIntegration:
    """Integration tests for Unit Converter"""
    
    def test_get_domain_prompt(self, unit_converter_module):
        """Test domain prompt retrieval"""
        prompt = unit_converter_module._get_domain_prompt()
        assert "unit_converter" in prompt.lower() or "birim" in prompt.lower()
        assert "{expression}" in prompt
    
    def test_multiple_conversions(self, unit_converter_module):
        """Test multiple conversions in sequence"""
        conversions = [
            (1, "km", "mile"),
            (100, "celsius", "fahrenheit"),
            (1, "kg", "lb"),
        ]
        
        for value, from_unit, to_unit in conversions:
            result = unit_converter_module._convert_units(value, from_unit, to_unit)
            assert isinstance(result, (int, float))
            assert result > 0
