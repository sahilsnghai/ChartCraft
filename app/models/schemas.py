from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChartData(BaseModel):
    resultSet: Optional[List[Dict[str, Any]]] = None
    headers: Optional[List[Dict[str, Any]]] = (
        None  # Schema for polars, might be list of dicts or list of strings depending on usage.
    )
    # In app.py: schema=req_data['data']['headers']
    # Polars schema can be a list of names or dict of name:type.
    # Let's assume Any for now to be safe, or List[str] / Dict.
    configData: Optional[List[Dict[str, Any]]] = None
    advance_settings: Optional[Dict[str, Any]] = None


class ChartRequestPayload(BaseModel):
    data: ChartData


class ChartResponse(BaseModel):
    # The result from generate_viz is a dict (Highcharts config)
    # It returns a dict.
    # We can use Dict[str, Any] or a more specific model if we knew the Highcharts schema well.
    # For now, Dict[str, Any] is safe.
    chart: Optional[Dict[str, Any]] = None
    # The response in app.py was json.dumps(result).
    # result = generate_viz(...)
    # So it's just the result dict.
