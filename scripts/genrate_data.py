import pandas as pd
import json
from services.visualization import generate_chart_config



# excel_file = "configuration/OnlineRetailSales.xlsx"
# # df_dict = pd.read_excel("configuration/OnlineRetailSales.xlsx", sheet_name=None)

# sheet1 = pd.read_excel(excel_file, sheet_name="Orders")
# sheet2 = pd.read_excel(excel_file, sheet_name="Product")
# sheet3 = pd.read_excel(excel_file, sheet_name="Address")
# sheet4 = pd.read_excel(excel_file, sheet_name="Customer")

# df = (
#     sheet1.merge(sheet2, on="Product id")
#     .merge(sheet3, on="Address id")
#     .merge(sheet4, on="Customer id")
# )

# df = df.head(100)
# Save the merged DataFrame to a JSON file
# df.to_json(open('configuration/merged_data.jsonc', "w"), orient='records', lines=True, indent=4)

# json.dump(json.loads(df.to_json(orient="records")), open("configuration/merged_data.json", "w"))

df = pd.read_json("data/ors_smaller_data.json", orient="records")

[
    "Order id",
    "Customer id",
    "Address id",
    "Product id",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Sales",
    "Quantity",
    "Order Discount",
    "Profit",
    "Shipping Cost",
    "Order Priority",
    "Channel",
    "Category",
    "Sub Category",
    "Product",
    "City",
    "State",
    "Country",
    "Region",
    "Customer Name",
    "Customer Segment",
]

headers = ["Region", "Profit", "Channel", "Sales"]

print(df[headers])
resultSet = df[headers].values.tolist()[:100]


data = {
    "resultSet": resultSet,
    "headers": headers,
    "configData": [
        {
            "type": "line",
            "x": headers[0],
            "y": headers[1],
            "aggregate": "sum",
            "groupedOn": [headers[2], headers[0]],
        },
        {
            "type": "line",
            "x": headers[0],
            "y": headers[3],
            "aggregate": "sum",
            "yopposite":True,
            "groupedOn": [headers[2], headers[0]],
        }
    ],
}


json.dump(data, open("configuration/example.json", "w"), indent=4)

# data = json.load(open('configuration\Viz_endpoint_Example.json',  "r"))['data']
# print(data.keys())

generate_chart_config(data)
