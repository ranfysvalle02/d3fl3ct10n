# ticketing_systems/salesforce_plugin.py  
  
from simple_salesforce import Salesforce  
from .base import TicketingSystemPlugin  
  
class SalesforcePlugin(TicketingSystemPlugin):  
    def __init__(self, username, password, security_token):  
        self.sf = Salesforce(username=username, password=password, security_token=security_token)  
  
    def create_ticket(self, user_id, prompt):  
        try:  
            case = self.sf.Case.create({  
                'Subject': 'Support request from Slack bot',  
                'Description': prompt,  
                'Origin': 'Slack Bot'  
            })  
            return f"Salesforce Case {case['id']} created successfully."  
        except Exception as e:  
            return "Failed to create Salesforce Case."  