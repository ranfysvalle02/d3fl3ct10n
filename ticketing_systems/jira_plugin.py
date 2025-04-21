# ticketing_systems/jira_plugin.py  
  
import requests  
from requests.auth import HTTPBasicAuth  
from .base import TicketingSystemPlugin  
  
class JiraPlugin(TicketingSystemPlugin):  
    def __init__(self, domain, email, api_token, project_key):  
        self.domain = domain  
        self.email = email  
        self.api_token = api_token  
        self.project_key = project_key  
  
    def create_ticket(self, user_id, prompt):  
        url = f'https://{self.domain}.atlassian.net/rest/api/3/issue'  
        headers = {'Content-Type': 'application/json'}  
        data = {  
            "fields": {  
                "project": {  
                    "key": self.project_key  
                },  
                "summary": "Support request from Slack bot",  
                "description": prompt,  
                "issuetype": {  
                    "name": "Task"  
                }  
            }  
        }  
  
        response = requests.post(  
            url,  
            json=data,  
            headers=headers,  
            auth=HTTPBasicAuth(self.email, self.api_token)  
        )  
  
        if response.status_code == 201:  
            issue_key = response.json()['key']  
            return f"JIRA issue {issue_key} created successfully."  
        else:  
            return "Failed to create JIRA issue."  