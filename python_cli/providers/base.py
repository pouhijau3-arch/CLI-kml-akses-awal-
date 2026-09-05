from abc import ABC,abstractmethod
class Provider(ABC):
    @abstractmethod
    async def chat(self,messages,tools=None,stream=False): ...
