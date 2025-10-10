import logging
from types import TracebackType
from typing import Type

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from common.config.mongodb_config import MongoDBConfig


class MongoDBClientManager:
    """
    Context manager for MongoDB client
    """

    def __init__(self, logger: logging.Logger) -> None:
        """
        Arguments:
            logger: Logger instance

        Returns:
            None
        """
        self.logger = logger
        self.client = None
        self.collection = None
        self.config = MongoDBConfig()

    def __enter__(self) -> Collection:
        """
        Connect to MongoDB and return collection

        Returns:
            MongoDB collection
        """
        try:
            self.logger.info(f"Connecting to MongoDB: {self.config.URI}")

            self.client = MongoClient(
                self.config.URI,
                serverSelectionTimeoutMS=self.config.SERVER_SELECTION_TIMEOUT_MS,
            )

            # Test connection
            self.client.admin.command("ping")
            self.logger.info("MongoDB connection successful")

            # Get database and collection
            db = self.client[self.config.DATABASE]
            self.collection = db[self.config.COLLECTION]

            self.logger.info(
                f"Using database: {self.config.DATABASE}, collection: {self.config.COLLECTION}"
            )

            return self.collection

        except ConnectionFailure as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            self.logger.error(f"MongoDB setup error: {e}")
            raise

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit context: close MongoDB connection
        """
        if self.client:
            try:
                self.client.close()
                self.logger.info("MongoDB connection closed")
            except Exception as e:
                self.logger.error(f"Error closing MongoDB connection: {e}")
