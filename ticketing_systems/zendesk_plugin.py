# ticketing_systems/zendesk_plugin.py  
  
import requests  
from .base import TicketingSystemPlugin  
  
class ZendeskPlugin(TicketingSystemPlugin):  
    def __init__(self, subdomain, email, api_token):  
        self.subdomain = subdomain  
        self.email = email  
        self.api_token = api_token  
  
    def create_ticket(self, user_id, prompt):  
        zendesk_url = f'https://{self.subdomain}.zendesk.com/api/v2/requests.json'  
        headers = {'Content-Type': 'application/json'}  
        data = {  
            "request": {  
                "subject": "Support request from Slack bot",  
                "comment": {"body": prompt},  
                "requester": {"name": user_id}  
            }  
        }  
  
        response = requests.post(  
            zendesk_url,  
            json=data,  
            headers=headers,  
            auth=(f'{self.email}/token', self.api_token)  
        )  
  
        if response.status_code == 201:  
            ticket_id = response.json()['request']['id']  
            return f"Zendesk ticket #{ticket_id} created successfully."  
        else:  
            return "Failed to create Zendesk ticket."  