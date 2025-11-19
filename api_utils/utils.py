from typing import Any

class RefrenceRegistry:
    utils = {}

    @classmethod
    def set(cls,name:str,value:Any)->None:
        if not cls.utils.get(name):
            cls.utils[name] = value

    @classmethod
    def get(cls,name:str)->Any:
        return cls.utils.get(name)