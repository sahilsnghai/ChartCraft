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

"""exceptions.py File"""
"""exceptions.py File"""
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.core.constants import Constants

constants = Constants()


def internal_server_error(
    title: str = "Internal server error", desc: str = "Something went wrong"
):
    """

    Parameters
    ----------
    title
    desc
    """
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=desc)


def error_response(error, resp=None):
    """
    Adapts error response for FastAPI.
    Note: In FastAPI, we typically raise exceptions, but if this is used in a catch block
    to return a response, we might return a JSONResponse.
    However, the original code modified a 'resp' object.
    We will change this to raise an HTTPException if possible, or return a dict/JSONResponse.
    """
    errors = {
        "AttributeError": [
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal Server Error",
        ],
        "RuntimeError": [status.HTTP_503_SERVICE_UNAVAILABLE, "Service Unavailable"],
        "ValueError": [status.HTTP_403_FORBIDDEN, "Forbidden"],
        "KeyError": [status.HTTP_400_BAD_REQUEST, "Bad Request"],
        "IndexError": [status.HTTP_412_PRECONDITION_FAILED, "Precondition Failed"],
        "AssertionError": [status.HTTP_401_UNAUTHORIZED, "Unauthorized"],
        "PermissionError": [status.HTTP_403_FORBIDDEN, "Permission denied"],
    }

    if error in errors:
        code, message = errors[error]
        raise HTTPException(status_code=code, detail=message)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


class CustomHTTPError(HTTPException):
    """Represents a generic HTTP error."""

    def __init__(self, status_code, description, code):
        """

        :param status_code:
        :param description:
        :param code:
        """
        super().__init__(status_code=status_code, detail=description)
        self.code = code
        # We can't easily modify a global constant to affect the response in FastAPI like this
        # but we will try to maintain the side effect if it's used elsewhere,
        # though it's bad practice.
        # constants.STATUS200["status"]["code"] = self.code
        # constants.STATUS200["status"]["value"] = "internal-server-error"
        # constants.STATUS200["data"] = self.description
        # constants.STATUS200["error"] = True
        # self.error = constants.STATUS200
