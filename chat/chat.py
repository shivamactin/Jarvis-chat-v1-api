from langchain_core.runnables import RunnableConfig
from uuid import uuid4
from langgraph.graph import MessagesState
from langgraph.types import Runnable
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from typing import Literal,AsyncGenerator,Dict
import asyncio
from api_utils.utils import RefrenceRegistry
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.crud import save_chat_in_db
from database.schemas import SaveChatRequest

async def thinking_chat(agent:Runnable,query:str,llm:Literal['gpt','anthropic'],db:Session)->AsyncGenerator[Dict[str,str],None]:
    try:
        agent:Runnable=RefrenceRegistry.get("agent")
        query_id:str = str(uuid4()) 
        config:RunnableConfig = {
            'thread_id':query_id,
            "llm":llm,
            'recursion_limit':50
            }
        
        initial_chat:MessagesState = {'messages':[HumanMessage(content=query)]}
        for events in agent.stream(initial_chat,config):
            if not events: continue
            logs = ""
            for node, value in events.items():
                ai_messages = [x for x in value['messages'] if isinstance(x,AIMessage)]
                tool_messages = [x for x in value['messages'] if isinstance(x,ToolMessage)]

                if ai_messages:
                    for ai_msg in ai_messages:
                        for content in ai_msg.content:
                            if not isinstance(content,str):
                                if content.get('type') and content['type'] == "text":
                                    logs += f"**{node}**: {content.get('text')}\n"
                                elif content.get('type') and content['type'] == 'tool_use':
                                    logs += f"**{node}**: Using {content.get('name')}\n"      
                
                if tool_messages:
                    for tool_msg in tool_messages:
                        logs += f"**{node}**: {tool_msg.content:.300}\n"

            if ai_messages and isinstance(ai_messages[0].content,str):
                save_chat_in_db(db,SaveChatRequest(question=query,answer=ai_messages[0].content))
                yield {"answer":ai_messages[0].content.encode("utf-8")}
                return 
            
            yield {"thinking":logs.encode("utf-8")}
            await asyncio.sleep(0)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to generate response. {e}")
    
    