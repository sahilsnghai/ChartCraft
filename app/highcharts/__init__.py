"""Highcharts module for ChartCraft.

This module provides a comprehensive, class-based chart generation system
that supports multiple chart types with a clean, modular architecture.
"""

# Core components
from .core.base_chart import BaseChart, ChartConfig, ChartSeries, AxisConfig, DataProcessor
from .core.chart_factory import ChartFactory
from .core.tooltip_plot_options import TooltipBuilder, PlotOptionsBuilder

# Chart implementations
from .charts import (
    # Basic charts
    ColumnChart, BarChart, LineChart, SplineChart, AreaChart, 
    AreaStackChart, AreaStackSplineChart, AreaRangeChart, SteplineChart,
    StepAreaChart, AreaStackPercentChart, AreaStackSplinePercentChart,
    ColumnStackChart, BarStackChart, ColumnStackPercentChart, BarStackPercentChart,
    LollipopChart, StackLollipopChart,
    
    # Pie charts
    PieChart, DonutChart, SemiDonutChart, SunburstChart,
    
    # Funnel charts
    FunnelChart, PyramidChart,
    
    # Polar charts
    ScatterChart, BubbleChart, SplitBubbleChart,
    
    # Boxplot charts
    BoxplotChart, CustomBoxplotChart,
    
    # Specialized charts
    HeatmapChart, TreemapChart, WaterfallChart, BellCurveChart, 
    StreamgraphChart, ParetoChart, TrendChart, PredictionChart,
    
    # Map charts
    MapChart, ScatterMapChart, BubbleMapChart, HeatMapChart,
    
    # Other charts
    GridChart, GroupedChart
)

# Main generator function (backward compatible)
from .chartgenerator import generate_viz

# Version information
__version__ = "2.0.0"
__author__ = "ChartCraft Team"

# Public API
__all__ = [
    # Core components
    'BaseChart', 'ChartConfig', 'ChartSeries', 'AxisConfig', 'DataProcessor',
    'ChartFactory', 'TooltipBuilder', 'PlotOptionsBuilder',
    
    # Chart classes
    'ColumnChart', 'BarChart', 'LineChart', 'SplineChart', 'AreaChart',
    'AreaStackChart', 'AreaStackSplineChart', 'AreaRangeChart', 'SteplineChart',
    'StepAreaChart', 'AreaStackPercentChart', 'AreaStackSplinePercentChart',
    'ColumnStackChart', 'BarStackChart', 'ColumnStackPercentChart', 'BarStackPercentChart',
    'LollipopChart', 'StackLollipopChart',
    'PieChart', 'DonutChart', 'SemiDonutChart', 'SunburstChart',
    'FunnelChart', 'PyramidChart',
    'ScatterChart', 'BubbleChart', 'SplitBubbleChart',
    'BoxplotChart', 'CustomBoxplotChart',
    'HeatmapChart', 'TreemapChart', 'WaterfallChart', 'BellCurveChart',
    'StreamgraphChart', 'ParetoChart', 'TrendChart', 'PredictionChart',
    'MapChart', 'ScatterMapChart', 'BubbleMapChart', 'HeatMapChart',
    'GridChart', 'GroupedChart',
    
    # Main function
    'generate_viz',
    
    # Version
    '__version__', '__author__'
]