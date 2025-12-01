"""Highcharts module for ChartCraft.

This module provides a comprehensive, class-based chart generation system
that supports multiple chart types with a clean, modular architecture.
"""

# Main generator function (backward compatible)
from .chartgenerator import generate_viz
# Chart implementations
from .charts import (  # Basic charts; Pie charts; Funnel charts; Polar charts; Boxplot charts; Specialized charts; Map charts; Other charts
    AreaChart, AreaRangeChart, AreaStackChart, AreaStackPercentChart,
    AreaStackSplineChart, AreaStackSplinePercentChart, BarChart, BarStackChart,
    BarStackPercentChart, BellCurveChart, BoxplotChart, BubbleChart,
    BubbleMapChart, ColumnChart, ColumnStackChart, ColumnStackPercentChart,
    CustomBoxplotChart, DonutChart, FunnelChart, GridChart, GroupedChart,
    HeatmapChart, HeatMapChart, LineChart, LollipopChart, MapChart,
    ParetoChart, PieChart, PredictionChart, PyramidChart, ScatterChart,
    ScatterMapChart, SemiDonutChart, SplineChart, SplitBubbleChart,
    StackLollipopChart, StepAreaChart, SteplineChart, StreamgraphChart,
    SunburstChart, TreemapChart, TrendChart, WaterfallChart)
# Core components
from .core.base_chart import (AxisConfig, BaseChart, ChartConfig, ChartSeries,
                              DataProcessor)
from .core.chart_factory import ChartFactory
from .core.tooltip_plot_options import PlotOptionsBuilder, TooltipBuilder

# Version information
__version__ = "2.0.0"
__author__ = "ChartCraft Team"

# Public API
__all__ = [
    # Core components
    "BaseChart",
    "ChartConfig",
    "ChartSeries",
    "AxisConfig",
    "DataProcessor",
    "ChartFactory",
    "TooltipBuilder",
    "PlotOptionsBuilder",
    # Chart classes
    "ColumnChart",
    "BarChart",
    "LineChart",
    "SplineChart",
    "AreaChart",
    "AreaStackChart",
    "AreaStackSplineChart",
    "AreaRangeChart",
    "SteplineChart",
    "StepAreaChart",
    "AreaStackPercentChart",
    "AreaStackSplinePercentChart",
    "ColumnStackChart",
    "BarStackChart",
    "ColumnStackPercentChart",
    "BarStackPercentChart",
    "LollipopChart",
    "StackLollipopChart",
    "PieChart",
    "DonutChart",
    "SemiDonutChart",
    "SunburstChart",
    "FunnelChart",
    "PyramidChart",
    "ScatterChart",
    "BubbleChart",
    "SplitBubbleChart",
    "BoxplotChart",
    "CustomBoxplotChart",
    "HeatmapChart",
    "TreemapChart",
    "WaterfallChart",
    "BellCurveChart",
    "StreamgraphChart",
    "ParetoChart",
    "TrendChart",
    "PredictionChart",
    "MapChart",
    "ScatterMapChart",
    "BubbleMapChart",
    "HeatMapChart",
    "GridChart",
    "GroupedChart",
    # Main function
    "generate_viz",
    # Version
    "__version__",
    "__author__",
]
