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
   git clone https://github.com/yourusername/highcharts-api.git
   cd highcharts-api
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
- **Payload Example**: See `config/viz_examples.json`.
- **Response**: Highcharts configuration in JSON format.

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
