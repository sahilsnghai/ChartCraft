import pandas as pd


class Grid:
    def __init__(self, df, config):
        self.df: pd.DataFrame = df
        self.config: dict = config

    def currency_formatter(self, unit: str, config: dict) -> dict:
        """currency_formatter

        Args:
            unit (str):
            config (dict):

        Returns:
            dict:
        """
        currency = {
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
            "zł": "pdN",
        }
        if unit in currency.keys():
            currency_format = (
                currency.get(unit)
                and f", {{style:'currency', currency:'{currency.get(unit)}'}}"
            ) or ""
            config["valueFormatter"] = (
                f"(value === null) ? null : value.toLocaleString('en-us'{currency_format})"
            )
        return config

    def _grid_table_config(
        self,
        head_name,
        idx,
        col_type,
    ):
        grid_config = self.config.get("gridConfig",{}).get(head_name, {})

        col = {
            "cellClassRules": {},
            "cellRenderer": "agGridCallback",
            "cellStyle": "cellStyleTemp",
            "cellStyleCopy": {},
            "class": grid_config.get("class","text-left"),
            "columnMapping": idx,
            "columnType": col_type,
            "ellipsis":  grid_config.get("ellipsis", False),
            "enablePivot": True,
            "enableRowGroup": True,
            "enableValue": True,
            "field": f"k{idx}",
            "filter": True,
            "flex": 1,
            "header": {"actualName": head_name, "data": head_name},
            "headerClass": "fontSize",
            "headerName": head_name,
            "openLink": {"value": False},
            "headerTooltip": head_name,
            "isField": True,
            "minWidth": grid_config.get("minWidth", 150),
            "order": 1,
            "resizable": True,
            "showHeaderTooltip": True,
            "sortable": True,
            "style": {"cursor": "pointer"},
            "type": "rightAligned",
            "visible": True,
            "formatter": {"symbol": grid_config.get("unit",""), "symbolPosition": grid_config.get("symbolPosition","left")},
            "showTotal": False,
            "enableFormating": True,
            "showTotalStyle": {},
            "symbolPosition": grid_config.get("symbolPosition","left"),
            "headerAlign": grid_config.get("headerAlign","text-left"),
            "pivotTotals": True,
            "autoHeight": True,
        }

        grid_config.get("borderStyle") and col.update({"cellStyle":{"borderStyle": grid_config.get("borderStyle")}})
        grid_config.get("sort") and col.update({"sort":grid_config.get("sort")})
        grid_config.get("openLink") and col.update({"openLink":{ "value":True,"openValueAsLink": grid_config.get("openLink")}})

        return col

    def grid_config(self) -> dict[str, list]:
        measure, dimension = [], []
        for idx, (col_name, dtype) in enumerate(self.df.schema.items()):
            if dtype in [pd.Float64Dtype, pd.Int64Dtype]:

                col = self._grid_table_config(
                    head_name=col_name,
                    col_type="measure",
                    idx=idx,
                    unit=self.config.get("unit"),
                )
                col = self.currency_formatter(self.config.get("unit"), col)
                measure.append(col)

            elif dtype in [pd.StringDtype, pd.BooleanDtype]:
                dimension.append(
                    self._grid_table_config(
                    head_name=col_name,
                    col_type="dimension",
                    idx=idx,
                )
                )

        dimension.extend(measure)
        return {
            "gridConfig": {"columns": dimension},
            "result": self.df.to_numpy().tolist(),
        }
