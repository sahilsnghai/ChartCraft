import pandas as pd
import json
from services.visualization import generate_chart_config

# Paths to files
excel_file = "configuration/OnlineRetailSales.xlsx"
json_output_path = "configuration/merged_data.json"
json_example_path = "config/payload_example.json"
smaller_data_path = "data/ors_smaller_data.json"

# Load the Excel file and merge sheets into a single DataFrame
# Uncomment the below lines if you need to generate a merged JSON from Excel data

# sheet1 = pd.read_excel(excel_file, sheet_name="Orders")
# sheet2 = pd.read_excel(excel_file, sheet_name="Product")
# sheet3 = pd.read_excel(excel_file, sheet_name="Address")
# sheet4 = pd.read_excel(excel_file, sheet_name="Customer")

# Merge sheets on common columns
# df = (
#     sheet1.merge(sheet2, on="Product id")
#     .merge(sheet3, on="Address id")
#     .merge(sheet4, on="Customer id")
# )

# Limit the DataFrame to the first 100 rows for processing
# df = df.head(100)

# Save the merged DataFrame to a JSON file (commented out as example data is used)
# df.to_json(open(json_output_path, "w"), orient='records', lines=True, indent=4)

# Alternatively, save in a more compact format
# json.dump(json.loads(df.to_json(orient="records")), open(json_output_path, "w"))

# Load a smaller dataset from JSON for testing
df = pd.read_json(smaller_data_path, orient="records")

# Define the headers to include in the result set
headers = [
    "Region", "Profit", "Channel", "Sales"
]

# Extract the relevant columns and limit to the first 100 rows
resultSet = df[headers].values.tolist()[:100]

# Define the configuration for charts
data = {
    "resultSet": resultSet,
    "headers": headers,
    "to_show": False,
    "configData": [
        {
            "type": "line",
            "x": headers[0],  # X-axis header
            "y": headers[1],  # Y-axis header
            "aggregate": "sum",  # Aggregation function
            "groupedOn": [headers[2], headers[0]],  # Grouping fields
        },
        {
            "type": "line",
            "x": headers[0],
            "y": headers[3],
            "aggregate": "sum",
            "yopposite": True,  # Display Y-axis on opposite side
            "groupedOn": [headers[2], headers[0]],
        },
        {
            "type": "column",
            "x": headers[0],
            "y": headers[3],
            "aggregate": "sum",
            "yopposite": True,
            "groupedOn": [headers[2], headers[0]],
        }
    ],
}

# Save the example payload configuration to a JSON file
json.dump(data, open(json_example_path, "w"), indent=4)

# Generate the chart configuration using the defined data
generate_chart_config(data)
