"""Specialized chart implementations."""

from typing import Dict, List, Any, Optional
import polars as pl

from ..core.base_chart import BaseChart, ChartConfig, ChartSeries, DataProcessor, AxisConfig


class HeatmapChart(BaseChart):
    """Heatmap chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'heatmap'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for heatmap charts."""
        if self.config.get('x') and self.config.get('y') and self.config.get('value'):
            return self._get_series_with_x_y_value()
        elif self.config.get('value') and (self.config.get('x') or self.config.get('y')):
            return self._get_series_with_value_and_axis()
        else:
            return {'series': [], 'chart': {'type': self.chart_type}}
    
    def _get_series_with_x_y_value(self) -> Dict[str, Any]:
        """Build series when x, y, and value are present."""
        # Sort data
        self.df = self.df.sort(by=[self.config['y'], self.config['x']])
        
        # Get y-axis categories
        y_categories = self.df[self.config['y']].unique().sort().to_list()
        
        # Build matrix data
        matrix = self.df[self.config['value'][0]].to_list()
        matrix_index = 0
        matrix_data = []
        
        x_unique_count = len(self.df[self.config['x']].unique())
        y_unique_count = len(y_categories)
        
        for row in range(y_unique_count):
            for column in range(x_unique_count):
                matrix_data.append([column, row, matrix[matrix_index]])
                matrix_index += 1
        
        result = {
            'series': [{
                'type': 'heatmap',
                'name': self.config['value'][0],
                'data': matrix_data
            }],
            'chart': {'type': self.chart_type},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': {
                'title': {'text': self.config['y']},
                'categories': y_categories
            }
        }
        
        return result
    
    def _get_series_with_value_and_axis(self) -> Dict[str, Any]:
        """Build series when value and one axis are present."""
        if self.config.get('y'):
            # y-axis heatmap
            self.df = self.df.sort(by=self.config['y'])
            y_categories = self.df[self.config['y']].unique().sort().to_list()
            
            matrix = self.df[self.config['value'][0]].to_list()
            matrix_data = [
                [0, row, matrix[row]]
                for row in range(len(y_categories))
            ]
            
            result = {
                'yAxis': {
                    'title': {'text': self.config['y']},
                    'categories': y_categories
                },
                'xAxis': {'categories': matrix}
            }
        else:
            # x-axis heatmap
            self.df = self.df.sort(by=self.config['x'])
            
            matrix = self.df[self.config['value'][0]].to_list()
            matrix_data = [
                [row, 0, matrix[row]]
                for row in range(len(matrix))
            ]
            
            result = {
                'yAxis': {'categories': [self.config['value'][0]]}
            }
        
        result.update({
            'series': [{
                'type': 'heatmap',
                'name': self.config['value'][0],
                'data': matrix_data
            }],
            'chart': {'type': self.chart_type},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis()
        })
        
        return result


class TreemapChart(BaseChart):
    """Treemap chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'treemap'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for treemap charts."""
        if self.config.get('x') and self.config.get('y') and self.config.get('value'):
            return self._get_series_with_x_y_value()
        elif self.config.get('value') and self.config.get('x'):
            return self._get_series_with_value_and_x()
        else:
            return {'series': [], 'chart': {'type': self.chart_type}}
    
    def _get_series_with_x_y_value(self) -> Dict[str, Any]:
        """Build series when x, y, and value are present."""
        # Sort data
        self.df = self.df.sort(by=[self.config['y']])
        
        # Get parent categories (y values)
        parent_names = self.df[self.config['y']].unique().sort().to_list()
        
        # Build treemap data
        matrix_data = []
        
        for row, parent_name in enumerate(parent_names):
            group_df = self.df.filter(self.df[self.config['y']] == parent_name)
            group_df = group_df.sort(by=self.config['x'])
            
            values = group_df[self.config['value'][0]].to_list()
            
            # Add parent node
            matrix_data.append({
                'name': parent_name,
                'id': str(row),
                'color': self._get_color(row)
            })
            
            # Add child nodes
            x_values = group_df[self.config['x']].to_list()
            for column, (x_val, value) in enumerate(zip(x_values, values)):
                matrix_data.append({
                    'name': str(x_val),
                    'value': value,
                    'parent': str(row),
                    'parent_row': row,
                    'parent_name': parent_name
                })
        
        result = {
            'series': [{
                'type': 'treemap',
                'layoutAlgorithm': 'stripes',
                'levels': [{
                    'level': 1,
                    'layoutAlgorithm': 'sliceAndDice',
                    'dataLabels': {
                        'enabled': self.config.get('dataLabels'),
                        'align': 'left',
                        'verticalAlign': 'top',
                        'style': {'fontSize': 12},
                        'format': '{point.name}'
                    }
                }],
                'alternateStartingDirection': True,
                'name': self.config['value'][0],
                'data': matrix_data
            }],
            'chart': {'type': self.chart_type},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': {
                'title': {'text': self.config['y']},
                'categories': parent_names
            }
        }
        
        return result
    
    def _get_series_with_value_and_x(self) -> Dict[str, Any]:
        """Build series when value and x are present."""
        # Add categories for x values
        x_values = self.df[self.config['x']].to_list()
        self.df = self.df.with_columns(pl.Series(values=x_values).alias('categories'))
        
        # Build matrix data
        values = self.df[self.config['value'][0]].to_list()
        matrix_data = [
            {
                'name': x_values[i],
                'value': value,
                'colorValue': (len(x_values) - i) + 0.3
            }
            for i, value in enumerate(values)
        ]
        
        result = {
            'series': [{
                'type': 'treemap',
                'layoutAlgorithm': 'squarified',
                'name': self.config['value'][0],
                'data': matrix_data
            }],
            'chart': {'type': self.chart_type},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': {'categories': [self.config['value'][0]]}
        }
        
        return result
    
    def _get_color(self, index: int) -> str:
        """Get color for treemap nodes."""
        colors = [
            '#60A5FA', '#F87171', '#FB923C', '#FACC15', '#4ADE80', '#2DD4BF',
            '#6366F1', '#A855F7', '#F472B6', '#E879F9', '#A78BFA', '#38BDF8',
            '#22D3EE', '#A3E635', '#94A3B8', '#60A5FA', '#FCA5A5', '#FDBA74',
            '#FDE047', '#86EFAC', '#5EEAD4', '#A5B4FC', '#C084FC', '#F9A8D4',
            '#F0ABFC', '#C4B5FD', '#7DD3FC', '#CBD5E1'
        ]
        return colors[index % len(colors)]


class WaterfallChart(BaseChart):
    """Waterfall chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'waterfall'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for waterfall charts."""
        # Process x column if present
        if self.config.get('x'):
            self.df, x_values = DataProcessor.replace_with_index(self.df, self.config['x'])
        else:
            x_values = []
        
        if self.config.get('x') and self.config.get('y') and self.config.get('difference'):
            return self._get_series_with_difference()
        elif self.config.get('x') and self.config.get('y') and self.config.get('changePercent'):
            return self._get_series_with_change_percent()
        elif self.config.get('x') and self.config.get('y') and self.config.get('value'):
            return self._get_series_with_value()
        else:
            return self._get_series_basic()
    
    def _get_series_with_difference(self) -> Dict[str, Any]:
        """Build series with difference calculation."""
        # Add categories
        x_values = self.df[self.config['x']].to_list()
        self.df = self.df.with_columns(pl.Series(values=x_values).alias('categories'))
        
        # Calculate differences
        names = self.df['categories'].to_list()
        values = self.df[self.config['y']].diff().fill_null(0).to_list()
        attributes = self.df[self.config['y']].to_list()
        
        # Build data with colors
        data = [
            [name, value, attr, '#FF0000' if value < 0 else '#2CAFFE']
            for name, value, attr in zip(names, values, attributes)
        ]
        
        result = {
            'series': [{
                'type': 'waterfall',
                'name': f"Difference of {self.config['y']}",
                'attribute': self.config['y'],
                'data': data
            }],
            'chart': {'type': self.chart_type},
            'yAxis': {'title': {'text': f"Difference of {self.config['y']}"}}
        }
        
        return result
    
    def _get_series_with_change_percent(self) -> Dict[str, Any]:
        """Build series with percentage change."""
        # Add categories
        x_values = self.df[self.config['x']].to_list()
        self.df = self.df.with_columns(pl.Series(values=x_values).alias('categories'))
        
        # Calculate percentage changes
        names = self.df['categories'].to_list()
        base_values = self.df[self.config['y']].to_list()
        diff_values = self.df[self.config['y']].diff().fill_null(0).to_list()
        
        # Calculate percentages (avoid division by zero)
        percentages = []
        for i, (base, diff) in enumerate(zip(base_values, diff_values)):
            if base == 0:
                percentages.append(0.0)
            else:
                percentages.append(round(diff / base, 2))
        
        attributes = base_values
        
        # Build data with colors
        data = [
            [name, pct, attr, '#FF0000' if pct < 0 else '#2CAFFE']
            for name, pct, attr in zip(names, percentages, attributes)
        ]
        
        result = {
            'series': [{
                'type': 'waterfall',
                'name': f"Change of {self.config['y']}",
                'attribute': self.config['y'],
                'data': data
            }],
            'chart': {'type': self.chart_type},
            'yAxis': {'title': {'text': f"Change of {self.config['y']}"}}
        }
        
        return result
    
    def _get_series_with_value(self) -> Dict[str, Any]:
        """Build series with explicit values."""
        # Add categories
        x_values = self.df[self.config['x']].to_list()
        self.df = self.df.with_columns(pl.Series(values=x_values).alias('categories'))
        
        # Get data
        names = self.df['categories'].to_list()
        measures = self.df[self.config['y']].fill_null(0).to_list()
        values = self.df[self.config['value']].to_list()
        
        # Build data with colors
        data = [
            [name, measure, value, '#FF0000' if measure < 0 else '#2CAFFE']
            for name, measure, value in zip(names, measures, values)
        ]
        
        result = {
            'series': [{
                'type': 'waterfall',
                'name': self.config['y'],
                'attribute': self.config['value'],
                'data': data
            }],
            'chart': {'type': self.chart_type}
        }
        
        # Add axis configurations
        result.update({
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': AxisConfig(self.df, self.config).get_y_axis()
        })
        
        return result
    
    def _get_series_basic(self) -> Dict[str, Any]:
        """Build basic waterfall series."""
        # Add categories if x is present
        if self.config.get('x'):
            x_values = self.df[self.config['x']].to_list()
            self.df = self.df.with_columns(pl.Series(values=x_values).alias('categories'))
            names = self.df['categories'].to_list()
        else:
            names = ['']
        
        # Get data
        measures = self.df[self.config['y']].fill_null(0).to_list()
        values = self.df[self.config['y']].to_list()
        
        # Build data with colors
        data = [
            [name, measure, value, '#FF0000' if measure < 0 else '#2CAFFE']
            for name, measure, value in zip(names, measures, values)
        ]
        
        result = {
            'series': [{
                'type': 'waterfall',
                'name': self.config['y'],
                'data': data
            }],
            'chart': {'type': self.chart_type}
        }
        
        # Add axis configurations
        result.update({
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': AxisConfig(self.df, self.config).get_y_axis()
        })
        
        return result


class BellCurveChart(BaseChart):
    """Bell curve chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'bellcurve'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for bell curve charts."""
        # Get data
        data = self.df[self.config['y']].to_list()
        
        result = {
            'series': [
                {
                    'name': 'Bell curve',
                    'type': 'bellcurve',
                    'xAxis': 1,
                    'yAxis': 1,
                    'baseSeries': 1,
                    'zIndex': -1
                },
                {
                    'name': self.config['y'],
                    'type': 'scatter',
                    'data': data,
                    'accessibility': {'exposeAsGroupOnly': True},
                    'marker': {'radius': 1.5}
                }
            ],
            'chart': {'type': self.chart_type},
            'xAxis': [
                {
                    'title': {'text': self.config['y']},
                    'alignTicks': False
                },
                {
                    'title': {'text': 'Bell curve'},
                    'alignTicks': False,
                    'opposite': True
                }
            ],
            'yAxis': [
                {'title': {'text': self.config['y']}},
                {
                    'title': {'text': 'Probability Density'},
                    'opposite': True
                }
            ]
        }
        
        return result


class StreamgraphChart(BaseChart):
    """Streamgraph chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'streamgraph'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for streamgraph charts."""
        # Get unique dimensions
        dimensions = self.df[self.config['color']].unique(maintain_order=True).to_list()
        
        series_data = []
        for dimension in dimensions:
            group_df = self.df.filter(self.df[self.config['color']] == dimension)
            data = group_df[self.config['y']].to_list()
            
            series = {
                'type': 'streamgraph',
                'name': dimension,
                'data': data
            }
            series_data.append(series)
        
        result = {
            'series': series_data,
            'chart': {'type': self.chart_type},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': {'visible': False}
        }
        
        return result


class ParetoChart(BaseChart):
    """Pareto chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'pareto'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for pareto charts."""
        # Sort data by y values in descending order
        self.df = self.df.sort(self.config['y'], descending=True)
        
        # Calculate cumulative sum percentages
        self.df = self.df.with_columns(
            (
                pl.col(self.config['y']).cum_sum() /
                self.df[self.config['y']].sum() * 100
            ).alias('cumulative_percentage')
        )
        
        # Build column series (sorted values)
        column_data = self.df[self.config['y']].to_list()
        column_series = {
            'type': 'column',
            'name': self.config['y'],
            'data': column_data
        }
        
        # Build spline series (cumulative percentages)
        spline_data = self.df['cumulative_percentage'].to_list()
        spline_series = {
            'type': 'spline',
            'name': self.config.get('cum_sum_name', 'Pareto'),
            'yAxis': 1,
            'data': spline_data
        }
        
        result = {
            'series': [column_series, spline_series],
            'chart': {'type': 'column'},  # Main chart type is column
            'xAxis': {'categories': self.df[self.config['x']].to_list()},
            'yAxis': [
                {},  # Left y-axis for column
                {    # Right y-axis for spline
                    'min': 0,
                    'max': 100,
                    'labels': {'format': '{value}%'},
                    'opposite': True
                }
            ]
        }
        
        return result


class TrendChart(BaseChart):
    """Trend chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'trend'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for trend charts."""
        # Get column names for trend and change
        headers = self.df.columns
        
        # Find overall trend column
        overall_trend = next(
            (col for col in headers if any(
                sub in col.lower() and (col.lower().startswith(sub) or col.lower().endswith(sub))
                for sub in ("overall trend", "trend", "overall_trend")
            )),
            self.config.get('overallTrend', headers[1] if len(headers) > 1 else '')
        )
        
        # Find change column
        change_in = next(
            (col for col in headers if any(
                sub in col.lower() and (col.lower().startswith(sub) or col.lower().endswith(sub))
                for sub in ("change in", "change", "percentage")
            )),
            self.config.get('change', headers[2] if len(headers) > 2 else '')
        )
        
        # Build column series for main metric
        column_series = {
            'type': 'column',
            'name': self.config['y'],
            'data': self.df[self.config['y']].to_list(),
            'color': self.config.get('color', '#3f7acc')
        }
        
        # Build line series for trend
        line_series = {
            'type': 'line',
            'name': overall_trend,
            'data': self.df[overall_trend].to_list(),
            'color': '#031836',
            'zIndex': 1
        }
        
        # Build spline series for change
        spline_series = {
            'type': 'spline',
            'name': change_in,
            'data': self.df[change_in].to_list(),
            'yAxis': 1,
            'color': '#23cf08',
            'dashStyle': 'Dash'
        }
        
        result = {
            'series': [column_series, line_series, spline_series],
            'chart': {'type': 'column'},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': [
                {},  # Left y-axis
                {    # Right y-axis for change
                    'opposite': True
                }
            ]
        }
        
        return result


class PredictionChart(BaseChart):
    """Prediction chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'prediction'
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for prediction charts."""
        # Split data into historical and predicted
        df_with_y = self.df.filter(pl.col(self.config['y']).is_not_null())
        df_with_null = self.df.filter(pl.col(self.config['y']).is_null())
        
        # Get headers
        headers = self.df.columns
        
        # Find prediction column
        prediction_key = next(
            (col for col in headers if any(
                sub in col.lower() and (col.lower().startswith(sub) or col.lower().endswith(sub))
                for sub in ("prediction", "predict", "forecast", "future")
            )),
            self.config.get('prediction_key', headers[1] if len(headers) > 1 else '')
        )
        
        # Find upper and lower limit columns
        upperlimit_key = next(
            (col for col in headers if any(
                sub in col.lower() and (col.lower().startswith(sub) or col.lower().endswith(sub))
                for sub in ("upper", "upper limit", "upper_limit")
            )),
            None
        )
        
        lowerlimit_key = next(
            (col for col in headers if any(
                sub in col.lower() and (col.lower().startswith(sub) or col.lower().endswith(sub))
                for sub in ("lower", "lower limit", "lower_limit")
            )),
            None
        )
        
        # Build spline series for historical data
        historical_series = {
            'type': 'spline',
            'name': self.config['y'],
            'data': df_with_y[self.config['y']].to_list(),
            'marker': {'fillColor': 'blue', 'lineWidth': 2},
            'zIndex': 1,
            'boostThreshold': 1000,
            'showInLegend': True,
            'color': 'blue'
        }
        
        # Build prediction series
        prediction_config = self.config.copy()
        prediction_config['y'] = prediction_key
        
        predicted_data = df_with_null[prediction_key].to_list()
        last_index = len(historical_series['data']) - 1
        
        prediction_series = {
            'type': 'spline',
            'name': prediction_key,
            'data': [[last_index + i + 1, val] for i, val in enumerate(predicted_data)],
            'marker': {'fillColor': 'green', 'lineWidth': 2},
            'zIndex': 1,
            'boostThreshold': 1000,
            'color': 'green'
        }
        
        series_list = [historical_series, prediction_series]
        
        # Add area range series if limits are available
        if upperlimit_key and lowerlimit_key:
            upper_data = df_with_null[upperlimit_key].to_list()
            lower_data = df_with_null[lowerlimit_key].to_list()
            
            range_data = [
                [last_index + i + 1, lower, upper]
                for i, (lower, upper) in enumerate(zip(lower_data, upper_data))
            ]
            
            range_series = {
                'type': 'arearange',
                'name': f"{self.config['y']} Range",
                'data': range_data,
                'boostThreshold': 1000
            }
            
            series_list.append(range_series)
        
        result = {
            'series': series_list,
            'chart': {'type': 'spline'},
            'xAxis': AxisConfig(self.df, self.config).get_x_axis(),
            'yAxis': AxisConfig(self.df, self.config).get_y_axis()
        }
        
        return result