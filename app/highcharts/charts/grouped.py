"""Grouped chart implementation."""

from typing import Any, Dict, List, Optional

import polars as pl

from ..core.base_chart import BaseChart, ChartConfig


class GroupedChart(BaseChart):
    """Grouped chart implementation."""

    def _get_chart_type(self) -> str:
        return self.config["type"].split("-")[
            1
        ]  # Extract chart type from 'grouped-{type}'

    def get_series(self) -> Dict[str, Any]:
        """Generate series data for grouped charts."""
        try:
            # Get chart type (bar, column, area, line)
            chart_type = self._get_chart_type()

            # Configure y-axis offset based on chart type
            y_offset = 10
            if chart_type == "bar":
                y_offset = 5

            # Build base configuration
            result = {
                "chart": {"type": chart_type},
                "extraDataConfig": {"chartversion": "newGroupedVersion"},
                "xAxis": {
                    "scrollbar": {"enabled": True},
                    "labels": {
                        "x": -2,
                        "groupedOptions": [
                            {
                                "rotation": 0,
                                "style": {
                                    "color": "black",
                                    "textOverflow": "ellipsis",
                                    "whiteSpace": "nowrap",
                                    "width": 90,
                                    "fontSize": "11px",
                                    "overflow": "hidden",
                                },
                            }
                        ],
                        "step": 1,
                        "y": y_offset,
                        "rotation": 0,
                        "style": {
                            "color": "black",
                            "textOverflow": "ellipsis",
                            "fontSize": "8px",
                            "width": "50px",
                            "overflow": "hidden",
                            "whiteSpace": "nowrap",
                        },
                    },
                },
            }

            # Process x-axis categories
            categories, data = self._get_x_axis_with_category()
            result["xAxis"].update(categories)
            result["xAxis"]["max"] = max(0, len(data) - 1)

            # Build series data
            series = [
                {
                    "name": measure,
                    "data": [
                        [data_index[0], data_index[1]] for data_index in enumerate(data)
                    ],
                }
                for measure in [self.config["y"]]
            ]

            result["series"] = series

            return result

        except Exception as e:
            # Return empty chart on error
            return {"series": [], "chart": {"type": self._get_chart_type()}}

    def _get_x_axis_with_category(self) -> tuple[Dict[str, Any], List[float]]:
        """Build x-axis categories for grouped charts."""
        categories = {}
        data = []

        if self.config.get("x"):
            # Build nested categories from the dataframe
            x_categories = self._build_category_structure(
                self.df, self.config["x"], data
            )
            categories = {"categories": x_categories}

        return categories, data

    def _build_category_structure(
        self, df: pl.DataFrame, levels: List[str], data: List[float]
    ) -> List[Dict[str, Any]]:
        """Build nested category structure for grouped charts."""
        if not levels:
            return []

        current_level, *remaining_levels = levels
        values = df[current_level].unique().sort()

        def build_category(value: str) -> Dict[str, Any]:
            """Build a category node with its subcategories."""
            filtered_df = df.filter(pl.col(current_level) == value)
            subcategories = self._build_category_structure(
                filtered_df, remaining_levels, data
            )

            category = {"name": value}

            # Add subcategories if they exist
            if subcategories:
                category["categories"] = subcategories

            # Add data point if this is a leaf node
            if filtered_df.shape[0] == 1 and not subcategories:
                data.append(
                    list(filtered_df.select(self.config["y"]).iter_rows())[0][0]
                )

            return category

        return [build_category(value) for value in values.to_list()]
