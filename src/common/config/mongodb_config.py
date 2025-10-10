import os

from dotenv import load_dotenv


class MongoDBConfig:
    """MongoDB configuration"""

    load_dotenv()

    URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE = os.getenv("MONGODB_DATABASE", "protexai")
    COLLECTION = os.getenv("MONGODB_COLLECTION", "metrics")
    SERVER_SELECTION_TIMEOUT_MS = 5000
