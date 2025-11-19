from langgraph.graph import END,MessagesState,StateGraph,add_messages
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from chat.graph.graph import AgentGraph 
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from yaml import safe_load
from langchain_core.messages import SystemMessage,HumanMessage,BaseMessage
import json
from chat.tools.tool_utils import perform_tool_call
from chat.registries.tool_registries import TOOLRegistry
from langgraph.checkpoint.memory import MemorySaver
import os
from json import JSONDecodeError
from typing import Union,TypedDict,Annotated
from typing import TypedDict
from chat.tools import func_tools

class customstate(TypedDict):
    messages:Annotated[list[BaseMessage], add_messages]
    db_schema:str

class Agent(AgentGraph):
    def __init__(self,prompt_yaml:str,temperature:float=0.)->None:
        self.temperature = temperature
        self.prompt_yaml = prompt_yaml
        self.graph = None
        self.gpt_model = ChatOpenAI(model="gpt-5",max_tokens=128_000,temperature=self.temperature)
        self.anthropic_model = ChatAnthropic(model="claude-sonnet-4-5",temperature=self.temperature,max_tokens=64_000)
        self.google_model = ChatGoogleGenerativeAI(model="gemini-2.5-pro",temperature=self.temperature,max_tokens=65_536)
    
    #utility functions 
    def __load_prompt_yaml__(self,model_family:str)->Union[str,None]:
        if self.prompt_yaml and os.path.exists(self.prompt_yaml):
            with open(self.prompt_yaml,'r') as f:
                prompts = safe_load(f)
            return prompts[model_family.upper()]

    def __get_model__(self,model_family:str)->BaseChatModel:
        model_family = model_family.lower()
        if model_family in ['gpt','anthropic','google']:
            if "gpt" == model_family:
                return self.gpt_model
            elif "anthropic" == model_family:
                return self.anthropic_model
            elif "google" == model_family:
                return self.google_model
        else:
            raise ValueError("Currently only support gpt , anthropic and google llm family.")

    def __anthropic_tool_calls__(self,last_message:BaseMessage)->list[dict]:
        content = last_message.content
        tool_call_list = []
        for i in content:
            type_of = i.get("type")
            args = {}
            if type_of and type_of == "tool_use":
                args['id'] = i.get('id')
                args['args'] = i.get('input')
                args['tool_name'] = i.get('name')
                tool_call_list.append(args)
        return tool_call_list
    
    def __gpt_tool_access__(self,last_message:BaseMessage)->MessagesState:
        if hasattr(last_message,"additional_kwargs") and "tool_calls" in last_message.additional_kwargs:
            tool_calls = last_message.additional_kwargs["tool_calls"]
            responses = []
            for call in tool_calls:
                id = call['tc']
                name = call['function']['name']
                try:
                    args = json.loads(call['function']['arguments'].strip())
                except JSONDecodeError:
                    tool_args = {}
                tool_message = perform_tool_call(name,args,id)
                responses.append(tool_message)
            return {'messages':responses}
    
    def __anthropic_tool_access__(self,last_message:BaseMessage)->MessagesState:
        calls = self.__anthropic_tool_calls__(last_message)
        responses = []
        for call in calls:
            tool_message = perform_tool_call(call['tool_name'],call['args'],call['id'])
            responses.append(tool_message)
        return {"messages":responses}
    
    def __anthropic_conditional_split__(self,last_message:BaseMessage)->str:
        content = last_message.content
        if isinstance(content,str) or (not isinstance(content,list) and "<ai>" in content):
            return "end"
        for i in content:
            type_of = i.get("type")
            if type_of and type_of == "tool_use":
                return "tool"
            elif type_of and type_of == "text" and "<answer>" in i.get("text"):
                return "end"

        return "llm"

    def __llm_call__(self,state:MessagesState,config:RunnableConfig)->MessagesState:
        llm_family:str = config['metadata']['llm']

        system_prompt:str = self.__load_prompt_yaml__(llm_family).replace("{{tools}}",f"{TOOLRegistry.get_all_tools()}")

        if not system_prompt:
            raise ValueError("No system prompt provided.")

        if llm_family.lower() in ["gpt","anthropic"]:
            system_message = [SystemMessage(content=system_prompt)]
        else:
            system_message = [HumanMessage(content=system_prompt)]

        conversation = system_message + state['messages']
        
        chat_model = self.__get_model__(llm_family)

        response = chat_model.invoke(conversation,config)
        return {'messages':[response]}

    def __tool__access__(self,state:MessagesState,config:RunnableConfig)->MessagesState:
        llm = config['metadata']['llm'].lower()
        last_message = state['messages'][-1]
        if "anthropic" == llm:
            return self.__anthropic_tool_access__(last_message)
        if "gpt" == llm:
            return self.__gpt_tool_access__(last_message)
        return state


    def __conditional_node__(self,state:MessagesState,config:RunnableConfig)->str:
        llm = config['metadata']['llm'].lower()
        last_message = state['messages'][-1]
        
        if "gpt" == llm:
            if hasattr(last_message,"additional_kwargs") and "tool_calls" in last_message.additional_kwargs:
                return "tool"
            if hasattr(last_message,"content") and last_message.content != "":
                return "end"
        elif "anthropic" == llm:
            return self.__anthropic_conditional_split__(last_message)
        
        return "llm"


    def build_graph(self):
        graph = StateGraph(MessagesState)
        graph.add_node("llm",self.__llm_call__)
        graph.add_node("tool",self.__tool__access__)
        graph.set_entry_point("llm")

        self.gpt_model = self.gpt_model.bind_tools(TOOLRegistry.get_all_tools())
        self.anthropic_model = self.anthropic_model.bind_tools(TOOLRegistry.get_all_tools())
        self.google_model = self.google_model.bind_tools(TOOLRegistry.get_all_tools())

        graph.add_conditional_edges(
            "llm",
            self.__conditional_node__,
            {
                "tool":"tool",
                "llm":"llm",
                "end":END
            }
        )

        graph.add_edge("tool","llm")
        mem = MemorySaver()
        self.graph = graph.compile(checkpointer=mem)
        return self.graph