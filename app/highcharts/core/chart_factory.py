"""Chart factory for creating chart instances based on type."""

from typing import Any, Dict, Optional, Type

import polars as pl

# Import all chart classes
from ..charts.basic import (AreaChart, AreaRangeChart, AreaStackChart,
                            AreaStackPercentChart, AreaStackSplineChart,
                            AreaStackSplinePercentChart, BarChart,
                            BarStackChart, BarStackPercentChart, ColumnChart,
                            ColumnStackChart, ColumnStackPercentChart,
                            LineChart, LollipopChart, SplineChart,
                            StackLollipopChart, StepAreaChart, SteplineChart)
from ..charts.boxplot import BoxplotChart, CustomBoxplotChart
from ..charts.funnel import FunnelChart, PyramidChart
from ..charts.grid import GridChart
from ..charts.grouped import GroupedChart
from ..charts.maps import (BubbleMapChart, HeatMapChart, MapChart,
                           ScatterMapChart)
from ..charts.pie import DonutChart, PieChart, SemiDonutChart, SunburstChart
from ..charts.polar import BubbleChart, ScatterChart, SplitBubbleChart
from ..charts.specialized import (BellCurveChart, HeatmapChart, ParetoChart,
                                  PredictionChart, StreamgraphChart,
                                  TreemapChart, TrendChart, WaterfallChart)
from .base_chart import BaseChart, ChartConfig


class ChartFactory:
    """Factory for creating chart instances."""

    _chart_registry: Dict[str, Type[BaseChart]] = {}

    @classmethod
    def register_chart(cls, chart_type: str, chart_class: Type[BaseChart]):
        """Register a chart type with its class."""
        cls._chart_registry[chart_type.lower()] = chart_class

    @classmethod
    def create_chart(
        cls, chart_type: str, df: pl.DataFrame, config: ChartConfig
    ) -> Optional[BaseChart]:
        """Create a chart instance based on the chart type."""
        chart_class = cls._chart_registry.get(chart_type.lower())
        if chart_class:
            return chart_class(df, config)
        return None

    @classmethod
    def get_chart_types(cls) -> list[str]:
        """Get list of all registered chart types."""
        return list(cls._chart_registry.keys())


# Register all chart types
def register_all_charts():
    """Register all chart types with the factory."""

    # Basic charts
    ChartFactory.register_chart("column", ColumnChart)
    ChartFactory.register_chart("bar", BarChart)
    ChartFactory.register_chart("line", LineChart)
    ChartFactory.register_chart("spline", SplineChart)
    ChartFactory.register_chart("area", AreaChart)
    ChartFactory.register_chart("area-stack", AreaStackChart)
    ChartFactory.register_chart("area-stack-spline", AreaStackSplineChart)
    ChartFactory.register_chart("area-range", AreaRangeChart)
    ChartFactory.register_chart("step-line", SteplineChart)
    ChartFactory.register_chart("step-area", StepAreaChart)
    ChartFactory.register_chart("area-stack-percent", AreaStackPercentChart)
    ChartFactory.register_chart(
        "area-stack-percent-spline", AreaStackSplinePercentChart
    )
    ChartFactory.register_chart("column-stack", ColumnStackChart)
    ChartFactory.register_chart("bar-stack", BarStackChart)
    ChartFactory.register_chart("column-stack-percent", ColumnStackPercentChart)
    ChartFactory.register_chart("bar-stack-percent", BarStackPercentChart)
    ChartFactory.register_chart("lollipop", LollipopChart)
    ChartFactory.register_chart("lollipop-stack", StackLollipopChart)

    # Pie charts
    ChartFactory.register_chart("pie", PieChart)
    ChartFactory.register_chart("donut", DonutChart)
    ChartFactory.register_chart("semi donut", SemiDonutChart)
    ChartFactory.register_chart("sunburst", SunburstChart)

    # Funnel charts
    ChartFactory.register_chart("funnel", FunnelChart)
    ChartFactory.register_chart("pyramid", PyramidChart)

    # Polar charts (scatter, bubble, etc.)
    ChartFactory.register_chart("scatter", ScatterChart)
    ChartFactory.register_chart("bubble", BubbleChart)
    ChartFactory.register_chart("split-bubble", SplitBubbleChart)

    # Boxplot charts
    ChartFactory.register_chart("boxplot", BoxplotChart)
    ChartFactory.register_chart("custom-boxplot", CustomBoxplotChart)

    # Specialized charts
    ChartFactory.register_chart("heatmap", HeatmapChart)
    ChartFactory.register_chart("treemap", TreemapChart)
    ChartFactory.register_chart("waterfall", WaterfallChart)
    ChartFactory.register_chart("bell-curve", BellCurveChart)
    ChartFactory.register_chart("streamgraph", StreamgraphChart)
    ChartFactory.register_chart("pareto", ParetoChart)
    ChartFactory.register_chart("trend", TrendChart)
    ChartFactory.register_chart("prediction", PredictionChart)

    # Map charts
    ChartFactory.register_chart("geo-map", MapChart)
    ChartFactory.register_chart("scatter-map", ScatterMapChart)
    ChartFactory.register_chart("bubble-map", BubbleMapChart)
    ChartFactory.register_chart("heat-map", HeatMapChart)

    # Other charts
    ChartFactory.register_chart("grid", GridChart)
    ChartFactory.register_chart("grouped-bar", GroupedChart)
    ChartFactory.register_chart("grouped-column", GroupedChart)
    ChartFactory.register_chart("grouped-area", GroupedChart)
    ChartFactory.register_chart("grouped-line", GroupedChart)


# Initialize the factory
register_all_charts()
