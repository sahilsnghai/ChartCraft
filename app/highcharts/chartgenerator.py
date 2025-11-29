"""Refactored viz_generator.py using the new class-based architecture.

This file replaces the original procedural implementation with a clean, 
object-oriented design that is fully modular and maintainable.
"""

from typing import Dict, List, Any, Optional
import polars as pl

from .core.base_chart import ChartConfig
from .core.chart_factory import ChartFactory
from .core.tooltip_plot_options import TooltipBuilder, PlotOptionsBuilder
from app.core.logging import set_up_logging

logger = set_up_logging()


class ChartGenerator:
    """Main chart generator that orchestrates the new class-based architecture."""
    
    def __init__(self):
        self.tooltip_builder = TooltipBuilder()
        self.plot_options_builder = PlotOptionsBuilder()
    
    def generate_viz(self, advance_settings: Dict[str, Any], df: pl.DataFrame, config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate visualization using the new class-based architecture.
        
        This function maintains the exact same signature as the original
        to ensure backward compatibility while using the new architecture internally.
        
        Args:
            advance_settings: Advanced chart settings
            df: Polars DataFrame with the data
            config: List of chart configurations
            
        Returns:
            Complete chart configuration
        """
        try:
            logger.info(f"Generating visualization with {len(config)} chart(s)")
            
            # Initialize main chart configuration
            high_chart = {}
            high_chart_config = {}
            is_grid_or_map = False
            
            # Process each chart configuration
            for index, chart_config in enumerate(config):
                # Normalize chart type
                chart_config['type'] = str.lower(chart_config['type'])
                
                # Apply advance settings to the first chart, preserve dataLabels for others
                if index == 0:
                    chart_config = self._apply_advance_settings(advance_settings, chart_config)
                else:
                    chart_config = self._preserve_data_labels(advance_settings, chart_config)
                
                # Create chart instance using factory
                chart_instance = ChartFactory.create_chart(chart_config["type"], df, ChartConfig(chart_config))
                
                if chart_instance is None:
                    logger.warning(f"Unknown chart type: {chart_config['type']}")
                    continue
                
                # Handle special chart types (Grid, Map)
                if self._is_special_chart(chart_instance):
                    high_chart = chart_instance.get_series()
                    is_grid_or_map = True
                    break
                
                # Generate series and update configurations
                high_chart_config = self._update_chart_with_series(high_chart_config, index, chart_config, chart_instance)
                
                # Initialize chart options for the first chart
                if index == 0:
                    high_chart_config = self._initialize_chart_options(high_chart_config, chart_config, chart_instance)
                
                # Update main configuration
                high_chart.update(high_chart_config)
            
            # Handle multi-chart Y-axis configuration
            if len(config) > 1 and not is_grid_or_map:
                high_chart = self._configure_multi_chart_y_axis(config, high_chart, advance_settings)
            
            return high_chart
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return {"error": str(e), "series": []}
    
    def _apply_advance_settings(self, advance_settings: Dict[str, Any], chart_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply advance settings to chart configuration."""
        if not advance_settings:
            return chart_config
        
        # Map advance settings to chart config
        advance_settings_mapping = {
            'dataLabels': 'dataLabels',
            'xAxis': 'xAxis',
            'yAxis': 'yAxis',
            'legend': 'legend',
            'chartTitle': 'chartTitle',
            'chartSubTitle': 'chartSubTitle',
            'chartSpacing': 'chartSpacing',
            'zoomType': 'zoomType',
            'scrollMax': 'scrollMax',
            'zooming': 'zooming',
            'opacity': 'opacity',
            'backgroundColor': 'backgroundColor',
            'plotBackgroundColor': 'plotBackgroundColor',
            'plotBorderColor': 'plotBorderColor',
            'plotBorderWidth': 'plotBorderWidth',
            'hoverHighlightColor': 'hoverHighlightColor',
        }
        
        # Apply settings
        for key, config_key in advance_settings_mapping.items():
            if key in advance_settings:
                chart_config[config_key] = advance_settings[key]
        
        # Handle special cases
        if 'scrollMax' in advance_settings:
            chart_config['max'] = advance_settings['scrollMax']
            chart_config['scrollBar'] = True
        
        return chart_config
    
    def _preserve_data_labels(self, advance_settings: Dict[str, Any], chart_config: Dict[str, Any]) -> Dict[str, Any]:
        """Preserve data labels settings for subsequent charts."""
        if advance_settings and 'dataLabels' in advance_settings:
            chart_config['dataLabels'] = advance_settings['dataLabels']
        return chart_config
    
    def _is_special_chart(self, chart_instance) -> bool:
        """Check if chart is a special type (Grid or Map)."""
        from .charts.grid import GridChart
        from .charts.maps import MapChart
        
        return isinstance(chart_instance, (GridChart, MapChart))
    
    def _update_chart_with_series(self, high_chart_config: Dict[str, Any], index: int, 
                                 chart_config: Dict[str, Any], chart_instance) -> Dict[str, Any]:
        """Update chart configuration with series data and tooltip/plot options."""
        # Get series data from chart instance
        series_data = chart_instance.get_series()
        
        if index == 0:
            # First chart - set series directly
            high_chart_config.update(series_data)
        else:
            # Subsequent charts - append to existing series
            if 'series' not in high_chart_config:
                high_chart_config['series'] = []
            
            if 'series' in series_data:
                high_chart_config['series'].extend(series_data['series'])
        
        # Add tooltip configuration
        tooltip_config = self.tooltip_builder.create_tooltip(ChartConfig(chart_config), chart_config['type'])
        high_chart_config['tooltip'] = tooltip_config
        
        # Add plot options
        plot_options = self.plot_options_builder.create_plot_options(ChartConfig(chart_config), chart_config['type'])
        if 'plotOptions' not in high_chart_config:
            high_chart_config['plotOptions'] = {}
        high_chart_config['plotOptions'].update(plot_options)
        
        # Update scrollbar if needed
        high_chart_config = self._update_scrollbar(high_chart_config, chart_config, index)
        
        return high_chart_config
    
    def _initialize_chart_options(self, high_chart_config: Dict[str, Any], 
                                 chart_config: Dict[str, Any], chart_instance) -> Dict[str, Any]:
        """Initialize main chart options."""
        # Add chart-level configurations
        if 'chart' not in high_chart_config:
            high_chart_config['chart'] = {}
        
        high_chart_config['chart'].update({
            'zooming': {'mouseWheel': chart_config.get('mouseWheel', False)},
            'zoomType': chart_config.get('zoomType'),
            'backgroundColor': chart_config.get('backgroundColor'),
            'plotBackgroundColor': chart_config.get('plotBackgroundColor'),
            'plotBorderWidth': chart_config.get('plotBorderWidth'),
            'plotBorderColor': chart_config.get('plotBorderColor')
        })
        
        # Add credits and exporting
        high_chart_config['credits'] = {'enabled': chart_config.get('credits', False)}
        high_chart_config['exporting'] = {'enabled': chart_config.get('exporting', False)}
        high_chart_config['lang'] = {'thousandsSep': ','}
        
        # Add titles
        title_config = chart_instance.get_title_config()
        high_chart_config.update(title_config)
        
        # Add legend
        legend_config = chart_instance.get_legend_config()
        if legend_config:
            high_chart_config['legend'] = legend_config
        
        # Add spacing if configured
        if chart_config.get('chartSpacing'):
            spacing_config = chart_instance.get_spacing_config()
            high_chart_config['chart'].update(spacing_config)
        
        return high_chart_config
    
    def _update_scrollbar(self, high_chart_config: Dict[str, Any], chart_config: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Update scrollbar configuration."""
        if 'xAxis' not in high_chart_config:
            return high_chart_config
        
        if chart_config.get('max'):
            if isinstance(high_chart_config['xAxis'], dict):
                high_chart_config['xAxis'].update({
                    'scrollbar': {'enabled': True},
                    'max': chart_config['max']
                })
            else:
                if index < len(high_chart_config['xAxis']):
                    high_chart_config['xAxis'][index].update({
                        'scrollbar': {'enabled': True},
                        'max': chart_config['max']
                    })
        
        return high_chart_config
    
    def _configure_multi_chart_y_axis(self, config: List[Dict[str, Any]], 
                                    high_chart: Dict[str, Any], 
                                    advance_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Y-axis for multi-chart scenarios."""
        y_axis_names = []
        y_axis_names_opposite = []
        
        for chart_config in config:
            if chart_config.get('opposite'):
                y_axis_names_opposite.append(chart_config['y'])
            else:
                y_axis_names.append(chart_config['y'])
        
        # Build Y-axis configuration
        y_axis_config = []
        opposite_found = False
        
        for index, chart_config in enumerate(config):
            if chart_config.get('opposite'):
                y_axis_config.append(self._build_y_axis_config(advance_settings, chart_config, opposite=True))
                if 'series' in high_chart and index < len(high_chart['series']):
                    high_chart['series'][index]['yAxis'] = 1
                opposite_found = True
            else:
                y_axis_config.append(self._build_y_axis_config(advance_settings, chart_config, opposite=False))
        
        high_chart['yAxis'] = y_axis_config
        
        # If no opposite axis found, combine names and use single axis
        if not opposite_found and y_axis_names:
            y_label_text = ', '.join(y_axis_names[:-1]) + f' and {y_axis_names[-1]}'
            if 'yAxis' in high_chart and high_chart['yAxis']:
                high_chart['yAxis'] = high_chart['yAxis'][0]
                high_chart['yAxis']['title']['text'] = advance_settings.get('yAxis', {}).get('commonName', y_label_text)
        
        return high_chart
    
    def _build_y_axis_config(self, advance_settings: Dict[str, Any], 
                           chart_config: Dict[str, Any], opposite: bool = False) -> Dict[str, Any]:
        """Build Y-axis configuration."""
        y_axis_settings = advance_settings.get('yAxis', {})
        if isinstance(y_axis_settings, list) and len(y_axis_settings) > 0:
            y_axis_settings = y_axis_settings[0]
        
        y_label = chart_config.get('yAxisLabel', chart_config.get('y', ''))
        if isinstance(y_label, list):
            y_label = '-'.join(y_label)
        
        return {
            'title': {
                'text': y_axis_settings.get('title', y_label),
                'margin': y_axis_settings.get('titleMargin', 11),
                'style': {
                    'color': y_axis_settings.get('titleLabelColor', '#000000'),
                    'fontWeight': y_axis_settings.get('fontWeight'),
                    'fontSize': y_axis_settings.get('titleLabelFontSize', 14)
                }
            },
            'gridLineWidth': y_axis_settings.get('gridLineWidth'),
            'tickInterval': y_axis_settings.get('scaleInterval'),
            'min': y_axis_settings.get('min'),
            'max': y_axis_settings.get('max'),
            'startOnTick': y_axis_settings.get('startOnTick'),
            'endOnTick': y_axis_settings.get('endOnTick'),
            'allowDecimals': y_axis_settings.get('allowDecimalScale'),
            'labels': {
                'format': y_axis_settings.get('labelFormat'),
                'style': {
                    'color': y_axis_settings.get('labelColor', '#000000'),
                    'fontSize': y_axis_settings.get('fontSize', 12),
                    'fontWeight': y_axis_settings.get('labelFontWeight')
                }
            },
            'opposite': opposite
        }


# Create global instance for backward compatibility
_chart_generator = ChartGenerator()


def generate_viz(advance_settings: Dict[str, Any], df: pl.DataFrame, config: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate visualization using the new class-based architecture.
    
    This function maintains the exact same signature as the original generate_viz
    to ensure complete backward compatibility while using the new architecture internally.
    
    Args:
        advance_settings: Advanced chart settings (same as original)
        df: Polars DataFrame with the data (same as original)
        config: List of chart configurations (same as original)
        
    Returns:
        Complete chart configuration (same format as original)
        
    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        >>> config = [{'type': 'column', 'x': 'x', 'y': 'y'}]
        >>> result = generate_viz({}, df, config)
        >>> print(result['series'][0]['type'])  # 'column'
    """
    return _chart_generator.generate_viz(advance_settings, df, config)
