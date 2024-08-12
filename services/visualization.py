
import json
import pandas as pd
from services.utils import (
    DefaultEncoder,
    update_config,
    display,
    grid_config,
    CHART_CONFIG,
    stacked_plot_options,
    x_axis_options
)
from copy import deepcopy
from typing import Any



def generate_chart_config(req_data: dict) -> dict:
    """generate_chart_config

    Args:
        req_data (dict):
        req_data[headers] = ["Channel","Region","Total Sales"]
        req_data[resultSet] = : [["Third Party Marketplace", "Central", 1084168.462]....]
        req_data[configData] = [
        {
            "type": "column",
            "x": ["Channel", "Category"],
            "y": "Total Sales",
            "color": "Category",
        },
        {"type": "line", "x": ["Channel"], "y": "Total Sales"},
    ]

    Returns:
        dict: Chart Config

    Comments:
        Error Handling is left 13 jun 24

        To save into json file
            json.dump(chart_config, open("configuration/ChartConfig.json","w"), indent=4)
        To display the chart on local
            Thread(target=display,args=(json.dumps(chart_config, cls=DefaultEncoder),), daemon=True).start()
    """
    # Copying the Basic HighChart Chart Config so we don't modified the origrinal
    to_show = req_data.get("to_show", False)
    chart_config = deepcopy(CHART_CONFIG)

    # Creating a dataframe from the data in req: req_data[resultSet]
    dataframe = pd.DataFrame(
        data=req_data["resultSet"], columns=req_data["headers"]
    ).convert_dtypes()

    print(dataframe.dtypes)

    # Create a con_info dict to register the unqiue values of Dimension columns
    col_info = dataframe.dtypes.apply(lambda x: {"colType": x.name}).to_dict()

    def add_unique_values(col: dict, info: dict) -> dict[str, Any]:
        """add_unique_values
        This just create a dict of columns and its value type with its
        postion. Metadata of dataframe with it column details

        Args:
            col (dict):
            info (dict):

        Returns:
            dict[str, Any]:
        """
        if info["colType"].lower() not in ("float64", "int64"):
            print(f"fetch unqiue values of dimension {col}")
            info = dict(info, unique_values=dataframe[col].unique().tolist())
        info.update({"colIndex": dataframe.columns.get_loc(col)})
        return info

    # Updating the values in col_info dict
    col_info = dict(
        map(
            lambda col: (col, add_unique_values(col, col_info[col])),
            dataframe.columns,
        )
    )
    x_axis = y_axis = None  # starting with None
    chart_config["title"]["text"] = req_data.get(
        "discription", ""
    )  # taking title text
    try:
        print("started working on Configuration data")
        for index, dc in enumerate(req_data["configData"]):
            series = []

            # getting chart type line, bar, column etc
            chart_type: str = dc.pop("type").lower()
            print(f"working on payload {index = } for {chart_type = }")

            # based on chart fetching plotoptions
            chart_config["plotOptions"], x_axis_option, chart_type = (
                (
                    chart_config["plotOptions"] == {}
                    and stacked_plot_options.get(chart_type.lower(), {})
                    or chart_config["plotOptions"]
                ),
                x_axis_options.get(chart_type, {}),
                chart_type.split(" ")[-1],
            )

            if (chart_type == "grid"):
                chart_config = {"aggridConf": grid_config(col_info, dc)}
                chart_config['resultset'] = req_data["resultSet"]
                break
            # fetching x-axis from payload or using the last fetched. can be both as string or list.
            # Incase of list 0 index will be default
            x_axis = (
                (isinstance(dc.get("x"), list) and dc.pop("x", []))
                or (isinstance(dc.get("x"), str) and [dc.pop("x", [])])
                or x_axis
            )
            # If grouping is need fetch data from request
            grouping = dc.get("groupedOn", [])

            # fetching y-axis from request else use the last y-axis
            y_axis = dc.get("y") or y_axis

            # fetch unqiue values for x-axis from requested x-axis
            x_axis_cat = col_info[x_axis[0]].get("unique_values", "")

            dataframe_cols = list(
                set(
                    filter(
                        lambda col: isinstance(col, str),
                        ([y_axis] + x_axis + grouping),
                    )
                )
            )

            # Creating x category and y-range
            y_axis_info = {"title": {"text": y_axis}}
            x_axis_info = {"categories": sorted(x_axis_cat), **x_axis_options.get(chart_type, {})}

            print("fetch axies and created x_categories and y_ranges created dataframes")
            yindex, xindex = get_x_y_index(
                chart_config, index, y_axis_info, x_axis_info
            )

            print(f"found x and y indexes  ({xindex , yindex })")
            set_df: pd.DataFrame = dataframe[dataframe_cols]

            if x_axis_option:
                x_axis_info = group_chart(
                    dc, x_axis_info, yindex, xindex, chart_type,
                    set_df, series, x_axis, y_axis, grouping
                )
            elif grouping and x_axis and not set(x_axis) <= set(grouping):
                print("grouping on the dataframe")
                series_by_group(
                    dc, yindex, xindex, series, chart_type,
                    x_axis, y_axis, set_df, grouping,
                )
            elif all(
                list(
                    map(
                        lambda x: str(x).lower().startswith(("int", "float")),
                        set_df.dtypes.tolist(),
                    )
                )
            ):
                print("got only measures in dataframes")
                y_axis_info = {}

                # This function only runs and update series in case of only measures
                print(f"x-axis {x_axis}")
                x_axis_info = series_for_only_measure(
                    dc, yindex, xindex, series,
                    chart_type, set_df, chart_config, x_axis_info,
                )
            else:

                # This is Non-group by case or 1 dimension and 1 measure case
                # Mostly likely even if 2 dimension and a measure. use can display both
                # default we take as both dimension as on x-axis else if reqs says to aggregate
                # any one of dimension.
                print("column are less or equals to 2")
                x_axis_cat = non_groupby(
                    dc, yindex, xindex, series, chart_type, x_axis, y_axis, set_df
                )

            # To update the chart_config like x-axes and y-axis
            print(f"updating config for payload index {index}")
            add_to_config(
                dc, chart_config, series, x_axis_info, y_axis_info,
                x_axis_cat, y_axis, x_axis_option
            )

        # This function is use to add the keys and values directly from payload
        # updateConfig = {"tooltip-[0]-animation": false}
        # It will update the tooltip if exist or dyaninamiclly create the key and sets the value
        # Can create dict or list depending on request key if not exists
        list(
            map(
                lambda item: update_config(
                    item[0].split("-"), item[1], chart_config
                ),
                req_data.get("updateConfig", {}).items(),
            )
        )

    except Exception as e:
        print(f"Error Found while create config -> {e}")
        print(dataframe)

    # Uncomment this code to see charts locally and to run
    # please get installed pip install PyQt6 PyQt6-WebEngine
    # Even if not able to see charts Contact Sahil Singhai

    # DO NOT PUSH THIS UNCOMMENTED CODE TO THE GITHUB
    json.dump(chart_config, open("config/chart_config.json","w"), indent=4)
    to_show and display(json.dumps(chart_config, cls=DefaultEncoder))
    return json.loads(json.dumps(chart_config, cls=DefaultEncoder))

def get_x_y_index(
     chart_config={}, index=0, y_axis_info=None, x_axis_info=None
) -> tuple[int, int]:
    """get_x_y_index

        Args:
            chart_config (dict, optional): _description_. Defaults to {}.
            index (int, optional): _description_. Defaults to 0.
            y_axis_info (_type_, optional): _description_. Defaults to None.
            x_axis_info (_type_, optional): _description_. Defaults to None.

        Returns:
            tuple[int, int]: _description_
    )
    """
    yindex = next(
        map(
            lambda x: x[0],
            filter(
                lambda x: all(
                    map(lambda item: item in x[1].items(), y_axis_info.items())
                ),
                enumerate(chart_config["yAxis"]),
            ),
        ),
        index,
    )
    xindex = next(
        map(
            lambda x: x[0],
            filter(
                lambda x: all(
                    map(lambda item: item in x[1].items(), x_axis_info.items())
                ),
                enumerate(chart_config["xAxis"]),
            ),
        ),
        index,
    )
    return yindex, xindex

def add_to_config(
    
    dc: dict,
    chart_config: dict,
    series: list,
    x_axis_info: dict,
    y_axis_info: dict,
    x_axis_cat: list,
    y_axis: Any,
    x_axis_option: bool = False
) -> None:
    """add_to_config Updates the chart config for series, xaxis and yaxis

    Args:
        dc (dict)
        chart_config (dict)
        series (list)
        x_axis_info (dict)
        y_axis_info (dict)
        x_axis_cat (list)
        y_axis (Any)
        isgrouped (bool) : Defaults to False
    """

    len(x_axis_cat) >= 10 and x_axis_info.update(
        {
            "scrollbar": {"enabled": True},
            "labels": {
                "rotation": -45 * ((len(x_axis_cat) >= 10) + (len(x_axis_cat) >= 20))
            },
            **x_axis_option
        }
    )

    dc.get("hline") and y_axis_info.update({"plotLines": [dc.get("hline")]})
    dc.get("vline") and x_axis_info.update({"plotLines": [dc.get("vline")]})
    dc.get("hbands") and y_axis_info.update({"plotBands": [dc.get("hbands")]})
    dc.get("vbands") and x_axis_info.update({"plotBands": [dc.get("vbands")]})
    dc.get("xopposite") and x_axis_info.update({"opposite": dc.get("xopposite")})
    dc.get("yopposite") and y_axis_info.update({"opposite": dc.get("yopposite")})

    y_ind, x_ind = get_x_y_index(
        chart_config=chart_config,
        index=None,
        y_axis_info=y_axis_info,
        x_axis_info=x_axis_info,
    )

    chart_config["series"] += series
    chart_config["xAxis"] += (x_ind is None and [x_axis_info]) or []
    chart_config["yAxis"] += (y_ind is None and [y_axis_info]) or []

def non_groupby(
    
    dc: dict,
    yindex: int,
    xindex: int,
    series: list,
    chart_type: str,
    x_axis: str,
    y_axis: str,
    set_df: pd.DataFrame,
) -> list:
    """non_groupby
    This function does the base creation of chart for single dimension
    with single measure.
    If data is of 2 dimension and 1 measure and groupedOn key is not defined
    in request by default it take a dimension and a measure create chart with
    possible duplicates

    Args:
        dc (dict):
        yindex (int):
        xindex (int):
        series (list):
        chart_type (str):
        x_axis (str):
        y_axis (str):
        set_df (pd.DataFrame):

    Returns:
        series: Appends data into data.
    """

    print("Non GroupBy function")
    if dc.get("aggregate"):
        get_gp = (
            set_df.groupby(by=x_axis)[y_axis]
            .agg(y_axis=dc.get("aggregate", "sum"))
            .reset_index()
        )

        x_axis_cat = sorted(get_gp[x_axis[0]].tolist())
        series.append(
            create_series(
                dc,
                y_axis,
                yindex,
                xindex,
                get_gp["y_axis"].tolist(),
                chart_type,
                x_axis[0],
            )
        )
    else:
        x_axis_cat = sorted(set_df[x_axis[0]].tolist())
        series.append(
            create_series(
                dc,
                y_axis,
                yindex,
                xindex,
                data=set_df[y_axis].tolist(),
                chart_type=chart_type,
                x_axis=x_axis[0],
            )
        )

    return x_axis_cat

def with_group_by(
    
    dc: dict,
    yindex: int,
    xindex: int,
    series: list,
    chart_type: str,
    x_axis: str,
    y_axis: str,
    set_df: pd.DataFrame,
) -> list:
    """with_group_by Creates Series for for groupby data
    NOT IN USE CURRENTLY
    Args:
        dc (dict):
        yindex (int):
        xindex (int):
        series (_type_):
        chart_type (str):
        x_axis (str):
        y_axis (str):
        set_df (pd.DataFrame):

    Returns:
        series: Appends data into data.
        list: x axis categories
    """
    print("GroupBy function")
    if dc.get("aggregate"):
        return non_groupby(
            dc, yindex, xindex, series, chart_type, x_axis, y_axis, set_df
        )
    x_axis_cat = []
    if x_axis_cat:
        xindex = get_x_y_index(x_axis_info={"categories": x_axis_cat})

    get_gp = set_df.groupby(by=x_axis)[[y_axis, x_axis]]
    for key, group in get_gp:
        series.append(
            create_series(
                dc,
                key,
                yindex,
                xindex,
                data=group[y_axis or x_axis].tolist(),
                chart_type=chart_type,
                x_axis=x_axis,
            )
        )
    return x_axis_cat

def series_for_only_measure(
    
    dc: dict,
    yindex: int,
    xindex: int,
    series: list,
    chart_type: str,
    set_df: pd.DataFrame,
    chart_config: dict,
    x_axis_info: dict,
) -> None:
    """series_for_only_measure
    Call the series function for only the case of measures.
    Either aggregate measure 'sales -> 100'
    Or Non aggregated measure list 'sales -> 50, 30, 20'

    Args:
        req_data (dict):
        dc (dict):
        yindex (int):
        xindex (int):
        series (list):
        chart_type (str):
        x_axis (str):
        x_axis_cat (list):

    Returns:
        series: Appends data into data.
    """
    print("Series for only Mesure.")
    if len(set_df) == 1:
        x_axis_info = {"categories": set_df.columns.tolist()}
        print("Series for aggregated measure value")
        chart_config["legend"] = True
        series.append(
            create_series(
                dc,
                None,
                yindex,
                xindex,
                data=[
                    {
                        "name": name,
                        "y": y,
                    }
                    for name, y in set_df.to_dict(orient="records")[0].items()
                ],
                chart_type=chart_type,
                x_axis=None,
            )
        )
    else:
        print("Series for non-aggregated measure value")
        for name in set_df.columns:
            series.append(
                create_series(
                    dc,
                    name,
                    yindex,
                    xindex,
                    data=set_df[name].tolist(),
                    chart_type=chart_type,
                    x_axis=None,
                )
            )
    return x_axis_info

def build_dict( df: pd.DataFrame, levels: list) -> list:
    """build_dict
    Create Categories for group chart

    Args:
        df (pd.DataFrame):
        levels (list):

    Returns:
        list:
    """

    if not levels:
        return []

    current_level, *remaining_levels = levels
    values = df[current_level].unique()

    def build_category(value: str) -> dict:
        """build_category
        Create nested dict for group charts

        Args:
            value (str):

        Returns:
            dict:
        """
        filtered_df = df[df[current_level] == value]
        subcategories = build_dict(filtered_df, remaining_levels)
        rt = {"name": value}
        subcategories and rt.update({"categories": subcategories})
        return rt

    return [build_category(value) for value in values]

def group_chart(
    
    dc: dict,
    x_axis_info: dict,
    yindex: int,
    xindex: int,
    chart_type: str,
    set_df: pd.DataFrame,
    series: list,
    x_axis: list,
    y_axis: str,
    grouping: list,
):
    x_axis_info = {
        "categories": build_dict(
            set_df[x_axis + grouping], set_df[x_axis + grouping].columns.tolist()
        )
    }
    data = []
    for _ , row in set_df.groupby(x_axis)[grouping + [y_axis]]:
        data += row.rename(columns={grouping[0]:"name", y_axis: "y"}).to_dict("records")
    series.append(
        create_series(
            dc,
            y_axis,
            yindex,
            xindex,
            data=data,
            chart_type=chart_type,
            x_axis=x_axis[0],
        )
    )
    return x_axis_info

def series_by_group(
    
    dc: dict,
    yindex: int,
    xindex: int,
    series: list,
    chart_type: str,
    x_axis: str,
    y_axis: str,
    set_df: pd.DataFrame,
    grouping: int,
) -> None:
    """series_by_group
    Call the create series function for the case of groupby.

    Args:
        dc (dict):
        yindex (int):
        xindex (int):
        series (list):
        chart_type (str):
        x_axis (str):
        y_axis (str):
        set_df (pd.DataFrame):
        grouping (int):

    Retuns:
        series: Appendes data in series.
    """
    get_gp = set_df.groupby(by=grouping)[x_axis + [y_axis]]
    for key, group in get_gp:
        series.append(
            create_series(
                dc,
                key,
                yindex,
                xindex,
                data=[row[y_axis] for _, row in group.iterrows()],
                chart_type=chart_type,
                x_axis=x_axis[0],
            )
        )

def create_series(
     dc: dict, name: str | None, yindex: int, xindex: int, data: Any,
    chart_type: str, x_axis: str | None,
) -> dict[str, Any]:
    """create_series This function actually create the series with json
    structure and returns the dict which appened to the list of series.

    Args:
        dc (dict):
        name (str | None):
        yindex (int):
        xindex (int):
        data (Any):
        chart_type (str):
        x_axis (str | None):

    Returns:
        dict[str, Any]:
    """
    series = {
        "xAxis": xindex,
        "yAxis": yindex,
        "name": name if isinstance(name, str) else name[0],
        "data": data,
        "type": list(chart_type.split(" "))[-1],
        "tooltip": {
            "formatter": "function() { return this.series.name + ': ' + this.y + '<br>'; }",
        },
    }

    dc.get("tooltip") and series["tooltip"].update({**dc.get("tooltip", {})})
    (dc.get("marker") or chart_type in ("line",)) and series.update(
        {
            "marker": {
                "radius": dc.get("marker", {}).get("radius", 0),
                "symbol": dc.get("marker", {}).get("symbol", "square"),
                **dc.get("marker", {}),
            }
        }
    )

    (
        color := (dc.get("color", {}).get(name) or dc.get("color", {}).get(x_axis))
    ) and series.update({"color": color})

    (l_width := dc.get("lWidth")) or chart_type in ("line",) and series.update(
        {"lineWidth": l_width or 2}
    )
    (zones := dc.get("zones", {}).get(x_axis, [])) and series.update(
        {"zones": zones}
    )

    return series
