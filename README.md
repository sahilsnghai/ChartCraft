# ChartCraft - Highcharts Configuration API

ChartCraft is a modern, FastAPI-based API that generates Highcharts configurations from data payloads. Built with a clean, object-oriented architecture, it provides a flexible and extensible solution for creating interactive data visualizations.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Chart Types](#chart-types)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Modern Architecture**: Clean, class-based design with dependency injection
- **Extensible Chart System**: Factory pattern for easy chart type registration
- **Comprehensive Chart Library**: Support for 40+ chart types across multiple categories
- **High Performance**: Optimized for response times under 50ms
- **Flexible Data Handling**: Supports both aggregated and raw data with on-the-fly aggregation
- **Rich Configuration**: Advanced tooltip and plot options builders
- **Type Safety**: Full Pydantic model validation and type hints

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn (for development server)
- Polars (data processing)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/sahilsnghai/ChartCraft.git
   cd ChartCraft
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```

5. Access the API at `http://127.0.0.1:8000/`.

## Project Structure

```plaintext
ChartCraft/
├── main.py                          # FastAPI application entry point
├── requirements.txt                   # Python dependencies
├── README.md                        # This file
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── routes.py                # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py             # Application constants
│   │   ├── exceptions.py            # Custom exceptions
│   │   └── logging.py               # Logging configuration
│   ├── highcharts/
│   │   ├── __init__.py
│   │   ├── chartgenerator.py        # Main chart generator 
│   │   ├── chartgenerator_refactor.py  # Legacy refactored version
│   │   ├── charts/                  # Chart implementations
│   │   │   ├── __init__.py
│   │   │   ├── basic.py             # Basic charts (column, bar, line, etc.)
│   │   │   ├── pie.py               # Pie, donut, sunburst charts
│   │   │   ├── funnel.py            # Funnel and pyramid charts
│   │   │   ├── polar.py             # Scatter, bubble charts
│   │   │   ├── boxplot.py           # Boxplot charts
│   │   │   ├── specialized.py       # Specialized charts (heatmap, treemap, etc.)
│   │   │   ├── maps.py              # Map-based charts
│   │   │   ├── grid.py              # Grid charts
│   │   │   └── grouped.py           # Grouped charts
│   │   └── core/                    # Core architecture
│   │       ├── base_chart.py        # Base classes and data processors
│   │       ├── chart_factory.py     # Chart factory for registration
│   │       └── tooltip_plot_options.py  # Tooltip and plot options builders
│   └── models/
│       └── schemas.py               # Pydantic data models
```

### Key Components

- **`main.py`**: FastAPI application setup with CORS middleware
- **`app/api/routes.py`**: API endpoints with request/response validation
- **`app/highcharts/chartgenerator.py`**: Main chart generator using new architecture
- **`app/highcharts/core/chart_factory.py`**: Factory for creating chart instances
- **`app/highcharts/core/base_chart.py`**: Base classes and common functionality
- **`app/models/schemas.py`**: Pydantic models for request validation

## Usage

### Running the API

After following the installation steps, start the FastAPI server:

```bash
uvicorn main:app --reload
```

### Example Request

Send a POST request to the `/visualisation` endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/visualisation" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "resultSet": [
        ["Category A", 10],
        ["Category B", 20],
        ["Category C", 30]
      ],
      "headers": ["Category", "Value"],
      "configData": [
        {
          "type": "column",
          "x": "Category",
          "y": "Value"
        }
      ]
    }
  }'
```

### Request Format

The API expects a JSON payload with the following structure:

```json
{
  "data": {
    "resultSet": [
      // Array of data rows
    ],
    "headers": [
      // Column names
    ],
    "configData": [
      {
        "type": "chart_type",
        "x": "x_axis_column",
        "y": "y_axis_column",
        // Additional configuration options
      }
    ],
    "advance_settings": {
      // Advanced styling and behavior options
    }
  }
}
```

## API Endpoints

### `/visualisation`

- **Method**: POST
- **Description**: Generates Highcharts configuration from data payload
- **Response**: Highcharts configuration object

### `/health`

- **Method**: GET
- **Description**: Health check endpoint

### `/`

- **Method**: GET
- **Description**: Root endpoint with success message

## Chart Types

ChartCraft supports a comprehensive library of chart types organized into categories:

### Basic Charts
- Column, Bar, Line, Spline
- Area, Area Stack, Area Range
- Step Line, Step Area
- Lollipop, Stack Lollipop

### Pie Charts
- Pie, Donut, Semi Donut
- Sunburst

### Funnel Charts
- Funnel, Pyramid

### Polar Charts
- Scatter, Bubble, Split Bubble

### Boxplot Charts
- Boxplot, Custom Boxplot

### Specialized Charts
- Heatmap, Treemap
- Waterfall, Bell Curve
- Streamgraph, Pareto
- Trend, Prediction

### Map Charts
- Geo Map, Scatter Map
- Bubble Map, Heat Map

### Grid Charts
- Grid-based layouts

### Grouped Charts
- Grouped Bar, Column, Area, Line

## Architecture

ChartCraft follows a clean, object-oriented architecture with the following key patterns:

### Factory Pattern
The `ChartFactory` class manages chart type registration and instantiation, making it easy to add new chart types without modifying existing code.

### Strategy Pattern
Each chart type implements the `BaseChart` interface, providing a consistent API while allowing for specialized behavior.

### Builder Pattern
The `TooltipBuilder` and `PlotOptionsBuilder` classes provide a fluent interface for constructing complex chart configurations.

### Dependency Injection
The `ChartGenerator` class uses dependency injection to receive its collaborators, making it easy to test and extend.

### Key Classes

- **`ChartGenerator`**: Main orchestrator that coordinates chart generation
- **`ChartFactory`**: Creates chart instances based on type
- **`BaseChart`**: Abstract base class for all chart types
- **`ChartConfig`**: Immutable wrapper for chart configuration
- **`TooltipBuilder`**: Builds tooltip configurations
- **`PlotOptionsBuilder`**: Builds plot options configurations

## Configuration

### Advance Settings

The API supports advanced configuration through the `advance_settings` field:

```json
{
  "dataLabels": {
    "enabled": true,
    "format": "{point.y}",
    "style": {
      "color": "#000000",
      "fontSize": "12px"
    }
  },
  "xAxis": {
    "title": "X Axis Title",
    "labelColor": "#666666"
  },
  "yAxis": {
    "title": "Y Axis Title",
    "gridLineWidth": 1
  },
  "legend": {
    "visible": true,
    "align": "center"
  },
  "chartTitle": {
    "text": "Chart Title",
    "align": "left"
  },
  "chartSubTitle": {
    "text": "Chart Subtitle"
  },
  "chartSpacing": {
    "marginTop": 10,
    "marginBottom": 20
  },
  "zoomType": "x",
  "scrollMax": 100,
  "zooming": {
    "mouseWheel": true
  },
  "opacity": 0.8,
  "backgroundColor": "#ffffff",
  "plotBackgroundColor": "#f5f5f5",
  "plotBorderColor": "#cccccc",
  "plotBorderWidth": 1,
  "hoverHighlightColor": "#333333"
}
```

### Chart Configuration

Each chart in the `configData` array supports the following properties:

- **`type`**: Chart type (e.g., "column", "line", "pie")
- **`x`**: X-axis column name
- **`y`**: Y-axis column name (or array for multiple series)
- **`aggregate`**: Aggregation function ("sum", "avg", "count", etc.)
- **`groupedOn`**: Array of columns to group by
- **`opposite`**: Boolean to place series on opposite Y-axis
- **`yAxisLabel`**: Custom Y-axis label
- **`share_tooltip`**: Boolean to share tooltip across series
- **`crosshair`**: Boolean to enable crosshair
- **`hoverHighlightColor`**: Color for hover highlighting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

When adding new chart types:
1. Create a new class in the appropriate charts module
2. Inherit from `BaseChart`
3. Implement the required methods
4. Register the chart type in `chart_factory.py`

## License

This project is licensed under the MIT License - see the [LICENSE](https://choosealicense.com/licenses/mit/) file for details.
