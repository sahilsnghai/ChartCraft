# Copyright © Lumenore Inc. All rights reserved.
# This software is the confidential and proprietary information of
# Lumenore Inc. "Confidential Information".
# You shall * not disclose such Confidential Information and shall use it only in
# accordance with the terms of the intellectual property agreement
# you entered into with Lumenore Inc.
# THIS SOFTWARE IS INTENDED STRICTLY FOR USE BY Lumenore Inc.
# AND ITS PARENT AND/OR SUBSIDIARY COMPANIES. Lumenore
# MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
# Lumenore SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY ANY PARTY AS A RESULT
# OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

"""constants.py File"""
import json
import polars as pl
import os
from os import path
from os.path import abspath, dirname
from typing import Any, Dict


class ConstantsMeta(type):
    """Constants Meta Class"""

    _instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super().__call__()
        return cls._instance


class Constants(metaclass=ConstantsMeta):
    """Constants Class"""

    def __init__(self):
        self.ROOT_DIR = dirname(dirname(dirname(abspath(__file__))))

        # Will remove Header later, for now it is required.
        self.HEADERS = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Accept": "application/json, text/plain, */*",
            "Authorization": None,
            "version": None,
        }

        self.STATUS200: Dict[str, Any] = {"status": {}}

        self.HEADERS_NOT_AUTH: Dict[str, str] = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "INTERNAL": "True",
        }

    def get_conn_info(self, org=None):
        """

        Parameters
        ----------
        org

        Returns
        -------

        """
        # Getting connection info from configuration
        conn_info = self.get_config(org=org)
        conn = {
            "host": conn_info["host"],
            "port": conn_info["port"],
            "user": conn_info["userName"],
            "password": conn_info["password"],
            "database": conn_info["schema"],
            "driver": conn_info["driver"],
        }
        return conn

    @staticmethod
    def get_config(org, key=None):
        """

        Parameters
        ----------
        org
        key

        Returns
        -------

        """
        root_dir = dirname(dirname(abspath(__file__)))
        json_filename = root_dir + "/configuration/configuration.json"

        if not path.exists(json_filename):
            json_filename = root_dir + "/configuration/askme-config-map-rsh"

        with open(json_filename, "r") as f:
            try:
                if org == "parameters":
                    return json.load(f)["parameters"][key]
                else:
                    return json.load(f)["dataSources"][org]

            except KeyError:
                return None


def get_response(msg="", error=False, success=1):
    """

    Parameters
    ----------
    msg
    error
    success

    Returns
    -------

    """

    return {
        "errorInfo": {
            "leftover": {"users": [], "groups": []},
            "message": msg,
        },
        "error": error,
        "success": success,
    }

def generate_data(measure=1, dimension=1):
    """
    D1 - Ship Mode
    D2 - Channel
    D3 - Order Priority
    M1 - Sales
    M2 - Profit
    M3 - Quantity
    """
    from app.core.constants import Constants

    root_dir = Constants().ROOT_DIR
    filename = os.path.join(root_dir, "data/{}D{}M.json").format(dimension, measure)
    with open(filename) as _f:
        data = json.load(_f)

    df = pl.DataFrame(data["resultSet"])

    if measure > 1 and dimension == 0:
        df = df.transpose()
        df = df.with_columns(number=0)
        data["headers"].append("number")
        df.columns = data["headers"]
    else:
        df.columns = data["headers"]
    return df