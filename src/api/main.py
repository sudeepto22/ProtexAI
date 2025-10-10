import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import DESCENDING

from common.config.mongodb_config import MongoDBConfig
from common.utils.logger import setup_logger
from common.utils.mongodb_client import MongoDBClientManager

logger = setup_logger("API")
config = MongoDBConfig()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/metrics/latest")
def get_latest_metrics(limit: int = 10):
    """Get latest metrics from MongoDB"""
    with MongoDBClientManager(logger) as collection:
        metrics = list(
            collection.find({}, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
        )
        return {"count": len(metrics), "metrics": metrics}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
