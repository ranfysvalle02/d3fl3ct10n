# ticketing_systems/base.py  
  
from abc import ABC, abstractmethod  
  
class TicketingSystemPlugin(ABC):  
    @abstractmethod  
    def create_ticket(self, user_id, prompt):  
        pass  