import json
from http import HTTPStatus
from statistics import mean
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

# Load sample telemetry bundle
with open("telemetry.json", "r") as f:
    telemetry_data = json.load(f)

app = FastAPI()

# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def compute_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    response = {}
    for region in regions:
        # Filter telemetry for the region
        region_data = [r for r in telemetry_data if r["region"] == region]

        if not region_data:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_percent"] for r in region_data]
        breaches = sum(1 for l in latencies if l > threshold)

        response[region] = {
            "avg_latency": round(mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(mean(uptimes), 2),
            "breaches": breaches
        }

    return JSONResponse(content=response, status_code=HTTPStatus.OK)
