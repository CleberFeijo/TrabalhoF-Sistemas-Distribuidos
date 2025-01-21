from typing import List, Optional
from utils.fastapi.models.history import HistoryCreationModel
from utils.fastapi.schemas.history import HistoryPostSchema, HistoryGetSchema, MSGPostSchema
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from loguru import logger
from core.database.connections import histories_collection
import os
from core.security import verify_password, get_password_hash
from core.permission import UserPermission


class CRUDHist():
    ## Done
    def create_history(self, history: HistoryCreationModel):
        latitude, longitude = map(float, history.location.split(","))
        new_history = HistoryPostSchema(
            curiosity=history.curiosity,
            location={
                "type": "Point",
                "coordinates": [longitude, latitude],
            },
            email=history.email
        ).__dict__

        try:
            result = histories_collection.insert_one(new_history)
            logger.info("History created successfully!")
            return self.get_by_id(result.inserted_id)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise e

    def delete_history(self, history_id: ObjectId):
        result = histories_collection.delete_one({"_id": history_id})
        if result.deleted_count == 0:
            raise ValueError("History not found.")
        logger.info("History deleted successfully!")
        return True

    @staticmethod
    def get_by_id(history_id: ObjectId) -> Optional[dict]:
        return histories_collection.find_one({"_id": history_id})

    def get_by_location(self, location: str):
        latitude, longitude = map(float, location.split(","))
        return self.find_nearby_histories(latitude, longitude)
    
    @staticmethod
    def find_nearby_histories(latitude, longitude, radius=200):
        try:
            results = histories_collection.find({
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "$maxDistance": radius,
                    }
                }
            })

            return list(results)
        except Exception as e:
            logger.info(f"Error while querying nearby histories: {e}")
            raise e

