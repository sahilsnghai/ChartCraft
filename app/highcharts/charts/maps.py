"""Map chart implementations."""

from typing import Dict, List, Any, Optional
import copy
import polars as pl

from ..core.base_chart import BaseChart, ChartConfig


class MapChartBase(BaseChart):
    """Base class for map chart implementations."""
    
    base_config: Dict[str, Any] = {
        "configuration": {
            "type": "map__leaflet",
            "tooltipOnHover": True,
            "tooltipStyle": {
                "background": "#ffffff",
                "color": "#010101",
                "width": "100%",
                "padding": "8px",
                "display": "flex",
                "alignItems": "center",
                "wordBreak": "break-all",
                "overflow": "hidden",
                "textOverflow": "ellipses",
            },
            "markerOpacity": 0.9,
            "iconSize": 30,
            "gradient": [
                {"key": 0.1, "value": "#32CD32"},
                {"key": 0.2, "value": "#228B22"},
                {"key": 0.3, "value": "#006400"},
                {"key": 0.4, "value": "#87CEFA"},
                {"key": 0.5, "value": "#4169E1"},
                {"key": 0.6, "value": "#0000FF"},
                {"key": 0.7, "value": "#00008B"},
                {"key": 0.8, "value": "#FF6347"},
                {"key": 0.9, "value": "#FF4500"},
                {"key": 1.0, "value": "#FF0000"},
            ],
        }
    }
    
    def map_tooltip(self, val: Dict[str, Any]) -> str:
        """Create tooltip content for map markers."""
        # Filter out latitude and longitude from tooltip
        tooltip_data = {
            k: v for k, v in val.items() 
            if not (k.startswith("long") or k.startswith("lat"))
        }
        
        # Build tooltip HTML
        tooltip_parts = [
            f"{k} : {v} <br/>"
            for k, v in tooltip_data.items()
        ]
        
        return f"<div>{''.join(tooltip_parts)[:-6]}</div>"
    
    def create_markers(self) -> tuple[List[Dict[str, Any]], float, float, int]:
        """Create map markers from data."""
        location_data = self.df.rows(named=True)
        lat_sum = 0
        long_sum = 0
        count = 0
        markers = []
        
        for val in location_data:
            lat_sum += val["latitude"]
            long_sum += val["longitude"]
            count += 1
            
            # Add tooltip content to each marker
            val_with_tooltip = val.copy()
            val_with_tooltip["tooltipContent"] = {"template": self.map_tooltip(val)}
            markers.append(val_with_tooltip)
        
        return markers, lat_sum, long_sum, count


class MapChart(MapChartBase):
    """Geo map chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'geo-map'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for geo map charts."""
        _config = copy.deepcopy(self.base_config)
        markers, lat_sum, long_sum, count = self.create_markers()
        
        # Calculate center point and zoom
        dynamic_config = {
            "dynamicConfig": {
                "lat": round(lat_sum / count, 2),
                "lng": round(long_sum / count, 2),
                "zoom": 5,
            }
        }
        
        _config["configuration"].update(dynamic_config)
        _config["markers"] = markers
        
        return _config


class ScatterMapChart(MapChart):
    """Scatter map chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'scatter-map'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for scatter map charts."""
        _config = super().get_series()
        
        # Add scatter-specific configuration
        scatter_config = {
            "scatterMapRadius": self.config.get("scatterMapRadius", 8),
            "scatterOpacity": self.config.get("scatterOpacity", 0.5),
            "scatterStroke": self.config.get("scatterStroke", False),
            "scatter": {"color": "#e43100"},
        }
        
        _config["configuration"].update(scatter_config)
        return _config


class BubbleMapChart(MapChart):
    """Bubble map chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'bubble-map'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for bubble map charts."""
        _config = super().get_series()
        
        # Add bubble-specific configuration
        bubble_config = {
            "bubbleMapKey": self.config.get(
                "bubbleMapKey", self.config.get("y", "bubble_map_key")
            ),
            "bubbleMapRadiusMultiplier": self.config.get(
                "bubbleMapRadiusMultiplier", 50
            ),
            "bubbleOpacity": self.config.get("bubbleOpacity", 0.5),
            "bubbleStroke": self.config.get("bubbleStroke", False),
            "bubble": {"color": "#e43100"},
        }
        
        _config["configuration"].update(bubble_config)
        return _config


class HeatMapChart(MapChart):
    """Heat map chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'heat-map'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for heat map charts."""
        _config = super().get_series()
        
        # Add heat-specific configuration
        heat_config = {
            "heatMapKey": self.config.get(
                "heatMapKey", self.config.get("y", "heat_map_key")
            ),
            "heatMapRadius": self.config.get("heatMapRadius", 30),
            "heatMapMax": self.config.get("heatMapMax", 3),
        }
        
        _config["configuration"].update(heat_config)
        return _config