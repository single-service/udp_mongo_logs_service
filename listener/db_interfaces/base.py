from abc import ABC, abstractmethod
from typing import Any, Dict


class StorageInterface(ABC):
    
    @abstractmethod
    async def insert(self, collection: str, data: Dict[str, Any]):
        raise NotImplementedError
