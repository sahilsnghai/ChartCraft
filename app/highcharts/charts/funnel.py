"""Funnel and pyramid chart implementations."""

from typing import Any, Dict, List, Optional

import polars as pl

from ..core.base_chart import (BaseChart, ChartConfig, ChartSeries,
                               DataProcessor)


class FunnelChartBase(BaseChart):
    """Base class for funnel and pyramid charts."""

    def __init__(self, df: pl.DataFrame, config: ChartConfig):
        super().__init__(df, config)
        self.x_col_distinct_values: List[str] = []

    def get_series(self) -> Dict[str, Any]:
        """Generate series data for funnel/pyramid charts."""
        # Process x column to create distinct values
        if self.config.get("x"):
            self._process_x_column()

        # Build the series data
        series_data = self._build_funnel_series()

        result = {"series": series_data, "chart": {"type": self.chart_type}}

        # Add axis configuration if x column exists
        if self.config.get("x"):
            result["xAxis"] = {"categories": self.x_col_distinct_values}

        return result

    def _process_x_column(self):
        """Process the x column to create indices and distinct values."""
        self.df, self.x_col_distinct_values = DataProcessor.replace_with_index(
            self.df, self.config["x"]
        )

    def _build_funnel_series(self) -> List[Dict[str, Any]]:
        """Build funnel series data."""
        # Sort data by y values in descending order for funnel visualization
        self.df = self.df.sort(by=self.config["y"], descending=True)

        # Extract names and values
        if self.config.get("x"):
            names = self.x_col_distinct_values
        else:
            names = self.df[self.config["y"]].to_list()

        values = self.df[self.config["y"]].to_list()

        # Create data points
        data = [{"name": name, "y": value} for name, value in zip(names, values)]

        return [
            {"type": self.chart_type, "name": self.config.get("y", ""), "data": data}
        ]


class FunnelChart(FunnelChartBase):
    """Funnel chart implementation."""

    def _get_chart_type(self) -> str:
        return "funnel"


class PyramidChart(FunnelChartBase):
    """Pyramid chart implementation."""

    def _get_chart_type(self) -> str:
        return "pyramid"
