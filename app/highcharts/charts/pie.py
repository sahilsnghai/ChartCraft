"""Pie chart implementations."""

from typing import Any, Dict, List, Optional

import polars as pl

from ..core.base_chart import BaseChart, ChartConfig, ChartSeries


class PieChartBase(BaseChart):
    """Base class for pie chart implementations."""

    def __init__(self, df: pl.DataFrame, config: ChartConfig):
        super().__init__(df, config)
        self.x_col_distinct_values: List[str] = []

    def get_series(self) -> Dict[str, Any]:
        """Generate series data for pie charts."""
        # Process x column to create distinct values
        if self.config.get("x"):
            self._process_x_column()

        # Build the series data
        series_data = self._build_pie_series()

        result = {"series": series_data, "chart": {"type": self.chart_type}}

        # Add axis configuration if x column exists
        if self.config.get("x"):
            result["xAxis"] = {"categories": self.x_col_distinct_values}

        return result

    def _process_x_column(self):
        """Process the x column to create indices and distinct values."""
        from ..core.base_chart import DataProcessor

        self.df, self.x_col_distinct_values = DataProcessor.replace_with_index(
            self.df, self.config["x"]
        )

    def _build_pie_series(self) -> List[Dict[str, Any]]:
        """Build pie series data."""
        # Sort data by x values for consistent ordering
        self.df = self.df.sort(by=self.config["x"])

        # Extract names and values
        names = (
            self.x_col_distinct_values
            if self.config.get("x")
            else self.df[self.config["y"]].to_list()
        )
        values = self.df[self.config["y"]].to_list()

        # Create data points
        data = [{"name": name, "y": value} for name, value in zip(names, values)]

        return [
            {"type": self.chart_type, "name": self.config.get("y", ""), "data": data}
        ]


class PieChart(PieChartBase):
    """Standard pie chart implementation."""

    def _get_chart_type(self) -> str:
        return "pie"


class DonutChart(PieChartBase):
    """Donut chart implementation."""

    def _get_chart_type(self) -> str:
        return "pie"

    def get_series(self) -> Dict[str, Any]:
        """Generate series with donut configuration."""
        result = super().get_series()

        # Add donut-specific configuration
        result["series"][0]["innerSize"] = "30%"

        return result


class SemiDonutChart(PieChartBase):
    """Semi donut chart implementation."""

    def _get_chart_type(self) -> str:
        return "pie"

    def get_series(self) -> Dict[str, Any]:
        """Generate series with semi donut configuration."""
        result = super().get_series()

        # Add semi donut-specific configuration
        result["series"][0].update(
            {
                "innerSize": "30%",
                "startAngle": -90,
                "endAngle": 90,
                "center": ["50%", "75%"],
                "size": "110%",
            }
        )

        return result


class SunburstChart(BaseChart):
    """Sunburst chart implementation."""

    def _get_chart_type(self) -> str:
        return "sunburst"

    def get_series(self) -> Dict[str, Any]:
        """Generate series data for sunburst charts."""
        # Sort data for consistent ordering
        self.df = self.df.sort(by=[self.config["x"], self.config["color"]])

        # Get distinct values for parent and child levels
        parent_names = self.df[self.config["x"]].unique().sort().to_list()
        child_names = self.df[self.config["color"]].unique().sort().to_list()

        # Calculate parent values (sum by x)
        parent_values = (
            self.df.group_by(self.config["x"])
            .sum()
            .sort(by=self.config["x"])[self.config["y"]]
            .to_list()
        )

        # Build parent-child data structure
        parent_data = []

        for i, parent_name in enumerate(parent_names):
            # Add parent node
            parent_data.append(
                {"id": str(i), "name": parent_name, "value": parent_values[i]}
            )

            # Add child nodes for this parent
            child_data = self.df.filter(self.df[self.config["x"]] == i)
            child_values = child_data[self.config["y"]].to_list()

            for j, child_name in enumerate(child_names):
                parent_data.append(
                    {"name": child_name, "parent": str(i), "value": child_values[j]}
                )

        result = {
            "series": [
                {
                    "type": "sunburst",
                    "data": parent_data,
                    "allowDrillToNode": True,
                    "levels": [
                        {"level": 1, "levelIsConstant": False},
                        {"level": 2, "colorByPoint": True},
                    ],
                }
            ],
            "chart": {"type": self.chart_type},
        }

        return result
