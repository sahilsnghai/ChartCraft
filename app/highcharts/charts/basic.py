"""Basic chart implementations."""

from typing import Any, Dict, List, Optional

import polars as pl

from ..core.base_chart import (AxisConfig, BaseChart, ChartConfig, ChartSeries,
                               DataProcessor)


class BasicCartesianChart(BaseChart):
    """Base class for cartesian coordinate system charts."""

    def __init__(self, df: pl.DataFrame, config: ChartConfig, x_axis_position: int = 0):
        super().__init__(df, config)
        self.x_axis_position = x_axis_position
        self.x_col_distinct_values: List[str] = []

    def get_series(self) -> Dict[str, Any]:
        """Generate series data for cartesian charts."""
        if self.config.get("x"):
            self._process_x_column()

        series_data = self._build_series()

        result = {"series": series_data, "chart": {"type": self.chart_type}}

        if self.config.get("x"):
            axis_config = AxisConfig(self.df, self.config)
            result["xAxis"] = axis_config.get_x_axis(self.x_col_distinct_values)
            result["yAxis"] = axis_config.get_y_axis()
        else:
            # Handle case where there's no x column (measures only)
            result.update(self._get_measures_config())

        return result

    def _process_x_column(self):
        """Process the x column to create indices and distinct values."""
        self.df, self.x_col_distinct_values = DataProcessor.replace_with_index(
            self.df, self.config["x"]
        )

    def _build_series(self) -> List[Dict[str, Any]]:
        """Build series data based on whether color column is present."""
        if self.config.get("color") in self.df.columns:
            return self._get_series_with_color_column()
        else:
            return self._get_series_without_color()

    def _get_series_with_color_column(self) -> List[Dict[str, Any]]:
        """Build series when color column defines series."""
        series_list = []

        # Group by color column to create separate series
        grouped = self.df.group_by([self.config["color"]], maintain_order=True)

        for group_name, group_df in grouped:
            # Extract the actual group name (handle both string and tuple cases)
            if isinstance(group_name, tuple):
                group_name = group_name[0]

            # Build data points
            data = [
                [row[0], row[1]]  # [x_index, y_value]
                for row in group_df.select(
                    [self.config["x"], self.config["y"]]
                ).iter_rows()
            ]

            series = ChartSeries(
                series_type=self.chart_type,
                data=data,
                name=str(group_name),
                xAxis=self.x_axis_position,
            )
            series_list.append(series.to_dict())

        return series_list

    def _get_series_without_color(self) -> List[Dict[str, Any]]:
        """Build series when no color column is present."""
        # Build single series with all data
        data = [
            [row[0], row[1]]  # [x_index, y_value]
            for row in self.df.select([self.config["x"], self.config["y"]]).iter_rows()
        ]

        series_name = self.config.get("yAxisLabel", self.config.get("y", ""))
        series = ChartSeries(
            series_type=self.chart_type,
            data=data,
            name=series_name,
            xAxis=self.x_axis_position,
        )

        return [series.to_dict()]

    def _get_measures_config(self) -> Dict[str, Any]:
        """Handle configuration when only measures are present (no x column)."""
        # Convert data to format expected for measures-only charts
        values = list(self.df.select(self.config["y"]).iter_rows())[0]
        data = [[i, val] for i, val in enumerate(values)]

        series_name = self.config.get("yAxisLabel", self.config.get("y", ""))
        series = ChartSeries(series_type=self.chart_type, data=data, name=series_name)

        # Create categories from measure names
        categories = (
            self.config["y"]
            if isinstance(self.config["y"], list)
            else [self.config["y"]]
        )

        return {
            "series": [series.to_dict()],
            "xAxis": {"categories": categories},
            "yAxis": {
                "title": {"text": ", ".join(categories[:-1]) + f" and {categories[-1]}"}
            },
        }


class ColumnChart(BasicCartesianChart):
    """Column chart implementation."""

    def _get_chart_type(self) -> str:
        return "column"


class BarChart(BasicCartesianChart):
    """Bar chart implementation."""

    def _get_chart_type(self) -> str:
        return "bar"


class LineChart(BasicCartesianChart):
    """Line chart implementation."""

    def _get_chart_type(self) -> str:
        return "line"

    def get_series(self) -> Dict[str, Any]:
        """Generate series with line-specific configurations."""
        result = super().get_series()

        # Add line-specific series configurations
        for series in result["series"]:
            series["label"] = {"enabled": False}

        return result


class SplineChart(LineChart):
    """Spline chart implementation."""

    def _get_chart_type(self) -> str:
        return "spline"


class SteplineChart(LineChart):
    """Step line chart implementation."""

    def _get_chart_type(self) -> str:
        return "line"

    def get_series(self) -> Dict[str, Any]:
        """Generate series with step line configuration."""
        result = super().get_series()

        # Add step configuration to all series
        for series in result["series"]:
            series["step"] = "left"

        return result


class AreaChart(BasicCartesianChart):
    """Area chart implementation."""

    def _get_chart_type(self) -> str:
        return "area"


class AreaSplineChart(AreaChart):
    """Area spline chart implementation."""

    def _get_chart_type(self) -> str:
        return "areaspline"


class StepAreaChart(AreaChart):
    """Step area chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with step area configuration."""
        result = super().get_series()

        # Add step configuration to all series
        for series in result["series"]:
            series["step"] = "left"

        return result


class AreaStackChart(AreaChart):
    """Stacked area chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with stacking configuration."""
        result = super().get_series()

        # Add stacking configuration
        for series in result["series"]:
            series["stacking"] = "normal"

        return result


class AreaStackSplineChart(AreaSplineChart):
    """Stacked area spline chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with stacking configuration."""
        result = super().get_series()

        # Add stacking configuration
        for series in result["series"]:
            series["stacking"] = "normal"

        return result


class AreaStackPercentChart(AreaChart):
    """Stacked area percent chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with percent stacking configuration."""
        result = super().get_series()

        # Add percent stacking configuration
        for series in result["series"]:
            series["stacking"] = "percent"

        return result


class AreaStackSplinePercentChart(AreaSplineChart):
    """Stacked area spline percent chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with percent stacking configuration."""
        result = super().get_series()

        # Add percent stacking configuration
        for series in result["series"]:
            series["stacking"] = "percent"

        return result


class AreaRangeChart(BasicCartesianChart):
    """Area range chart implementation."""

    def _get_chart_type(self) -> str:
        return "arearange"

    def __init__(self, df: pl.DataFrame, config: ChartConfig, x_axis_position: int = 0):
        # Process deviation configuration to create lower and upper bounds
        self._process_deviation_config(df, config)
        super().__init__(df, config, x_axis_position)

    def _process_deviation_config(self, df: pl.DataFrame, config: ChartConfig):
        """Process deviation configuration to create lower and upper y values."""
        y_col = config["y"]
        lower_y = f"lower-{y_col}"
        upper_y = f"upper-{y_col}"

        deviation_config = config.get("deviation", {})
        deviation_type = deviation_config.get("type")
        deviation_value = deviation_config.get("value", 0)

        if deviation_type == "percent":
            # Calculate percentage-based deviation
            y_modified = [
                (pl.col(y_col) * (1 - deviation_value / 100)).alias(lower_y),
                (pl.col(y_col) * (1 + deviation_value / 100)).alias(upper_y),
            ]
        elif deviation_type == "normal":
            # Calculate fixed value deviation
            y_modified = [
                (pl.col(y_col) - deviation_value).alias(lower_y),
                (pl.col(y_col) + deviation_value).alias(upper_y),
            ]
        elif deviation_type == "stddev":
            # Calculate standard deviation-based deviation
            y_modified = [
                (pl.col(y_col) - pl.col(y_col).std()).alias(lower_y),
                (pl.col(y_col) + pl.col(y_col).std()).alias(upper_y),
            ]
        else:
            # Use explicit lower_y and upper_y columns if provided
            lower_y = config.get("lower_y", y_col)
            upper_y = config.get("upper_y", y_col)
            y_modified = [
                pl.col(lower_y).alias(lower_y),
                pl.col(upper_y).alias(upper_y),
            ]

        # Apply the transformations
        self.df = df.lazy().with_columns(*y_modified).collect()

        # Update config with the new y columns
        config.raw["y"] = [lower_y, upper_y]
        config.raw["yAxisLabel"] = y_col


class StackLollipopChart(BasicCartesianChart):
    """Stacked lollipop chart implementation."""

    def _get_chart_type(self) -> str:
        return "lollipop"

    def get_series(self) -> Dict[str, Any]:
        """Generate series with stacking configuration."""
        result = super().get_series()

        # Add stacking configuration
        for series in result["series"]:
            series["stacking"] = "normal"

        return result


class LollipopChart(BasicCartesianChart):
    """Lollipop chart implementation."""

    def _get_chart_type(self) -> str:
        return "lollipop"


class ColumnStackChart(ColumnChart):
    """Stacked column chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with stacking configuration."""
        result = super().get_series()

        # Add stacking configuration
        for series in result["series"]:
            series["stacking"] = "normal"

        return result


class BarStackChart(BarChart):
    """Stacked bar chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with stacking configuration."""
        result = super().get_series()

        # Add stacking configuration
        for series in result["series"]:
            series["stacking"] = "normal"

        return result


class ColumnStackPercentChart(ColumnChart):
    """Stacked column percent chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with percent stacking configuration."""
        result = super().get_series()

        # Add percent stacking configuration
        for series in result["series"]:
            series["stacking"] = "percent"

        return result


class BarStackPercentChart(BarChart):
    """Stacked bar percent chart implementation."""

    def get_series(self) -> Dict[str, Any]:
        """Generate series with percent stacking configuration."""
        result = super().get_series()

        # Add percent stacking configuration
        for series in result["series"]:
            series["stacking"] = "percent"

        return result
