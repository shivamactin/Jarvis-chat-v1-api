from chat.registries.tool_registries import TOOLRegistry
from langchain_core.messages import AIMessage,ToolMessage,BaseMessage
import re


def perform_tool_call(tool_name: str, args: dict, tool_call_id: str) -> BaseMessage:
    tool = TOOLRegistry.get_tool(tool_name)
    if tool:
        result = tool.invoke(args)
    else:
        return AIMessage(content=f"Unknown tool: {tool_name}")
    return ToolMessage(name=tool_name, content=str(result), tool_call_id=tool_call_id)


def is_safe_readonly_sql(query: str) -> bool:
    """
    Returns True only if the query does NOT contain any write modifying keywords
    like CREATE, UPDATE, DELETE, INSERT, ALTER, DROP, TRUNCATE.
    
    Case insensitive.
    """
    pattern = r"\b(create|update|delete|insert|alter|drop|truncate|replace)\b"
    return not bool(re.search(pattern, query, re.IGNORECASE))
