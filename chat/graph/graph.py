from abc import ABC , abstractmethod

class AgentGraph(ABC):

    @abstractmethod
    def build_graph(self):
        pass

