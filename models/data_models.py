from pydantic import BaseModel
from typing import Any


class request(BaseModel):
    resultSet: list[list]
    headers: list[str]
    configData: list[dict]