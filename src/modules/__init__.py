"""Modules package for Calculator Agent"""

from .calculus import CalculusModule
from .linear_algebra import LinearAlgebraModule
from .basic_math import BasicMathModule
from .financial import FinancialModule
from .equation_solver import EquationSolverModule
from .graph_plotter import GraphPlotterModule
from .unit_converter import UnitConverterModule

__all__ = [
    "CalculusModule",
    "LinearAlgebraModule",
    "BasicMathModule",
    "FinancialModule",
    "EquationSolverModule",
    "GraphPlotterModule",
    "UnitConverterModule",
]
