"""Grid chart implementation."""

from typing import Any, Dict, List, Optional

import polars as pl

from ..core.base_chart import BaseChart, ChartConfig


class GridChart(BaseChart):
    """Grid chart implementation."""

    def _get_chart_type(self) -> str:
        return "grid"

    def get_series(self) -> Dict[str, Any]:
        """Generate grid configuration and data."""
        try:
            # Get grid configuration from config
            grid_config = self.config.get("gridConfig", {})

            # Build columns configuration
            columns = self._build_columns_config(grid_config)

            # Build result data
            result_data = self.df.to_numpy().tolist()

            return {"gridConfig": {"columns": columns}, "result": result_data}

        except Exception as e:
            # Return empty grid on error
            return {"gridConfig": {"columns": []}, "result": []}

    def _build_columns_config(
        self, grid_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build column configuration for the grid."""
        columns = []

        for idx, (col_name, dtype) in enumerate(self.df.schema.items()):
            if dtype in [pl.Float64, pl.Int64]:
                # Measure column
                column_config = self._get_measure_column_config(
                    col_name, idx, grid_config
                )
                # Add currency formatting if unit is specified
                if self.config.get("unit"):
                    column_config = self._add_currency_formatting(
                        column_config, self.config["unit"]
                    )
                columns.append(column_config)

            elif dtype in [pl.Utf8, pl.Boolean]:
                # Dimension column
                columns.append(
                    self._get_dimension_column_config(col_name, idx, grid_config)
                )

        return columns

    def _get_measure_column_config(
        self, col_name: str, idx: int, grid_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get configuration for measure columns."""
        col_config = grid_config.get(col_name, {})

        column = {
            "cellClassRules": {},
            "cellRenderer": col_config.get("cellRenderer", "agGridCallback"),
            "cellStyle": "cellStyleTemp",
            "cellStyleCopy": {},
            "class": col_config.get("class", "text-left"),
            "columnMapping": idx,
            "columnType": "measure",
            "ellipsis": col_config.get("ellipsis", False),
            "enablePivot": col_config.get("enablePivot", True),
            "enableRowGroup": col_config.get("enableRowGroup", True),
            "enableValue": col_config.get("enableValue", True),
            "field": f"k{idx}",
            "filter": col_config.get("filter", True),
            "flex": col_config.get("flex", 1),
            "header": {"actualName": col_name, "data": col_name},
            "headerClass": col_config.get("headerClass", "fontSize"),
            "headerName": col_config.get("headerName", col_name),
            "openLink": {"value": bool(col_config.get("openLink", False))},
            "headerTooltip": col_config.get("headerName", col_name),
            "isField": col_config.get("isField", True),
            "minWidth": col_config.get("minWidth", 150),
            "order": 1,
            "resizable": col_config.get("resizable", True),
            "showHeaderTooltip": col_config.get("showHeaderTooltip", True),
            "sortable": col_config.get("sortable", True),
            "style": {"cursor": "pointer"},
            "type": col_config.get("type", "rightAligned"),
            "visible": col_config.get("visible", True),
            "formatter": {
                "symbol": col_config.get("unit", ""),
                "symbolPosition": col_config.get("symbolPosition", "left"),
            },
            "showTotal": col_config.get("showTotal", False),
            "enableFormating": col_config.get("enableFormating", True),
            "showTotalStyle": {},
            "symbolPosition": col_config.get("symbolPosition", "left"),
            "headerAlign": col_config.get("headerAlign", "text-left"),
            "pivotTotals": col_config.get("pivotTotals", True),
            "autoHeight": col_config.get("autoHeight", True),
        }

        # Add conditional styling
        if col_config.get("backgroundColor") or col_config.get("borderStyle"):
            column["cellStyle"] = {}
            if col_config.get("borderStyle"):
                column["cellStyle"]["borderStyle"] = col_config["borderStyle"]
            if col_config.get("backgroundColor"):
                column["cellStyle"]["backgroundColor"] = col_config["backgroundColor"]

        # Add sorting configuration
        if col_config.get("sort"):
            column["sort"] = col_config["sort"]

        # Add open link configuration
        if col_config.get("openLink"):
            column["openLink"]["openValueAsLink"] = col_config["openLink"]

        return column

    def _get_dimension_column_config(
        self, col_name: str, idx: int, grid_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get configuration for dimension columns."""
        col_config = grid_config.get(col_name, {})

        return {
            "cellClassRules": {},
            "cellRenderer": col_config.get("cellRenderer", "agGridCallback"),
            "cellStyle": "cellStyleTemp",
            "cellStyleCopy": {},
            "class": col_config.get("class", "text-left"),
            "columnMapping": idx,
            "columnType": "dimension",
            "ellipsis": col_config.get("ellipsis", False),
            "enablePivot": col_config.get("enablePivot", True),
            "enableRowGroup": col_config.get("enableRowGroup", True),
            "enableValue": col_config.get("enableValue", True),
            "field": f"k{idx}",
            "filter": col_config.get("filter", True),
            "flex": col_config.get("flex", 1),
            "header": {"actualName": col_name, "data": col_name},
            "headerClass": col_config.get("headerClass", "fontSize"),
            "headerName": col_config.get("headerName", col_name),
            "openLink": {"value": bool(col_config.get("openLink", False))},
            "headerTooltip": col_config.get("headerName", col_name),
            "isField": col_config.get("isField", True),
            "minWidth": col_config.get("minWidth", 150),
            "order": 1,
            "resizable": col_config.get("resizable", True),
            "showHeaderTooltip": col_config.get("showHeaderTooltip", True),
            "sortable": col_config.get("sortable", True),
            "style": {"cursor": "pointer"},
            "type": col_config.get("type", "rightAligned"),
            "visible": col_config.get("visible", True),
            "formatter": {
                "symbol": col_config.get("unit", ""),
                "symbolPosition": col_config.get("symbolPosition", "left"),
            },
            "showTotal": col_config.get("showTotal", False),
            "enableFormating": col_config.get("enableFormating", True),
            "showTotalStyle": {},
            "symbolPosition": col_config.get("symbolPosition", "left"),
            "headerAlign": col_config.get("headerAlign", "text-left"),
            "pivotTotals": col_config.get("pivotTotals", True),
            "autoHeight": col_config.get("autoHeight", True),
        }

    def _add_currency_formatting(
        self, column_config: Dict[str, Any], unit: str
    ) -> Dict[str, Any]:
        """Add currency formatting to column configuration."""
        currency_map = {
            "€": "EUR",
            "kr": "SEK",
            "฿": "THB",
            "#": None,
            "Mex$": "MXN",
            "R$": "BRL",
            "A$": "AUD",
            "C$": "CAD",
            "$": "USD",
            "JP¥": "JPY",
            "₩": "KRW",
            "NT$": "TWD",
            "¥": "CNY",
            "₹": "INR",
            "£": "GBP",
            "zł": "PLN",
        }

        if unit in currency_map:
            currency_code = currency_map[unit]
            if currency_code:
                currency_format = f", {{style:'currency', currency:'{currency_code}'}}"
                column_config["valueFormatter"] = (
                    f"(value === null) ? null : value.toLocaleString('en-us'{currency_format})"
                )

        return column_config
