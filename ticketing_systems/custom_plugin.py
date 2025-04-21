# ticketing_systems/custom_plugin.py  
  
import requests  
from .base import TicketingSystemPlugin  
  
class CustomPlugin(TicketingSystemPlugin):  
    def __init__(self, api_url, api_key):  
        self.api_url = api_url  
        self.api_key = api_key  
  
    def create_ticket(self, user_id, prompt):  
        # Implement the API call to your custom system  
        response = requests.post(  
            f"{self.api_url}/tickets",  
            json={  
                "user_id": user_id,  
                "description": prompt  
            },  
            headers={  
                "Authorization": f"Bearer {self.api_key}"  
            }  
        )  
  
        if response.status_code == 201:  
            ticket_id = response.json()['id']  
            return f"Custom ticket #{ticket_id} created successfully."  
        else:  
            return "Failed to create ticket in custom system."  