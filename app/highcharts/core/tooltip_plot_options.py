"""Tooltip and plot options configuration for charts."""

from typing import Dict, Any, List, Optional, Union
from .base_chart import ChartConfig, DataProcessor


class TooltipBuilder:
    """Builds tooltip configurations for different chart types."""
    
    @staticmethod
    def create_tooltip(config: ChartConfig, chart_type: str) -> Dict[str, Any]:
        """Create tooltip configuration based on chart type."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        base_tooltip = {
            'shared': config.get('share_tooltip', True),
            'useHTML': True,
            'headerFormat': '<b>{point.x}</b><br>',
            'footerFormat': '',
            'valueDecimals': 2
        }
        
        tooltip_methods = {
            'heatmap': TooltipBuilder._heatmap_tooltip,
            'pie': TooltipBuilder._pie_tooltip,
            'donut': TooltipBuilder._pie_tooltip,
            'semi donut': TooltipBuilder._pie_tooltip,
            'sunburst': TooltipBuilder._sunburst_tooltip,
            'scatter': TooltipBuilder._scatter_tooltip,
            'bubble': TooltipBuilder._bubble_tooltip,
            'split-bubble': TooltipBuilder._split_bubble_tooltip,
            'waterfall': TooltipBuilder._waterfall_tooltip,
            'custom-boxplot': TooltipBuilder._boxplot_tooltip,
            'boxplot': TooltipBuilder._boxplot_tooltip,
            'treemap': TooltipBuilder._treemap_tooltip,
            'bell-curve': TooltipBuilder._bell_curve_tooltip,
            'area-range': TooltipBuilder._area_range_tooltip,
            'pareto': TooltipBuilder._pareto_tooltip,
            'trend': TooltipBuilder._trend_tooltip,
            'prediction': TooltipBuilder._prediction_tooltip
        }
        
        if chart_type in tooltip_methods:
            return tooltip_methods[chart_type](config, base_tooltip)
        
        # Default tooltip for most chart types
        return TooltipBuilder._default_tooltip(config, base_tooltip, value_prefix, value_suffix)
    
    @staticmethod
    def _default_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any], 
                        value_prefix: str, value_suffix: str) -> Dict[str, Any]:
        """Create default tooltip with value formatting."""
        point_format = '{point.y:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '{point.series.name}: ')
        
        return {**base_tooltip, 'pointFormat': point_format}
    
    @staticmethod
    def _heatmap_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create heatmap-specific tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '{point.value:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '{point.series.name}: ')
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': (
                '<b>{series.xAxis.userOptions.title.text}</b>: {series.xAxis.categories.(point.x)}</br>'
                '<b>{series.yAxis.userOptions.title.text}</b>: {series.yAxis.categories.(point.y)}</br>'
                f'{point_format}'
            )
        }
    
    @staticmethod
    def _pie_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create pie chart tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '{point.y:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '{point.series.name}: ')
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': point_format
        }
    
    @staticmethod
    def _sunburst_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create sunburst tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '{point.value:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '{point.name}: ')
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': point_format
        }
    
    @staticmethod
    def _scatter_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create scatter plot tooltip."""
        tooltip_config = config.get('tooltip', [])
        if not tooltip_config or len(tooltip_config) < 2:
            return base_tooltip
        
        value_prefix1 = tooltip_config[0].get('valuePrefix', '')
        value_suffix1 = tooltip_config[0].get('valueSuffix', '')
        value_prefix2 = tooltip_config[1].get('valuePrefix', '')
        value_suffix2 = tooltip_config[1].get('valueSuffix', '')
        
        point_format1 = '{point.x:,.2f}'
        point_format2 = '{point.y:,.2f}'
        
        point_format_1 = TooltipBuilder._format_point_format_scatter(value_prefix1, value_suffix1, point_format1)
        point_format_2 = TooltipBuilder._format_point_format_scatter(value_prefix2, value_suffix2, point_format2)
        
        point_format = f'<b>{{series.userOptions.x}}</b>: {point_format_1}<b>{{series.userOptions.y}}</b>: {point_format_2}'
        
        if isinstance(config.get('dimension'), list):
            point_format = (
                '<b>{series.userOptions.dimension1}</b>: {point._name1}</br>'
                '<b>{series.userOptions.dimension2}</b>: {point._name2}</br>'
            ) + point_format
        elif config.get('color') and isinstance(config.get('dimension'), str):
            point_format = (
                '<b>{series.userOptions.color_name}</b>: {series.name}</br>'
                '<b>{series.userOptions.dimension}</b>: {point._name}</br>'
            ) + point_format
        elif config.get('color'):
            point_format = '<b>{series.userOptions.color_name}</b>: {point._name}</br>' + point_format
        elif isinstance(config.get('dimension'), str):
            point_format = '<b>{series.name}</b>: {point._name}</br>' + point_format
        
        return {**base_tooltip, 'pointFormat': point_format}
    
    @staticmethod
    def _bubble_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create bubble chart tooltip."""
        tooltip_config = config.get('tooltip', [])
        if not tooltip_config or len(tooltip_config) < 2:
            return base_tooltip
        
        value_prefix1 = tooltip_config[0].get('valuePrefix', '')
        value_suffix1 = tooltip_config[0].get('valueSuffix', '')
        value_prefix2 = tooltip_config[1].get('valuePrefix', '')
        value_suffix2 = tooltip_config[1].get('valueSuffix', '')
        
        point_format1 = '{point.x:,.2f}'
        point_format2 = '{point.y:,.2f}'
        point_format3 = '{point.z:,.2f}'
        
        point_format_1 = TooltipBuilder._format_point_format_scatter(value_prefix1, value_suffix1, point_format1)
        point_format_2 = TooltipBuilder._format_point_format_scatter(value_prefix2, value_suffix2, point_format2)
        
        point_format = f'<b>{{series.userOptions.x}}</b>: {point_format_1}<b>{{series.userOptions.y}}</b>: {point_format_2}'
        
        if config.get('color') and isinstance(config.get('dimension'), str) and config.get('radius'):
            point_format_3 = TooltipBuilder._format_point_format_scatter(
                tooltip_config[2].get('valuePrefix', ''), 
                tooltip_config[2].get('valueSuffix', ''), 
                point_format3
            )
            point_format += f'<b>{{series.userOptions.z}} (Size)</b>: {point_format_3}'
        elif config.get('radius') and config.get('color'):
            point_format_3 = TooltipBuilder._format_point_format_scatter(
                tooltip_config[2].get('valuePrefix', ''), 
                tooltip_config[2].get('valueSuffix', ''), 
                point_format3
            )
            point_format += f'<b>{{series.userOptions.z}} (Size)</b>: {point_format_3}'
        elif isinstance(config.get('dimension'), list):
            point_format = (
                '<b>{series.userOptions.dimension1}</b>: {point._name1}</br>'
                '<b>{series.userOptions.dimension2}</b>: {point._name2}</br>'
            ) + point_format
        elif config.get('color') and isinstance(config.get('dimension'), str):
            point_format = (
                '<b>{series.userOptions.color_name}</b>: {series.name}</br>'
                '<b>{series.userOptions.dimension}</b>: {point._name}</br>'
            ) + point_format
        elif config.get('radius'):
            point_format_3 = TooltipBuilder._format_point_format_scatter(
                tooltip_config[2].get('valuePrefix', ''), 
                tooltip_config[2].get('valueSuffix', ''), 
                point_format3
            )
            point_format += f'<b>{{series.userOptions.z}} (Size)</b>: {point_format_3}'
        
        return {**base_tooltip, 'pointFormat': point_format}
    
    @staticmethod
    def _split_bubble_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create split bubble tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '{point.y:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '<b>{series.userOptions.y}</b>: ')
        
        point_format = (
            '<b>{series.userOptions.color_name}</b>: {series.name}</br>'
            '<b>{series.userOptions.x}</b>: {point.name}</br>'
        ) + point_format
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': point_format
        }
    
    @staticmethod
    def _waterfall_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create waterfall tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        if config.get('value') or config.get('difference') or config.get('changePercent'):
            point_format = '{point.value:,.2f}'
            point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '<b>{series.userOptions.attribute}</b>: ')
            
            if config.get('difference'):
                return {**base_tooltip, 'pointFormat': '<b>{series.name}</b>: {point.y}<br>' + point_format}
            else:
                return {**base_tooltip, 'pointFormat': '<b>{series.name}</b>: {point.y:,.2f}%<br>' + point_format}
        else:
            point_format = '{point.y:,.2f}'
            point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '{point.series.name}: ')
            return {**base_tooltip, 'pointFormat': point_format}
    
    @staticmethod
    def _boxplot_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create boxplot tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '{point.y:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '<b>{series.userOptions.measure}</b>: ')
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': '<b>{series.userOptions.attribute}</b>: {point.outlier_name}</br>' + point_format
        }
    
    @staticmethod
    def _treemap_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create treemap tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '{point.value:,.2f}'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, point_format, '{point.name}: ')
        
        if config.get('y'):
            point_format = '<b>{point.parent_name}</b></br>' + point_format
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': point_format
        }
    
    @staticmethod
    def _bell_curve_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create bell curve tooltip."""
        value_prefix = config.get('tooltip', {}).get('valuePrefix', '')
        value_suffix = config.get('tooltip', {}).get('valueSuffix', '')
        
        point_format = '<b>Data point index:</b> {point.x}<br><b>{series.name}: </b>'
        point_format = TooltipBuilder._format_point_format(value_prefix, value_suffix, '{point.y}', point_format)
        
        return {
            **base_tooltip,
            'headerFormat': '',
            'pointFormat': point_format
        }
    
    @staticmethod
    def _area_range_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create area range tooltip."""
        return base_tooltip
    
    @staticmethod
    def _pareto_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create pareto tooltip."""
        # Pareto uses different tooltips for column and spline series
        return base_tooltip
    
    @staticmethod
    def _trend_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create trend tooltip."""
        return base_tooltip
    
    @staticmethod
    def _prediction_tooltip(config: ChartConfig, base_tooltip: Dict[str, Any]) -> Dict[str, Any]:
        """Create prediction tooltip."""
        return base_tooltip
    
    @staticmethod
    def _format_point_format(value_prefix: str, value_suffix: str, point_format: str, point_series_name: str) -> str:
        """Format point format with prefix and suffix."""
        has_prefix = bool(value_prefix)
        has_suffix = bool(value_suffix)
        
        if has_prefix and has_suffix:
            return f'{point_series_name}{value_prefix}{point_format} {value_suffix}</br>'
        elif has_prefix:
            return f'{point_series_name}{value_prefix}{point_format}</br>'
        elif has_suffix:
            return f'{point_series_name}{point_format} {value_suffix}</br>'
        else:
            return f'{point_series_name}{point_format}</br>'
    
    @staticmethod
    def _format_point_format_scatter(value_prefix: str, value_suffix: str, point_format: str) -> str:
        """Format point format for scatter plots."""
        has_prefix = bool(value_prefix)
        has_suffix = bool(value_suffix)
        
        if has_prefix and has_suffix:
            return f'{value_prefix}{point_format} {value_suffix}</br>'
        elif has_prefix:
            return f'{value_prefix}{point_format}</br>'
        elif has_suffix:
            return f'{point_format} {value_suffix}</br>'
        else:
            return f'{point_format}</br>'


class PlotOptionsBuilder:
    """Builds plot options for different chart types."""
    
    @staticmethod
    def create_plot_options(config: ChartConfig, chart_type: str) -> Dict[str, Any]:
        """Create plot options based on chart type."""
        plot_options_methods = {
            'custom-boxplot': PlotOptionsBuilder._boxplot_plot_options,
            'boxplot': PlotOptionsBuilder._boxplot_plot_options,
            'area-range': PlotOptionsBuilder._area_range_plot_options,
            'bar-stack': PlotOptionsBuilder._bar_stack_plot_options,
            'column-stack': PlotOptionsBuilder._bar_stack_plot_options,
            'lollipop-stack': PlotOptionsBuilder._bar_stack_plot_options,
            'area-stack-spline': PlotOptionsBuilder._bar_stack_plot_options,
            'bar-stack-percent': PlotOptionsBuilder._bar_stack_percent_plot_options,
            'column-stack-percent': PlotOptionsBuilder._bar_stack_percent_plot_options,
            'area-stack-percent': PlotOptionsBuilder._bar_stack_percent_plot_options,
            'area-stack-percent-spline': PlotOptionsBuilder._bar_stack_percent_plot_options,
            'heatmap': PlotOptionsBuilder._heatmap_plot_options,
            'treemap': PlotOptionsBuilder._treemap_plot_options,
            'waterfall': PlotOptionsBuilder._waterfall_plot_options,
            'bell-curve': PlotOptionsBuilder._bell_curve_plot_options,
            'streamgraph': PlotOptionsBuilder._streamgraph_plot_options,
            'pie': PlotOptionsBuilder._pie_plot_options,
            'donut': PlotOptionsBuilder._pie_plot_options,
            'semi donut': PlotOptionsBuilder._semi_donut_plot_options,
            'sunburst': PlotOptionsBuilder._sunburst_plot_options,
            'funnel': PlotOptionsBuilder._funnel_plot_options,
            'pyramid': PlotOptionsBuilder._funnel_plot_options,
            'scatter': PlotOptionsBuilder._scatter_plot_options,
            'bubble': PlotOptionsBuilder._scatter_plot_options,
            'split-bubble': PlotOptionsBuilder._split_bubble_plot_options,
            'area-spline': PlotOptionsBuilder._area_spline_plot_options,
            'area-stack': PlotOptionsBuilder._area_stack_plot_options,
            'area-stack-spline': PlotOptionsBuilder._area_stack_spline_plot_options,
            'step-line': PlotOptionsBuilder._step_line_plot_options,
            'step-area': PlotOptionsBuilder._step_area_plot_options,
            'grouped-bar': PlotOptionsBuilder._grouped_plot_options,
            'grouped-column': PlotOptionsBuilder._grouped_plot_options,
            'grouped-area': PlotOptionsBuilder._grouped_plot_options,
            'grouped-line': PlotOptionsBuilder._grouped_plot_options,
            'pareto': PlotOptionsBuilder._pareto_plot_options,
            'trend': PlotOptionsBuilder._trend_plot_options,
            'prediction': PlotOptionsBuilder._prediction_plot_options
        }
        
        if chart_type in plot_options_methods:
            return plot_options_methods[chart_type](config)
        
        # Default plot options for most chart types
        return PlotOptionsBuilder._default_plot_options(config)
    
    @staticmethod
    def _default_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create default plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'series': {
                'turboThreshold': 0,
                'cursor': 'pointer',
                'stacking': None,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _boxplot_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create boxplot plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'boxplot': {
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _area_range_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create area range plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'area': {
                'stacking': None,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _bar_stack_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create bar stack plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        chart_type = config.get('type', 'column')
        if chart_type in ['bar-stack', 'bar-stack-percent']:
            key = 'bar'
        elif chart_type in ['lollipop-stack']:
            key = 'lollipop'
        else:
            key = 'column'
        
        return {
            key: {
                'stacking': 'normal',
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _bar_stack_percent_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create bar stack percent plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        data_labels['format'] = '{point.percentage:.2f}%'
        
        chart_type = config.get('type', 'column')
        if chart_type in ['bar-stack-percent']:
            key = 'bar'
        else:
            key = 'column'
        
        return {
            key: {
                'stacking': 'percent',
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _heatmap_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create heatmap plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'heatmap': {
                'stacking': None,
                'showInLegend': False,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _treemap_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create treemap plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        if not config.get('y'):
            data_labels['format'] = '{point.name} - {point.value}'
        
        return {
            'treemap': {
                'stacking': None,
                'showInLegend': False,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _waterfall_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create waterfall plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        if config.get('value') or config.get('changePercent'):
            data_labels['format'] = '{point.y:.,2f}%'
        
        return {
            'waterfall': {
                'stacking': None,
                'showInLegend': True,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _bell_curve_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create bell curve plot options."""
        return {'enabled': False}
    
    @staticmethod
    def _streamgraph_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create streamgraph plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'series': {
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _pie_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create pie chart plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        data_labels['format'] = '{point.name} : {point.formatted_data}'
        
        return {
            'pie': {
                'stacking': None,
                'showInLegend': True,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _semi_donut_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create semi donut plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        data_labels['format'] = '{point.name} : {point.formatted_data}'
        
        return {
            'pie': {
                'stacking': None,
                'showInLegend': True,
                'dataLabels': data_labels,
                'startAngle': -90,
                'endAngle': 90,
                'center': ['50%', '75%'],
                'size': '110%'
            }
        }
    
    @staticmethod
    def _sunburst_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create sunburst plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'sunburst': {
                'stacking': None,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _funnel_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create funnel plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            config.get('type', 'funnel'): {
                'stacking': None,
                'showInLegend': True,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _scatter_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create scatter plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        chart_type = config.get('type', 'scatter')
        
        return {
            chart_type: {
                'stacking': None,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _split_bubble_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create split bubble plot options."""
        return {
            'packedbubble': {
                'minSize': '20%',
                'maxSize': '100%',
                'zMin': 0,
                'zMax': 1000,
                'layoutAlgorithm': {
                    'gravitationalConstant': 0.05,
                    'enableSimulation': False,
                    'splitSeries': True,
                    'seriesInteraction': False,
                    'dragBetweenSeries': True,
                    'parentNodeLimit': True
                },
                'dataLabels': {
                    'enabled': config.get('dataLabels', {}).get('enabled', True),
                    'format': '{point.name}',
                    'style': {
                        'textOutline': 'none',
                        'fontWeight': 'normal',
                        'color': config.get('dataLabels', {}).get('style', {}).get('color', '#000000'),
                        'fontSize': config.get('dataLabels', {}).get('style', {}).get('fontSize', 11)
                    },
                    'allowOverLap': config.get('dataLabels', {}).get('allowOverLap', False)
                }
            }
        }
    
    @staticmethod
    def _area_spline_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create area spline plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'areaspline': {
                'stacking': None,
                'opacity': config.get('opacity', 1),
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _area_stack_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create area stack plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'area': {
                'stacking': 'normal',
                'opacity': config.get('opacity', 1),
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _area_stack_spline_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create area stack spline plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'areaspline': {
                'stacking': 'normal',
                'opacity': config.get('opacity', 1),
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _step_line_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create step line plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'line': {
                'stacking': None,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _step_area_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create step area plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'area': {
                'stacking': None,
                'opacity': config.get('opacity', 1),
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _grouped_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create grouped chart plot options."""
        data_labels = PlotOptionsBuilder._get_data_labels_config(config)
        
        return {
            'series': {
                'turboThreshold': 0,
                'cursor': 'pointer',
                'stacking': None,
                'dataLabels': data_labels
            }
        }
    
    @staticmethod
    def _pareto_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create pareto plot options."""
        # Pareto uses different plot options for column and spline series
        return PlotOptionsBuilder._default_plot_options(config)
    
    @staticmethod
    def _trend_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create trend plot options."""
        return PlotOptionsBuilder._default_plot_options(config)
    
    @staticmethod
    def _prediction_plot_options(config: ChartConfig) -> Dict[str, Any]:
        """Create prediction plot options."""
        return PlotOptionsBuilder._default_plot_options(config)
    
    @staticmethod
    def _get_data_labels_config(config: ChartConfig) -> Dict[str, Any]:
        """Get data labels configuration."""
        data_labels_config = config.get('dataLabels', {})
        if isinstance(data_labels_config, bool) or data_labels_config is None:
            data_labels_config = {'enabled': data_labels_config if data_labels_config is not None else True}
        
        return {
            'enabled': data_labels_config.get('enabled', True),
            'format': data_labels_config.get('format', '{point.formatted_data}'),
            'style': {
                'textShadow': data_labels_config.get('style', {}).get('textShadow', False),
                'textOutline': data_labels_config.get('style', {}).get('textOutline'),
                'color': data_labels_config.get('style', {}).get('color', '#000000'),
                'fontSize': data_labels_config.get('style', {}).get('fontSize', 10)
            },
            'allowOverLap': data_labels_config.get('allowOverLap', False)
        }