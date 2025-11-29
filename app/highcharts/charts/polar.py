"""Polar chart implementations (scatter, bubble, etc.)."""

from typing import Dict, List, Any, Optional
import polars as pl

from ..core.base_chart import BaseChart, ChartConfig, ChartSeries


class ScatterChart(BaseChart):
    """Scatter plot implementation."""
    
    def _get_chart_type(self) -> str:
        return 'scatter'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for scatter plots."""
        series_data = self._build_scatter_series()
        
        result = {
            'series': series_data,
            'chart': {'type': self.chart_type}
        }
        
        # Add axis configurations
        result.update(self._get_axis_config())
        
        return result
    
    def _build_scatter_series(self) -> List[Dict[str, Any]]:
        """Build scatter series data."""
        if self.config.get('dimension') and self.config.get('color'):
            return self._get_series_with_dimension_and_color()
        elif self.config.get('dimension'):
            return self._get_series_with_dimension()
        elif self.config.get('color'):
            return self._get_series_with_color()
        else:
            return self._get_series_basic()
    
    def _get_series_with_dimension_and_color(self) -> List[Dict[str, Any]]:
        """Build series when both dimension and color are present."""
        series_list = []
        color_values = self.df[self.config['color']].unique().sort().to_list()
        
        for color_value in color_values:
            group_df = self.df.filter(self.df[self.config['color']] == color_value)
            
            dimension_values = group_df[self.config['dimension']].to_list()
            x_values = group_df[self.config['x']].to_list()
            y_values = group_df[self.config['y']].to_list()
            
            data = [
                {'_name': dim, 'x': x, 'y': y}
                for dim, x, y in zip(dimension_values, x_values, y_values)
            ]
            
            series = {
                'type': 'scatter',
                'color_name': self.config['color'],
                'name': str(color_value),
                'x': self.config['x'],
                'y': self.config['y'],
                'dimension': self.config['dimension'],
                'keys': ['_name', 'x', 'y'],
                'data': data
            }
            series_list.append(series)
        
        return series_list
    
    def _get_series_with_dimension(self) -> List[Dict[str, Any]]:
        """Build series when only dimension is present."""
        if isinstance(self.config['dimension'], list):
            return self._get_series_with_multiple_dimensions()
        else:
            return self._get_series_with_single_dimension()
    
    def _get_series_with_multiple_dimensions(self) -> List[Dict[str, Any]]:
        """Build series with multiple dimensions."""
        dimension1_values = self.df[self.config['dimension'][0]].to_list()
        dimension2_values = self.df[self.config['dimension'][1]].to_list()
        x_values = self.df[self.config['x']].to_list()
        y_values = self.df[self.config['y']].to_list()
        
        data = [
            {'_name1': d1, '_name2': d2, 'x': x, 'y': y}
            for d1, d2, x, y in zip(dimension1_values, dimension2_values, x_values, y_values)
        ]
        
        return [{
            'type': 'scatter',
            'dimension1': self.config['dimension'][0],
            'dimension2': self.config['dimension'][1],
            'x': self.config['x'],
            'y': self.config['y'],
            'name': f"{self.config['dimension'][0]} and {self.config['dimension'][1]}",
            'keys': ['_name1', '_name2', 'x', 'y'],
            'data': data
        }]
    
    def _get_series_with_single_dimension(self) -> List[Dict[str, Any]]:
        """Build series with single dimension."""
        dimension_values = self.df[self.config['dimension']].to_list()
        x_values = self.df[self.config['x']].to_list()
        y_values = self.df[self.config['y']].to_list()
        
        data = [
            {'_name': dim, 'x': x, 'y': y}
            for dim, x, y in zip(dimension_values, x_values, y_values)
        ]
        
        return [{
            'type': 'scatter',
            'name': self.config['dimension'],
            'x': self.config['x'],
            'y': self.config['y'],
            'keys': ['_name', 'x', 'y'],
            'data': data
        }]
    
    def _get_series_with_color(self) -> List[Dict[str, Any]]:
        """Build series when only color is present."""
        color_values = self.df[self.config['color']].to_list()
        x_values = self.df[self.config['x']].to_list()
        y_values = self.df[self.config['y']].to_list()
        
        data = [
            {'_name': color, 'x': x, 'y': y}
            for color, x, y in zip(color_values, x_values, y_values)
        ]
        
        return [{
            'color_name': self.config['color'],
            'name': '_name',
            'x': self.config['x'],
            'y': self.config['y'],
            'keys': ['_name', 'x', 'y'],
            'data': data
        }]
    
    def _get_series_basic(self) -> List[Dict[str, Any]]:
        """Build basic series with no dimension or color."""
        x_values = self.df[self.config['x']].to_list()
        y_values = self.df[self.config['y']].to_list()
        
        data = [
            [x, y] for x, y in zip(x_values, y_values)
        ]
        
        return [{
            'x': self.config['x'],
            'y': self.config['y'],
            'showInLegend': False,
            'keys': ['x', 'y'],
            'data': data
        }]
    
    def _get_axis_config(self) -> Dict[str, Any]:
        """Get axis configuration for scatter plots."""
        from ..core.base_chart import AxisConfig
        axis_config = AxisConfig(self.df, self.config)
        
        return {
            'xAxis': axis_config.get_x_axis(),
            'yAxis': axis_config.get_y_axis()
        }


class BubbleChart(BaseChart):
    """Bubble chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'bubble'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for bubble charts."""
        series_data = self._build_bubble_series()
        
        result = {
            'series': series_data,
            'chart': {'type': self.chart_type}
        }
        
        # Add axis configurations
        result.update(self._get_axis_config())
        
        return result
    
    def _build_bubble_series(self) -> List[Dict[str, Any]]:
        """Build bubble series data."""
        if self.config.get('radius') and self.config.get('dimension') and self.config.get('color'):
            return self._get_series_with_radius_dimension_color()
        elif self.config.get('radius') and self.config.get('color'):
            return self._get_series_with_radius_and_color()
        elif self.config.get('dimension') and self.config.get('color'):
            return self._get_series_with_dimension_and_color()
        elif self.config.get('radius'):
            return self._get_series_with_radius()
        else:
            return []
    
    def _get_series_with_radius_dimension_color(self) -> List[Dict[str, Any]]:
        """Build series with radius, dimension, and color."""
        series_list = []
        color_values = self.df[self.config['color']].unique().sort().to_list()
        
        for color_value in color_values:
            group_df = self.df.filter(self.df[self.config['color']] == color_value)
            
            dimension_values = group_df[self.config['dimension']].to_list()
            x_values = group_df[self.config['x']].to_list()
            y_values = group_df[self.config['y']].to_list()
            radius_values = group_df[self.config['radius']].to_list()
            
            data = [
                {'_name': dim, 'x': x, 'y': y, 'z': radius}
                for dim, x, y, radius in zip(dimension_values, x_values, y_values, radius_values)
            ]
            
            series = {
                'type': 'bubble',
                'color_name': self.config['color'],
                'name': str(color_value),
                'x': self.config['x'],
                'y': self.config['y'],
                'z': self.config['radius'],
                'dimension': self.config['dimension'],
                'keys': ['_name', 'x', 'y', 'z'],
                'data': data
            }
            series_list.append(series)
        
        return series_list
    
    def _get_series_with_radius_and_color(self) -> List[Dict[str, Any]]:
        """Build series with radius and color."""
        series_list = []
        color_values = self.df[self.config['color']].to_list()
        x_values = self.df[self.config['x']].to_list()
        y_values = self.df[self.config['y']].to_list()
        radius_values = self.df[self.config['radius']].to_list()
        
        for color, x, y, radius in zip(color_values, x_values, y_values, radius_values):
            series = {
                'type': 'bubble',
                'color_name': self.config['color'],
                'name': str(color),
                'x': self.config['x'],
                'y': self.config['y'],
                'z': self.config['radius'],
                'keys': ['_name', 'x', 'y', 'z'],
                'data': [[color, x, y, radius]]
            }
            series_list.append(series)
        
        return series_list
    
    def _get_series_with_dimension_and_color(self) -> List[Dict[str, Any]]:
        """Build series with dimension and color."""
        series_list = []
        color_values = self.df[self.config['color']].unique().sort().to_list()
        
        for color_value in color_values:
            group_df = self.df.filter(self.df[self.config['color']] == color_value)
            
            dimension_values = group_df[self.config['dimension']].to_list()
            x_values = group_df[self.config['x']].to_list()
            y_values = group_df[self.config['y']].to_list()
            
            data = [
                {'_name': dim, 'x': x, 'y': y}
                for dim, x, y in zip(dimension_values, x_values, y_values)
            ]
            
            series = {
                'type': 'bubble',
                'color_name': self.config['color'],
                'name': str(color_value),
                'x': self.config['x'],
                'y': self.config['y'],
                'dimension': self.config['dimension'],
                'keys': ['_name', 'x', 'y'],
                'data': data
            }
            series_list.append(series)
        
        return series_list
    
    def _get_series_with_radius(self) -> List[Dict[str, Any]]:
        """Build series with radius only."""
        x_values = self.df[self.config['x']].to_list()
        y_values = self.df[self.config['y']].to_list()
        radius_values = self.df[self.config['radius']].to_list()
        
        data = [
            [x, y, radius]
            for x, y, radius in zip(x_values, y_values, radius_values)
        ]
        
        return [{
            'type': 'bubble',
            'x': self.config['x'],
            'y': self.config['y'],
            'z': self.config['radius'],
            'keys': ['x', 'y', 'z'],
            'data': data,
            'showInLegend': False
        }]
    
    def _get_axis_config(self) -> Dict[str, Any]:
        """Get axis configuration for bubble charts."""
        from ..core.base_chart import AxisConfig
        axis_config = AxisConfig(self.df, self.config)
        
        return {
            'xAxis': axis_config.get_x_axis(),
            'yAxis': axis_config.get_y_axis()
        }


class SplitBubbleChart(BaseChart):
    """Split bubble chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'packedbubble'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for split bubble charts."""
        series_data = self._build_split_bubble_series()
        
        result = {
            'series': series_data,
            'chart': {'type': self.chart_type},
            'xAxis': {},  # Split bubble charts don't use traditional x-axis
            'yAxis': {}   # Split bubble charts don't use traditional y-axis
        }
        
        return result
    
    def _build_split_bubble_series(self) -> List[Dict[str, Any]]:
        """Build split bubble series data."""
        series_list = []
        color_values = self.df[self.config['color']].unique().sort().to_list()
        
        for color_value in color_values:
            group_df = self.df.filter(self.df[self.config['color']] == color_value)
            
            x_values = group_df[self.config['x']].to_list()
            y_values = group_df[self.config['y']].to_list()
            
            data = [
                {'name': x, 'value': y}
                for x, y in zip(x_values, y_values)
            ]
            
            series = {
                'type': 'packedbubble',
                'color_name': self.config['color'],
                'name': str(color_value),
                'x': self.config['x'],
                'y': self.config['y'],
                'keys': ['name', 'value'],
                'data': data
            }
            series_list.append(series)
        
        return series_list