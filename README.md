# Highcharts Configuration API

This project provides a FastAPI-based API endpoint `/viz` that accepts a payload and returns a Highcharts configuration. The project is structured for clarity and maintainability, allowing for easy understanding and extension.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn (for development server)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/sahilsnghai/Highchart.git
   cd Highcharts
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
   uvicorn api.endpoint:app --reload
   ```

5. Access the API at `http://127.0.0.1:8000/viz`.

## Project Structure

```plaintext
D:.
│   .gitignore
│   main.py
│   requirements.txt
│   
├───api
│       endpoint.py            # Contains the /viz FastAPI endpoint
│       data_models.py         # Pydantic models for request validation
│
├───config
│       chart_config.json      # Example of Highcharts configuration
│       example_payload.json   # Example of a single payload and its expected output
│       viz_examples.json      # All possible payloads and data structure formats
│
├───data
│       OnlineRetailSales.xlsx # Source Excel file for initial data
│       merged_data.json       # Simplified data version for faster processing
│
├───services
│       visualization.py       # Core logic for generating Highcharts configurations
│       utils.py               # Helper functions used by visualization.py
│
└───scripts
        generate_chart.py       # Script to generate a chart using merged_data.json
```

### Description of Key Files

- **`main.py`**: Entry point for the FastAPI application.
- **`api/endpoint.py`**: Contains the `/viz` API endpoint.
- **`config/viz_examples.json`**: Contains all possible payloads and their formats.
- **`services/visualization.py`**: Core logic for generating the Highcharts configuration.
- **`scripts/generate_chart.py`**: Script to generate a chart using `merged_data.json`.

## Usage

### Running the API

After following the installation steps, you can start the FastAPI server with:

```bash
uvicorn api.endpoint:app --reload
```

### Example Request

You can send a POST request to the `/viz` endpoint with a payload to receive a Highcharts configuration.

Example:
```bash
curl -X POST "http://127.0.0.1:8000/viz" -H "Content-Type: application/json" -d @config/example_payload.json
```

### Script Usage

To generate a chart using the provided data:

```bash
python scripts/generate_chart.py
```

## API Endpoints

### `/viz`

- **Method**: POST
- **Description**: Accepts a payload and returns a Highcharts configuration.
- **Payload Example**:

  ```json
  {
      "resultSet": [
          [
              "Southeast Asia",
              59.796,
              "Third Party Marketplace",
              555.516
          ],
          [
              "Central",
              23.904,
              "Social Media",
              1076.004
          ],
          [
              "EMEA",
              53.07,
              "Third Party Marketplace",
              204.15
          ],
          [
              "East",
              19.824,
              "Coupan site",
              264.32
          ],
          [
              "Southeast Asia",
              -17.1258,
              "Third Party Marketplace",
              264.9942
          ],
          [
              "Central Asia",
              -63.54,
              "Coupan site",
              68.94
          ],
          [
              "Southeast Asia",
              29.436,
              "Third Party Marketplace",
              195.786
          ],
          [
              "South",
              1.999,
              "Social Media",
              31.984
          ],
          [
              "Southeast Asia",
              -137.349,
              "Third Party Marketplace",
              876.231
          ],
          [
              "Central Asia",
              10.74,
              "Third Party Marketplace",
              71.94
          ],
          [
              "EMEA",
              14.49,
              "Direct through website",
              51.84
          ],
          [
              "South",
              28.98,
              "Direct through website",
              193.41
          ],
          [
              "South",
              -97.74,
              "Third Party Marketplace",
              254.88
          ]
      ],
      "headers": [
          "Region",
          "Profit",
          "Channel",
          "Sales"
      ],
      "configData": [
          {
              "type": "line",
              "x": "Region",
              "y": "Profit",
              "aggregate": "sum",
              "groupedOn": [
                  "Channel",
                  "Region"
              ]
          },
          {
              "type": "line",
              "x": "Region",
              "y": "Sales",
              "aggregate": "sum",
              "yopposite": true,
              "groupedOn": [
                  "Channel",
                  "Region"
              ]
          }
      ]
  }
  ```

- **Response**: Highcharts configuration in JSON format.

### Performance and Flexibility

This API is optimized for speed, with a response time of under 50ms, and is capable of generating multiple charts simultaneously. By default, the `/viz` endpoint expects aggregated data, but if the user lacks pre-aggregated data, they can use the `aggregate` key to define the aggregation type and apply groupings based on the provided columns. Additionally, users can customize their charts by assigning specific colors to columns or individual values.

## Configuration

- **`config/chart_config.json`**: Contains a sample Highcharts configuration.
- **`config/example_payload.json`**: An example of a single payload.
- **`data/OnlineRetailSales.xlsx`**: Source Excel file with initial data.
- **`data/merged_data.json`**: Simplified data version for faster processing.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://choosealicense.com/licenses/mit/) file for details.
