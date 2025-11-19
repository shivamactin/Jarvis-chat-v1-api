from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel
from typing import Literal,Optional
from fastapi.responses import JSONResponse,StreamingResponse
from chat.chat import thinking_chat

class ChatData(BaseModel):
    query:str
    llm:Optional[Literal['gpt','anthropic']]


inference_router = APIRouter()


@inference_router.post('/chat')
async def chat_inference(request:Request,chat_inputs:ChatData)->StreamingResponse:
    try:
        if not chat_inputs.query:
            raise HTTPException(status_code=400,detail="Please provide valid query.")

        llm = chat_inputs.llm or "anthropic"
        
        return StreamingResponse(thinking_chat(
            agent=request.app.state.agent,
            query=chat_inputs.query,
            llm=llm),
            media_type="text/plain; charset=utf-8")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail="Failed to answer, please try again.")