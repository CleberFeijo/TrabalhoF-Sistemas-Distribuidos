from fastapi_restful.cbv import cbv
from fastapi import APIRouter, Depends, HTTPException, Query
from app.crud.crud_histories import CRUDHist
from ..deps import get_current_user
from utils.fastapi.models.response import ResponseModelDict
from utils.fastapi.models.history import (
    HistoryCreationModel,
    HistoryGetModel
)
from utils.pydantic import ObjectIdField
from loguru import logger

from utils.fastapi import OpenAPISchemaFactory

__all__ = 'router',

router = APIRouter(prefix='/history', tags=['Histories'])

@cbv(router)
class Hist:

    @router.get(
        path='/',
        responses=OpenAPISchemaFactory(200),
        summary="History information",
        description="Returns the curiosity and the webhook for chat connection.",
    )
    async def getHistory(self, history=Depends(HistoryGetModel)):
        try:
            response = CRUDHist().get_by_location(history.location)
            history_dict = {
                'tem_curiosidade': False,
                'list_curiosidades': []
            }

            for history in response:
                history_dict['tem_curiosidade'] = True
                history_dict['list_curiosidades'].append({
                    'curiosidade': history["curiosity"],
                    'websocket_id': str(history["_id"])
                })         

            return ResponseModelDict(
                message="User information returned successfully!", data=history_dict
            )
        except Exception as e:
            logger.error(f"Unexpected error in retrieving user profile: {e}")
            raise e

    @router.post(
        path='/',
    )
    def postHistory(self, body: HistoryCreationModel):
        try:
        # Try to create the user
            _ = CRUDHist().create_history(body)
            response = CRUDHist().get_by_location(body.location)
            history_dict = {
                'tem_curiosidade': False,
                'list_curiosidades': []
            }

            for history in response:
                history_dict['tem_curiosidade'] = True
                print("Daqui tá passando!")
                history_dict['list_curiosidades'].append({
                    'curiosidade': history["curiosity"],
                    'websocket_id': str(history["_id"])
                })   

            print("Chegou aqui!")
            return ResponseModelDict(message="History created successfully!", data=history_dict)
        except Exception as e:
            # Capture unexpected errors and return an HTTP 500 error
            logger.error(f"Unexpected error during history creation: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")


    @router.delete("/{hist_id}")
    def deleteUser(
        self,
        hist_id: ObjectIdField
    ):
        try:
            # Delete the user
            CRUDHist().delete_history(hist_id)

            return ResponseModelDict(
                message="History deleted successfully!", data={"hist_id": hist_id}
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"HTTP Error during history deletion: {e.detail}")
                raise e
            logger.error(f"Unexpected error during history deletion: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
