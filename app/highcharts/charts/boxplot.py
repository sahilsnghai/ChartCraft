"""Boxplot chart implementations."""

from typing import Dict, List, Any, Optional
import polars as pl
import numpy as np

from ..core.base_chart import BaseChart, ChartConfig, ChartSeries, DataProcessor, AxisConfig


class BoxplotChartBase(BaseChart):
    """Base class for boxplot chart implementations."""
    
    def __init__(self, df: pl.DataFrame, config: ChartConfig):
        super().__init__(df, config)
        self.x_col_distinct_values: List[str] = []
    
    def get_series(self) -> Dict[str, Any]:
        """Generate series data for boxplot charts."""
        # Process x column if present
        if self.config.get('x'):
            self._process_x_column()
        
        # Build the series data
        series_data = self._build_boxplot_series()
        
        result = {
            'series': series_data,
            'chart': {'type': self.chart_type}
        }
        
        # Add axis configurations
        result.update(self._get_axis_config())
        
        return result
    
    def _process_x_column(self):
        """Process the x column to create indices and distinct values."""
        self.df, self.x_col_distinct_values = DataProcessor.replace_with_index(
            self.df, self.config['x']
        )
    
    def _get_axis_config(self) -> Dict[str, Any]:
        """Get axis configuration for boxplot charts."""
        if self.config.get('x'):
            return {
                'xAxis': {
                    'categories': self.x_col_distinct_values,
                    'labels': {
                        'style': {
                            'color': self.config.get('xAxis', {}).get('labelColor'),
                            'fontSize': self.config.get('xAxis', {}).get('labelFontSize', 12),
                            'fontWeight': self.config.get('xAxis', {}).get('labelFontWeight')
                        }
                    }
                },
                'yAxis': AxisConfig(self.df, self.config).get_y_axis()
            }
        else:
            return {
                'xAxis': {
                    'categories': [self.config.get('outlierAttribute', '')]
                },
                'yAxis': AxisConfig(self.df, self.config).get_y_axis()
            }


class BoxplotChart(BoxplotChartBase):
    """Standard boxplot chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'boxplot'
    
    def _build_boxplot_series(self) -> List[Dict[str, Any]]:
        """Build boxplot series data with outliers."""
        if self.config.get('x') and self.config.get('y') and self.config.get('outlierAttribute'):
            return self._get_series_with_x_y_outlier()
        elif self.config.get('y') and self.config.get('outlierAttribute'):
            return self._get_series_with_y_outlier()
        else:
            return []
    
    def _get_series_with_x_y_outlier(self) -> List[Dict[str, Any]]:
        """Build series when x, y, and outlierAttribute are present."""
        # Separate normal and outlier data
        other_df = self.df.filter(self.df['is Outlier'] != True)
        outlier_df = self.df.filter(self.df['is Outlier'])
        
        # Get unique groups
        groups = self.df[self.config['x']].unique().to_list()
        
        boxplot_data = []
        outlier_data = []
        modified_z_scores = []
        
        for group in groups:
            # Process normal data for this group
            processed_df = other_df.filter(other_df[self.config['x']] == group)
            processed_df = processed_df.sort(by=self.config['y']).head(1)
            
            # Extract boxplot statistics
            modified_z_scores.append(processed_df['Modified Z score'][0])
            boxplot_stats = [
                processed_df['Minimum'][0],
                processed_df['Q1'][0],
                processed_df['Median'][0],
                processed_df['Q3'][0],
                processed_df['Maximum'][0]
            ]
            boxplot_data.append(boxplot_stats)
            
            # Process outliers for this group
            outlier_group_df = outlier_df.filter(outlier_df[self.config['x']] == group)
            outlier_values = outlier_group_df[self.config['y']].to_list()
            outlier_attributes = outlier_group_df[self.config['outlierAttribute']].to_list()
            
            for value, attr in zip(outlier_values, outlier_attributes):
                outlier_data.append([
                    group, value, attr, self.x_col_distinct_values[group]
                ])
        
        return [
            {
                'type': 'boxplot',
                'modified_z_score': modified_z_scores,
                'attribute': self.config['outlierAttribute'],
                'name': 'Other',
                'data': boxplot_data,
                'dimension': self.config['x']
            },
            {
                'type': 'scatter',
                'name': 'Outliers',
                'attribute': self.config['outlierAttribute'],
                'dimension': self.config['x'],
                'measure': self.config['y'],
                'data': outlier_data,
                'color': self.config.get('scatterColor', 'red')
            }
        ]
    
    def _get_series_with_y_outlier(self) -> List[Dict[str, Any]]:
        """Build series when only y and outlierAttribute are present."""
        # Process normal data
        other_df = self.df.filter(self.df['is Outlier'] != True).head(1)
        
        # Process outliers
        outlier_df = self.df.filter(self.df['is Outlier'])
        outlier_values = outlier_df[self.config['y']].to_list()
        outlier_attributes = outlier_df[self.config['outlierAttribute']].to_list()
        
        # Build outlier data
        outlier_data = [
            [0, value, attr]
            for value, attr in zip(outlier_values, outlier_attributes)
        ]
        
        # Build boxplot data
        boxplot_data = [
            other_df['Minimum'][0],
            other_df['Q1'][0],
            other_df['Median'][0],
            other_df['Q3'][0],
            other_df['Maximum'][0]
        ]
        
        return [
            {
                'type': 'boxplot',
                'attribute': self.config['outlierAttribute'],
                'name': 'Other',
                'modified_z_score': outlier_df['Modified Z score'].to_list(),
                'data': [boxplot_data]
            },
            {
                'type': 'scatter',
                'name': 'Outliers',
                'attribute': self.config['outlierAttribute'],
                'measure': self.config['y'],
                'data': outlier_data,
                'color': self.config.get('scatterColor', 'red')
            }
        ]


class CustomBoxplotChart(BoxplotChartBase):
    """Custom boxplot chart implementation."""
    
    def _get_chart_type(self) -> str:
        return 'boxplot'
    
    def _build_boxplot_series(self) -> List[Dict[str, Any]]:
        """Build custom boxplot series data with outliers."""
        if self.config.get('x') and self.config.get('y') and self.config.get('outlierAttribute'):
            return self._get_series_with_x_y_outlier()
        elif self.config.get('y') and self.config.get('outlierAttribute'):
            return self._get_series_with_y_outlier()
        elif self.config.get('y') and self.config.get('x'):
            return self._get_series_with_x_y()
        else:
            return []
    
    def _get_series_with_x_y_outlier(self) -> List[Dict[str, Any]]:
        """Build series when x, y, and outlierAttribute are present."""
        # Sort data
        self.df = self.df.sort(by=[self.config['x'], self.config['outlierAttribute']])
        
        groups = self.df[self.config['x']].unique().to_list()
        boxplot_data = []
        outlier_data = []
        
        for group in groups:
            group_df = self.df.filter(self.df[self.config['x']] == group)
            group_df = group_df.sort(by=self.config['y'])
            
            # Calculate quartiles and other statistics
            q1 = group_df[self.config['y']].quantile(0.25)
            median = group_df[self.config['y']].quantile(0.5)
            q3 = group_df[self.config['y']].quantile(0.75)
            iqr = q3 - q1
            
            # Find outliers
            outliers_df = group_df.filter(
                (group_df[self.config['y']] < (q1 - 1.5 * iqr)) |
                (group_df[self.config['y']] > (q3 + 1.5 * iqr))
            )
            
            # Extract outlier data
            outliers_measure = outliers_df[self.config['y']].to_list()
            outliers_attribute = outliers_df[self.config['outlierAttribute']].to_list()
            
            # Remove outliers from main data
            main_data = group_df[self.config['y']].to_list()
            for outlier in outliers_measure:
                main_data.remove(outlier)
            
            # Calculate min and max for boxplot
            min_value = min(main_data)
            max_value = max(main_data)
            
            # Add to boxplot data
            boxplot_data.append([min_value, q1, median, q3, max_value])
            
            # Add to outlier data
            for i in range(len(outliers_measure)):
                outlier_data.append([
                    group, outliers_measure[i], outliers_attribute[i]
                ])
        
        return [
            {
                'type': 'boxplot',
                'name': self.config['outlierAttribute'],
                'data': boxplot_data
            },
            {
                'type': 'scatter',
                'name': 'Outliers',
                'attribute': self.config['outlierAttribute'],
                'measure': self.config['y'],
                'data': outlier_data
            }
        ]
    
    def _get_series_with_y_outlier(self) -> List[Dict[str, Any]]:
        """Build series when only y and outlierAttribute are present."""
        # Sort data
        self.df = self.df.sort(by=self.config['y'])
        
        data = sorted(self.df[self.config['y']].to_list())
        
        # Calculate statistics
        median = np.median(data)
        q1 = self.df[self.config['y']].quantile(0.25)
        q3 = self.df[self.config['y']].quantile(0.75)
        iqr = q3 - q1
        
        # Find outliers
        outliers_df = self.df.filter(
            (self.df[self.config['y']] < (q1 - 1.5 * iqr)) |
            (self.df[self.config['y']] > (q3 + 1.5 * iqr))
        )
        
        # Extract outlier data
        outliers_measure = outliers_df[self.config['y']].to_list()
        outliers_attribute = outliers_df[self.config['outlierAttribute']].to_list()
        
        # Remove outliers from main data
        main_data = self.df[self.config['y']].to_list()
        for outlier in outliers_measure:
            main_data.remove(outlier)
        
        # Calculate min and max for boxplot
        min_value = min(main_data)
        max_value = max(main_data)
        
        boxplot_data = [min_value, q1, median, q3, max_value]
        
        # Build outlier data
        outlier_data = [
            [0, measure, attr]
            for measure, attr in zip(outliers_measure, outliers_attribute)
        ]
        
        return [
            {
                'type': 'boxplot',
                'name': self.config['outlierAttribute'],
                'data': [boxplot_data]
            },
            {
                'type': 'scatter',
                'name': 'Outliers',
                'attribute': self.config['outlierAttribute'],
                'measure': self.config['y'],
                'data': outlier_data
            }
        ]
    
    def _get_series_with_x_y(self) -> List[Dict[str, Any]]:
        """Build series when x and y are present (no outlierAttribute)."""
        # Sort data
        self.df = self.df.sort(by=self.config['x'])
        
        groups = self.df[self.config['x']].to_list()
        boxplot_data = []
        outlier_data = []
        
        for group in groups:
            group_df = self.df.filter(self.df[self.config['x']] == group)
            
            # Calculate quartiles and other statistics
            q1 = group_df[self.config['y']].quantile(0.25)
            median = group_df[self.config['y']].quantile(0.5)
            q3 = group_df[self.config['y']].quantile(0.75)
            iqr = q3 - q1
            
            # Find outliers
            outliers_df = group_df.filter(
                (group_df[self.config['y']] < (q1 - 1.5 * iqr)) |
                (group_df[self.config['y']] > (q3 + 1.5 * iqr))
            )
            
            # Extract outlier data
            outliers_measure = outliers_df[self.config['y']].to_list()
            outliers_attribute = outliers_df[self.config['x']].to_list()
            
            # Remove outliers from main data
            main_data = group_df[self.config['y']].to_list()
            for outlier in outliers_measure:
                main_data.remove(outlier)
            
            # Calculate min and max for boxplot
            min_value = min(main_data)
            max_value = max(main_data)
            
            # Add to boxplot data
            boxplot_data.append([min_value, q1, median, q3, max_value])
            
            # Add to outlier data
            for i in range(len(outliers_measure)):
                outlier_data.append([
                    0, outliers_measure[i], outliers_attribute[i]
                ])
        
        return [
            {
                'type': 'boxplot',
                'name': self.config['x'],
                'data': boxplot_data
            },
            {
                'type': 'scatter',
                'name': 'Outliers',
                'attribute': self.config['x'],
                'measure': self.config['y'],
                'data': outlier_data
            }
        ]