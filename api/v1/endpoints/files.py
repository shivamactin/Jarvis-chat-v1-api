from fastapi import APIRouter,Request,HTTPException,Depends
from fastapi.responses import JSONResponse,StreamingResponse
from database.database import get_db
from database.crud import create_entry,list_all
from database.schemas import ChatSentimentLogCreate
from api_utils.auth_utils import decode_token
import io
import csv


files_router = APIRouter()


@files_router.post('/store_sentiment')
async def save_sentiment(request:Request,data:ChatSentimentLogCreate,db=Depends(get_db),user=Depends(decode_token))->JSONResponse:
    try:
        if not data.question or not data.answer or not data.sentiment or not data.feedback:
            raise HTTPException(status_code=400,detail="Invalid data.")
        
        entry = create_entry(db,data)
        return JSONResponse(content={
            "status": "success",
            "id": entry.id,
            "message": "Chat record stored successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to save sentiment data. {e}")
    

@files_router.get('/get_stored_sentiments')
async def download_sentiment(request:Request,db=Depends(get_db),user=Depends(decode_token))->StreamingResponse:
    try:
        records = list_all(db)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "question", "answer", "sentiment", "feedback"])
        for r in records:
            writer.writerow([
                r.id,
                r.question,
                r.answer,
                r.sentiment,
                r.feedback
            ])

        output.seek(0)
        return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=chat_history.csv"
        }
    )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to download file. {e}")    