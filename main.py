from fastapi import FastAPI
from models.data_models import request
from services.visualization import generate_chart_config

app = FastAPI()


@app.get("/viz")
def read_root(req: request):
    req: dict = req.model_dump()
    generate_chart_config(req_data=req)
    return True

