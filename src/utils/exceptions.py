"""Custom exceptions for Calculator Agent"""

class CalculationError(Exception):
    """Base exception for calculation errors"""
    pass


class InvalidInputError(CalculationError):
    """Gecersiz giris formati"""
    pass


class GeminiAPIError(CalculationError):
    """Gemini API'den donen hata"""
    pass


class SecurityViolationError(CalculationError):
    """Guvenlik ihlali tespit edildi"""
    pass


class ModuleNotFoundError(CalculationError):
    """Modul bulunamadi"""
    pass

