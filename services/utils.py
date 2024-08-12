
import json, numpy as np, decimal, datetime
from typing import Any, Callable

import sys
import json

# below package are helpfull to display chart locally DO Not push the to upstream / uncommented
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl


attribute_dict = {
    "color": [
        "#FF0000",
        "#00FF00",
        "#0000FF",
        "#00FFFF",
        "#FF00FF",
        "#FFFF00",
        "#FFA500",
        "#800080",
        "#008080",
        "#FFC0CB",
        "#00FF00",
        "#E6E6FA",
        "#A52A2A",
        "#800000",
        "#808000",
        "#000080",
        "#4B0082",
        "#40E0D0",
        "#C0C0C0",
        "#FFD700",
    ],
    "currency" : {
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
}

class DefaultEncoder(json.JSONEncoder):
    """DefaultEncoder class"""

    def default(self, obj):
        """

        Parameters
        ----------
        obj
        """
        if isinstance(obj, (datetime.datetime, datetime.date)):
            resp = obj.__str__()
        elif isinstance(obj, decimal.Decimal):
            resp = obj.__float__()
        elif isinstance(obj, np.integer):
            resp = int(obj)
        elif isinstance(obj, np.floating):
            resp = float(obj)
        elif isinstance(obj, np.ndarray):
            resp = obj.tolist()
        else:
            resp = json.JSONEncoder.default(self, obj)
        return resp

stacked_plot_options = {
    "stacked line": {"line": {"stacking": "normal"}},
    "stacked column": {"column": {"stacking": "normal"}},
    "stacked bar": {"bar": {"stacking": "normal"}},
    "stacked area": {"area": {"stacking": "normal"}},
    "100% stacked line": {"line": {"stacking": "percent"}},
    "100% stacked column": {"column": {"stacking": "percent"}},
    "100% stacked bar": {"bar": {"stacking": "percent"}},
    "100% stacked area": {"area": {"stacking": "percent"}},
}

x_axis_options = {
    "grouped column": {
        "labels": {
            "groupedOptions": [
                {
                    "rotation": -90,
                    "style": {
                        "color": "#00008B",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "width": 40,
                        "fontSize": "20px",
                    },
                }
            ],
            "step": 1,
            "y": 6,
            "rotation": 0,
            "style": {
                "color": "black",
                "textOverflow": "ellipsis",
                "fontSize": "16px",
                "width": 90,
            },
        }
    },
    "grouped bar": {
        "labels": {
            "groupedOptions": [
                {
                    "rotation": -90,
                    "style": {
                        "color": "#00008B",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "width": 40,
                        "fontSize": "20px",
                    },
                }
            ],
            "step": 1,
            "y": 6,
            "rotation": 0,
            "style": {
                "color": "black",
                "textOverflow": "ellipsis",
                "fontSize": "16px",
                "width": 90,
            },
        }
    },
    "grouped line": {
        "labels": {
            "groupedOptions": [
                {
                    "rotation": -90,
                    "style": {
                        "color": "#00008B",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "width": 40,
                        "fontSize": "20px",
                    },
                }
            ],
            "step": 1,
            "y": 6,
            "rotation": 0,
            "style": {
                "color": "black",
                "textOverflow": "ellipsis",
                "fontSize": "16px",
                "width": 90,
            },
        }
    },
    "grouped area": {
        "labels": {
            "groupedOptions": [
                {
                    "rotation": -90,
                    "style": {
                        "color": "#00008B",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "width": 40,
                        "fontSize": "20px",
                    },
                }
            ],
            "step": 1,
            "y": 6,
            "rotation": 0,
            "style": {
                "color": "black",
                "textOverflow": "ellipsis",
                "fontSize": "16px",
                "width": 90,
            },
        }
    },
}

CHART_CONFIG = {
    "chart": {"zoomType": "xy"},
    "legend":{"maxHeight":50},
    "credits": False,
    "plotOptions": {},
    "title": {"text": ""},
    "xAxis": [],
    "yAxis": [],
    "series": [],
    "boost": {"enabled": True, "useGPUTranslations": True},
    "accessibility": {
        "enabled": False
    }
}

def update_config(place_in: list, value: Any, chart_config: dict | list) -> dict|list:
    """update_config Update Chart config dynamiclly

    Args:
        place_in (list):
        value (Any):
        chart_config (dict | list):

    Returns:
        dict | list:
    """

    def update_nested(config, keys, val) -> dict | Any:
        key = keys[0]
        remaining_keys = keys[1:]

        if isinstance(config, dict):
            update_create_value(config, val, key, remaining_keys, update_nested)
        elif isinstance(config, list) & key.startswith("[") & key.endswith("]"):
            idx = int(key[1])
            if idx < len(config):
                if remaining_keys:
                    config[idx] = update_nested(config[idx], remaining_keys, val)
                else:
                    config[idx] = val
            else:
                config.extend(map(lambda _: {}, range(idx - len(config) + 1)))
                update_nested(config[idx], remaining_keys, val)

        return config

    return update_nested(chart_config, place_in, value)

def update_create_value(
    config: dict, val: Any, key: str, remaining_keys: list, update_nested: Callable
) -> None:
    """update_create_value Update Chart config dynamiclly

    Args:
        config (_type_):
        val (_type_):
        key (_type_):
        remaining_keys (_type_):
        update_nested (_type_):
    """
    if (key in config) & (bool(remaining_keys)):
        config[key] = update_nested(config[key], remaining_keys, val)
    elif remaining_keys and "[" in remaining_keys[0]:
        config[key] = []
        update_nested(config[key], remaining_keys, val)
    elif len(remaining_keys) >= 1:
        config[key] = {}
        update_nested(config[key], remaining_keys, val)
    else:
        config[key] = val

class HighchartWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle('Highcharts')
        self.setGeometry(200, 90, 800, 800)
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Highcharts Example</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="http://blacklabel.github.io/grouped_categories/grouped-categories.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highcharts/11.4.3/highcharts.js"
                integrity="sha512-qCaTHDKX58QLNYgW+wHYhMDNak+/fN7qg1ZNMsbmDhyOnceqaOOtPCLIELLpdRdvIngZZPw1rmrtmc9EFfJLOQ=="
                crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        </head>
        <body>
            <div id="container" style="width:100%; height:100%;"></div>
            <script>
                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig = {config};
                    Highcharts.chart('container', chartConfig);
                }});
            </script>
        </body>
        </html>
        """

        self.browser.setHtml(html_content, QUrl(''))

def display(configuration):
    try:
        app = QApplication(sys.argv)
        main_window = HighchartWindow(configuration)
        main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        pass

def currency_formatter(unit: str, config: dict) -> dict:
    """currency_formatter

    Args:
        unit (str):
        config (dict):

    Returns:
        dict:
    """
    if unit in attribute_dict['currency'].keys():
        currency_format = (
            attribute_dict['currency'].get(unit)
            and f", {{style:'currency', currency:'{attribute_dict['currency'].get(unit)}'}}"
        ) or ""
        config["valueFormatter"] = (
            f"(value === null) ? null : value.toLocaleString('en-us'{currency_format})"
        )
    return config

def grid_config(col_info: dict, dc: dict) -> dict[str, list]:
    """grid_config
    Create grid conffiguration

    Args:
        col_info (dict):
        dc (dict):

    Returns:
        dict[str, list]:
    """
    measure, dimension = [], []
    for key, meta in col_info.items():
        if (meta['colType'].lower().startswith(("int", "float"))) and meta['colType'] != 'BOOLEAN':
            col = {"columnMapping": meta["colIndex"],
                    "filter": 'agNumberColumnFilter',
                    "enablePivot": True,
                    "enableValue": True,
                    "pivotTotals": True,
                    "autoHeight": True,
                    "enableRowGroup": True,
                    "field": f"k{meta['colIndex']}",
                    "headerName": key,
                    "cellStyle": {"textAlign": "right"},
                    }
            col = currency_formatter(meta.get("unit"), col)
            measure.append(col)

        elif (meta['colType'].lower().startswith(('string','varchar'))) or meta['colType'] == 'BOOLEAN':
            dimension.append({"columnMapping": meta["colIndex"],
                                "filter": 'agTextColumnFilter',
                                "enablePivot": True,
                                "enableValue": False,
                                "pivotTotals": False,
                                "autoHeight": True,
                                "enableRowGroup": True,
                                "field": f"d{meta['colIndex']}",
                                "headerName": key,
                                "sortable": True})

    dimension.extend(measure)
    return {"columns": dimension}
