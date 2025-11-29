import json

import polars as pl
from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import error_response
from app.core.logging import set_up_logging
from app.models.schemas import ChartRequestPayload
from app.highcharts.viz_generator import generate_viz

router = APIRouter()
logger = set_up_logging()


@router.post("/visualisation", status_code=status.HTTP_200_OK)
async def create_chart(payload: ChartRequestPayload):
    try:
        logger.info(payload.model_dump())
        data = payload.data.resultSet
        headers = payload.data.headers
        config = payload.data.configData
        advance_settings = payload.data.advance_settings

        if data is None:
            logger.info("Please provide the dataframe to plot a chart")
            # The original code logged this but continued?
            # "if df is None: ... elif config is None: ... else: logger.info..."
            # Then it called generate_viz.
            # If df is None, generate_viz might fail or handle it.
            # Let's assume we should proceed but maybe df will be empty or None.
            # pl.DataFrame(data=None) creates empty DF.

        # Polars DataFrame creation
        # schema argument in polars can be list of names or dict.
        # headers from payload might be compatible.
        try:
            df = pl.DataFrame(
                data=data, schema=headers, orient="row", infer_schema_length=None
            )
        except Exception as e:
            logger.error(f"Error creating DataFrame: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data for DataFrame: {str(e)}",
            )

        if (
            df is None
        ):  # Should not happen with polars constructor unless data is None and it returns something else?
            logger.info("Please provide the dataframe to plot a chart")
        elif config is None:
            logger.info("Please provide configuration to create a chart.")
        elif df.is_empty() and config is None:
            logger.info(
                "Please provide configuration and dataframe to create a chart configuration."
            )
        else:
            logger.info("Generating chart configuration.")

        result = generate_viz(advance_settings=advance_settings, df=df, config=config)
        logger.info(result)
        return result

    except Exception as ex:
        logger.error(ex)
        # error_response in exceptions.py raises HTTPException
        # We can use it or just raise directly.
        # The original code passed 'resp' to error_response.
        # We refactored error_response to raise HTTPException.
        error_response(type(ex).__name__)
        # If error_response doesn't raise (e.g. unknown error), we raise 500 here.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def home():
    return {"message": "Success OK 200"}


@router.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"message": "Health check OK 200"}
