class TOOLRegistry:
    tool_set = {}

    @classmethod
    def register(cls,func):
        if func.name not in cls.tool_set:
            cls.tool_set[func.name] = func
        return func
    
    @classmethod
    def get_tool(cls,name):
        if name in cls.tool_set:
            return cls.tool_set[name]
        return None
    
    @classmethod
    def get_all_tools(cls):
        if cls.tool_set:
            return list(cls.tool_set.values())
        return []