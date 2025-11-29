"""Base chart classes and common functionality for the highcharts module."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import polars as pl

from app.core.logging import set_up_logging

logger = set_up_logging()


class ChartConfig:
    """Immutable configuration wrapper for chart configurations."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        return self._config[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._config
    
    @property
    def raw(self) -> Dict[str, Any]:
        """Get the raw configuration dictionary."""
        return self._config.copy()


class ChartSeries:
    """Represents a single series in a chart."""
    
    def __init__(self, series_type: str, data: List, name: str, **kwargs):
        self.series_type = series_type
        self.data = data
        self.name = name
        self.options = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert series to dictionary format."""
        result = {
            'type': self.series_type,
            'name': self.name,
            'data': self.data
        }
        result.update(self.options)
        return result


class BaseChart(ABC):
    """Abstract base class for all chart types."""
    
    def __init__(self, df: pl.DataFrame, config: ChartConfig):
        self.df = df
        self.config = config
        self.chart_type = self._get_chart_type()
    
    @abstractmethod
    def _get_chart_type(self) -> str:
        """Get the chart type identifier."""
        pass
    
    @abstractmethod
    def get_series(self) -> Dict[str, Any]:
        """Generate the series data for this chart."""
        pass
    
    def get_chart_options(self) -> Dict[str, Any]:
        """Get chart-specific options."""
        return {}
    
    def get_tooltip_config(self) -> Dict[str, Any]:
        """Get tooltip configuration."""
        return {
            'shared': self.config.get('share_tooltip', True),
            'useHTML': True
        }
    
    def get_legend_config(self) -> Dict[str, Any]:
        """Get legend configuration."""
        legend_config = self.config.get('legend', {})
        if legend_config.get('visible') is False:
            return {'enabled': False}
        
        return {
            'verticalAlign': legend_config.get('layout', 'bottom'),
            'align': legend_config.get('align', 'center'),
            'floating': legend_config.get('floating', False),
            'y': legend_config.get('y', 20),
            'backgroundColor': legend_config.get('backgroundColor', '#ffffff'),
            'maxHeight': legend_config.get('maxHeight', 70),
            'itemStyle': {
                'color': legend_config.get('color', '#000000'),
                'fontSize': legend_config.get('fontSize', 12),
                'fontWeight': legend_config.get('fontWeight')
            }
        }
    
    def get_title_config(self) -> Dict[str, Any]:
        """Get title and subtitle configuration."""
        title_config = self.config.get('chartTitle', {})
        subtitle_config = self.config.get('chartSubTitle', {})
        
        result = {
            'title': {
                'text': title_config.get('text', ''),
                'align': title_config.get('align', 'left'),
                'style': {
                    'fontSize': title_config.get('fontSize', 16),
                    'fontWeight': title_config.get('fontWeight'),
                    'color': title_config.get('color', '#000000')
                }
            }
        }
        
        if subtitle_config:
            result['subtitle'] = {
                'text': subtitle_config.get('text', ''),
                'align': subtitle_config.get('align', 'left'),
                'style': {
                    'fontSize': subtitle_config.get('fontSize', 16),
                    'fontWeight': subtitle_config.get('fontWeight'),
                    'color': subtitle_config.get('color', '#000000')
                }
            }
        
        return result
    
    def get_spacing_config(self) -> Dict[str, Any]:
        """Get chart spacing configuration."""
        spacing = self.config.get('chartSpacing', {})
        return {
            'marginTop': spacing.get('marginTop'),
            'marginBottom': spacing.get('marginBottom'),
            'marginLeft': spacing.get('marginLeft'),
            'marginRight': spacing.get('marginRight'),
            'spacingTop': spacing.get('spacingTop'),
            'spacingBottom': spacing.get('spacingBottom'),
            'spacingLeft': spacing.get('spacingLeft'),
            'spacingRight': spacing.get('spacingRight')
        }


class AxisConfig:
    """Configuration for chart axes."""
    
    def __init__(self, df: pl.DataFrame, config: ChartConfig):
        self.df = df
        self.config = config
    
    def get_x_axis(self, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get X-axis configuration."""
        x_axis_config = self.config.get('xAxis', {})
        
        result = {
            'crosshair': {
                'enabled': self.config.get('crosshair', True),
                'color': self.config.get('hoverHighlightColor')
            },
            'labels': {
                'style': {
                    'color': x_axis_config.get('labelColor'),
                    'fontSize': x_axis_config.get('labelFontSize', 12),
                    'fontWeight': x_axis_config.get('labelFontWeight')
                },
                'format': x_axis_config.get('labelFormat')
            },
            'scrollbar': x_axis_config.get('scrollBar', False),
            'max': x_axis_config.get('max')
        }
        
        if categories:
            result['categories'] = categories
        
        if self.config.get('x'):
            result['title'] = {
                'text': x_axis_config.get('title', self.config['x']),
                'style': {
                    'color': x_axis_config.get('titleLabelColor', '#000000'),
                    'fontWeight': x_axis_config.get('fontWeight'),
                    'fontSize': x_axis_config.get('titleLabelFontSize', 14)
                }
            }
        
        return result
    
    def get_y_axis(self, y_label: Optional[str] = None) -> Dict[str, Any]:
        """Get Y-axis configuration."""
        y_axis_config = self.config.get('yAxis', {})
        
        if isinstance(y_axis_config, list):
            y_axis_config = y_axis_config[0]
        
        if not y_label:
            y_label = self.config.get('yAxisLabel', self.config.get('y', ''))
            if isinstance(y_label, list):
                y_label = '-'.join(y_label)
        
        return {
            'title': {
                'text': y_axis_config.get('title', y_label),
                'style': {
                    'color': y_axis_config.get('titleLabelColor', '#000000'),
                    'fontWeight': y_axis_config.get('fontWeight'),
                    'fontSize': y_axis_config.get('titleLabelFontSize', 14)
                }
            },
            'gridLineWidth': y_axis_config.get('gridLineWidth'),
            'labels': {
                'style': {
                    'color': y_axis_config.get('labelColor', '#000000'),
                    'fontSize': y_axis_config.get('labelFontSize', 12),
                    'fontWeight': y_axis_config.get('labelFontWeight')
                },
                'format': y_axis_config.get('labelFormat')
            }
        }


class DataProcessor:
    """Handles data processing and transformation for charts."""
    
    @staticmethod
    def replace_with_index(df: pl.DataFrame, column: str) -> tuple[pl.DataFrame, List[str]]:
        """Replace column values with indices and return distinct values."""
        df_col = df.select(column).unique(maintain_order=True)
        col_values = df_col.to_numpy().T.tolist()[0]
        df = (
            df.join(df_col.with_row_index("ones", offset=0), on=column)
            .drop(column)
            .rename({"ones": column})
        )
        return df, col_values
    
    @staticmethod
    def format_with_commas(value: float, prefix: str = '', suffix: str = '') -> str:
        """Format a number with commas and optional prefix/suffix."""
        value = round(value, 2)
        formatted_value = f"{value:,.2f}"
        return f"{prefix}{formatted_value}{suffix}"
    
    @staticmethod
    def display_human_readable(n: float, currency: str = '') -> str:
        """Display a number in human-readable format."""
        if n is None:
            return ''
        
        currency_symbols = {
            '€': 'EUR', 'kr': 'SEK', '฿': 'THB', '#': None, 'Mex$': 'MXN',
            'R$': 'BRL', 'A$': 'AUD', 'C$': 'CAD', '$': 'USD', 'JP¥': 'JPY',
            '₩': 'KRW', 'NT$': 'TWD', '¥': 'CNY', '₹': 'INR', '£': 'GBP', 'zł': 'PLN'
        }
        
        mill_names = ['', 'K', 'M', 'B', ' Trillion']
        n = float(n)
        mill_idx = max(0, min(4, int((0 if n == 0 else pl.math.log10(abs(n)) / 3))))
        value = f"{n / 10 ** (3 * mill_idx):.2f}{mill_names[mill_idx]}"
        
        if currency in currency_symbols:
            return f"{currency} {value}" if currency_symbols[currency] else value
        elif not currency:
            return value
        else:
            return f"{value} {currency}"