![](https://d1eipm3vz40hy0.cloudfront.net/images/AMER/fourillustratedreasonstouseticketdeflection.png)

# Building an AI-Powered Slack Bot for Ticket Deflection using Azure OpenAI and Zendesk  

In today's digital landscape, customer support teams are continually seeking innovative ways to enhance efficiency and improve customer satisfaction. One effective strategy is **ticket deflection**, which empowers customers to resolve their issues through self-service options without direct agent involvement. By leveraging artificial intelligence (AI) and automation, businesses can significantly reduce the volume of support tickets, allowing agents to focus on more complex and high-value queries.  
   
This blog post explores how to build an AI-powered Slack bot using Python, Slack Bolt, and Azure OpenAI. This bot assists in ticket deflection by providing instant responses to user queries within Slack. We'll also discuss how integrating this bot with Zendesk can further streamline customer support operations.  
   
## Understanding Ticket Deflection  
   
Ticket deflection is a customer service strategy that minimizes the number of support tickets by offering self-service resources such as AI-powered chatbots, knowledge bases, FAQs, and community forums. By enabling customers to find answers independently, businesses can:  
   
- **Improve Customer Experience**: Provide immediate assistance without waiting for a support agent.  
- **Increase Agent Productivity**: Allow agents to focus on complex issues rather than repetitive inquiries.  
- **Scale Support Operations**: Handle multiple queries simultaneously without adding more staff.  
- **Reduce Operational Costs**: Lower the demand on support agents, reducing costs associated with large support teams.  
   
## Benefits of Using AI for Ticket Deflection  
   
Integrating AI into ticket deflection strategies amplifies these benefits:  
   
- **24/7 Support**: AI-powered bots are available around the clock, offering immediate responses regardless of time zones.  
- **Personalized Interactions**: AI can tailor responses based on user data and past interactions.  
- **Continuous Improvement**: Machine learning algorithms enable AI to improve over time by learning from interactions.  
- **Better Resource Allocation**: Agents can devote time to tasks requiring human empathy and complex problem-solving.  
   
## Overview of the AI-Powered Slack Bot  
   
Our goal is to build a Slack bot that:  
   
- Listens for mentions in Slack channels.  
- Uses Azure OpenAI to generate responses to user queries.  
- Provides interactive feedback options (e.g., thumbs up/down).  
- Allows users to create Zendesk tickets directly from Slack if their issue isn't resolved.  
   
By integrating Azure OpenAI's language capabilities with Slack and Zendesk, we create a seamless support experience that promotes ticket deflection and enhances customer satisfaction.  
   
## Prerequisites  
   
Before we begin, ensure you have:  
   
- **A Slack Workspace** where you can install and manage apps.  
- **Access to Azure OpenAI services** and the necessary API keys.  
- **A Zendesk Account** with API access to create tickets.  
- **Python 3.7** or higher installed.  
- Familiarity with Python programming and basic knowledge of APIs.  
   
## Setting Up the Slack App  
   
1. **Create a New Slack App**:  
  
   - Go to [Slack API - Your Apps](https://api.slack.com/apps) and click **"Create New App"**.  
   - Choose **"From scratch"**, provide an app name, and select your workspace.  
   
2. **Enable Socket Mode**:  
  
   - In your app settings, navigate to **"Socket Mode"** under **"Settings"**.  
   - Enable Socket Mode.  
   - Generate an **App-Level Token** with the `connections:write` scope.  
   - Note down this token (`SLACK_APP_TOKEN`).  
   
3. **Configure Bot Token Scopes**:  
  
   - Under **"OAuth & Permissions"**, add the following scopes to the **"Bot Token Scopes"**:  
     - `app_mentions:read`  
     - `chat:write`  
     - `reactions:write`  
     - `channels:history`  
     - `groups:history`  
     - `im:history`  
     - `mpim:history`  
   - Install the app to your workspace to get the `SLACK_BOT_TOKEN`.  
   
4. **Set Up Event Subscriptions**:  
  
   - Go to **"Event Subscriptions"** and enable it.  
   - Under **"Subscribe to Bot Events"**, add `app_mention`.  
   
## Setting Up Azure OpenAI  
   
1. **Create an Azure OpenAI Resource**:  
  
   - Sign in to the [Azure Portal](https://portal.azure.com/).  
   - Create a new **Azure OpenAI** resource.  
   - Note the **Endpoint** and **API Key** (your `AZURE_OPENAI_API_KEY`).  
   
2. **Deploy a Model**:  
  
   - Within your Azure OpenAI resource, deploy a model (e.g., `gpt-4` or `gpt-3.5-turbo`).  
   - Ensure your API key has access to the deployed model.  
   
## Integrating with Zendesk  
   
1. **Obtain Zendesk API Credentials**:  
  
   - Log into your Zendesk account.  
   - Navigate to **Admin** > **Channels** > **API**.  
   - Enable **Token Access** and generate a new API token.  
   - Note down the API token (`ZENDESK_API_TOKEN`).  
   
2. **Set Up Proper Permissions**:  
  
   - Ensure the API token has the necessary permissions to create tickets.  
   - Note your Zendesk subdomain (e.g., `your_subdomain` in `https://your_subdomain.zendesk.com`).  
   
## Implementing the Slack Bot  
   
First, set up your development environment.  
   
1. **Create a Project Directory**:  
  
   ```bash  
   mkdir ai_slack_bot  
   cd ai_slack_bot  
   ```  
   
2. **Create and Activate a Virtual Environment**:  
  
   ```bash  
   python3 -m venv venv  
   source venv/bin/activate  
   ```  
   
3. **Install Required Libraries**:  
  
   ```bash  
   pip install slack_bolt flask openai requests  
   ```  
   
4. **Create the Python Script**:  
  
   Create a file named `app.py` and add the following code, replacing placeholders with your actual tokens and keys.  
  
   ```python  
   import os  
   import logging  
   from slack_bolt import App  
   from slack_bolt.adapter.socket_mode import SocketModeHandler  
   from flask import Flask  
   from threading import Thread  
   import requests  
  
   # Get environment variables  
   SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')  
   SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')  
   AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')  
   AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')  
   ZENDESK_SUBDOMAIN = os.environ.get('ZENDESK_SUBDOMAIN')  
   ZENDESK_EMAIL = os.environ.get('ZENDESK_EMAIL')  
   ZENDESK_API_TOKEN = os.environ.get('ZENDESK_API_TOKEN')  
  
   # Initialize the Slack app and Flask app  
   app = App(token=SLACK_BOT_TOKEN)  
   flask_app = Flask(__name__)  
  
   # Configure logging  
   logging.basicConfig(level=logging.INFO)  
   logger = logging.getLogger(__name__)  
  
   # Define the AI response function  
   def get_answer(prompt):  
       import openai  
       openai.api_type = "azure"  
       openai.api_key = AZURE_OPENAI_API_KEY  
       openai.api_base = AZURE_OPENAI_ENDPOINT  
       openai.api_version = "2023-10-01"  # Use the correct API version  
  
       response = openai.ChatCompletion.create(  
           engine="gpt-4",  # Replace with your deployment name  
           messages=[  
               {"role": "system", "content": "You are a helpful assistant."},  
               {"role": "user", "content": prompt}  
           ],  
           temperature=0.5,  
           max_tokens=500  
       )  
       return response.choices[0].message.content.strip()  
  
   # Handle app mentions  
   @app.event("app_mention")  
   def handle_app_mention_events(body, say, logger):  
       event = body.get('event', {})  
       user = event.get('user')  
       text = event.get('text')  
       channel = event.get('channel')  
       ts = event.get('ts')  
  
       if event.get('subtype') == 'bot_message' or user is None:  
           return  
  
       # Acknowledge the user's message  
       try:  
           app.client.reactions_add(  
               channel=channel,  
               timestamp=ts,  
               name="eyes"  
           )  
       except Exception as e:  
           logger.error(f"Error adding reaction: {e}")  
  
       # Process the user's message  
       def process_and_post_answer():  
           bot_user_id = app.client.auth_test()['user_id']  
           mention_text = f"<@{bot_user_id}>"  
           prompt = text.replace(mention_text, '').strip()  
           answer = get_answer(prompt)  
  
           # Build the response blocks  
           blocks = [  
               {"type": "section", "text": {"type": "mrkdwn", "text": f"*Response:*\n{answer}"}},  
               {  
                   "type": "actions",  
                   "elements": [  
                       {  
                           "type": "button",  
                           "text": {"type": "plain_text", "text": "👍", "emoji": True},  
                           "action_id": "feedback_positive",  
                           "value": "positive_feedback"  
                       },  
                       {  
                           "type": "button",  
                           "text": {"type": "plain_text", "text": "👎", "emoji": True},  
                           "action_id": "feedback_negative",  
                           "value": "negative_feedback"  
                       },  
                       {  
                           "type": "button",  
                           "text": {"type": "plain_text", "text": "Create Zendesk Ticket"},  
                           "style": "primary",  
                           "action_id": "create_zendesk_issue",  
                           "value": prompt  
                       }  
                   ]  
               }  
           ]  
  
           # Post the response in a thread  
           try:  
               app.client.chat_postMessage(  
                   channel=channel,  
                   thread_ts=ts,  
                   blocks=blocks,  
                   text="Response"  
               )  
           except Exception as e:  
               logger.error(f"Error posting message: {e}")  
  
       # Start processing in a new thread to avoid blocking  
       processing_thread = Thread(target=process_and_post_answer)  
       processing_thread.start()  
  
   # Handle positive feedback  
   @app.action("feedback_positive")  
   def handle_feedback_positive(ack, body, client, logger):  
       ack()  
       # Optionally implement feedback handling logic  
       # For now, we'll thank the user  
       client.chat_postMessage(  
           channel=body['channel']['id'],  
           thread_ts=body['message']['ts'],  
           text="Thank you for your feedback! 😊"  
       )  
  
   # Handle negative feedback  
   @app.action("feedback_negative")  
   def handle_feedback_negative(ack, body, client, logger):  
       ack()  
       # Optionally implement feedback handling logic  
       # For now, we'll ask for more details  
       client.chat_postMessage(  
           channel=body['channel']['id'],  
           thread_ts=body['message']['ts'],  
           text="Sorry to hear that. Could you provide more details?"  
       )  
  
   # Handle Zendesk issue creation  
   @app.action("create_zendesk_issue")  
   def handle_create_zendesk_issue(ack, body, client, logger):  
       ack()  
       user_id = body['user']['id']  
       channel_id = body['channel']['id']  
       message_ts = body['message']['ts']  
       prompt = body['actions'][0]['value']  
  
       # Remove the "Create Zendesk Ticket" button to prevent multiple submissions  
       original_message = body['message']  
       blocks = original_message['blocks']  
  
       for block in blocks:  
           if block.get('type') == 'actions':  
               new_elements = [el for el in block['elements'] if el.get('action_id') != 'create_zendesk_issue']  
               block['elements'] = new_elements if new_elements else []  
  
       try:  
           client.chat_update(  
               channel=channel_id,  
               ts=message_ts,  
               blocks=blocks,  
               text=original_message.get('text', '')  
           )  
       except Exception as e:  
           logger.error(f"Error updating message to remove button: {e}")  
  
       # Create a Zendesk ticket  
       zendesk_url = f'https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/requests.json'  
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
           auth=(f'{ZENDESK_EMAIL}/token', ZENDESK_API_TOKEN)  
       )  
  
       if response.status_code == 201:  
           ticket_id = response.json()['request']['id']  
           client.chat_postMessage(  
               channel=channel_id,  
               thread_ts=message_ts,  
               text=f"Zendesk ticket #{ticket_id} created successfully."  
           )  
       else:  
           logger.error(f"Failed to create Zendesk ticket: {response.text}")  
           client.chat_postMessage(  
               channel=channel_id,  
               thread_ts=message_ts,  
               text="Failed to create Zendesk ticket."  
           )  
  
   # Run the Slack app  
   def run_slack_app():  
       handler = SocketModeHandler(app, SLACK_APP_TOKEN)  
       handler.start()  
  
   if __name__ == "__main__":  
       slack_thread = Thread(target=run_slack_app)  
       slack_thread.start()  
       flask_app.run(host='0.0.0.0', port=8080)  
   ```  
   
5. **Set Environment Variables**:  
  
   It's best practice to use environment variables for sensitive information. You can set them in your shell or use a `.env` file with a library like `python-dotenv`.  
  
   ```bash  
   export SLACK_APP_TOKEN='xapp-...'  
   export SLACK_BOT_TOKEN='xoxb-...'  
   export AZURE_OPENAI_API_KEY='your-azure-api-key'  
   export AZURE_OPENAI_ENDPOINT='https://your-openai-endpoint'  
   export ZENDESK_SUBDOMAIN='your_zendesk_subdomain'  
   export ZENDESK_EMAIL='your_email@example.com'  
   export ZENDESK_API_TOKEN='your_zendesk_api_token'  
   ```  
   
## Running and Testing the Bot  
   
1. **Run the Bot**:  
  
   ```bash  
   python app.py  
   ```  
  
   Ensure there are no errors and both the Slack bot and Flask app start successfully.  
   
2. **Test in Slack**:  
  
   - In your Slack workspace, mention the bot in a channel:  
  
     ```  
     @your_bot_name How do I reset my password?  
     ```  
  
   - The bot should react with 👀 and then reply in a thread with an AI-generated answer.  
  
   - Use the feedback buttons to test the feedback functionality.  
  
   - Click **"Create Zendesk Ticket"** to test ticket creation.  
   
3. **Verify Zendesk Ticket Creation**:  
  
   - Log into your Zendesk account and check that a new ticket has been created with the information you provided.  
   
## Conclusion  
   
By integrating Azure OpenAI with Slack and Zendesk, we've created a powerful AI-driven support system that enhances ticket deflection. This solution:  
   
- Provides instant, automated responses to user queries in Slack.  
- Offers interactive feedback options to improve future interactions.  
- Allows seamless escalation by creating Zendesk tickets directly from Slack.  
   
Implementing such a system not only improves the customer experience but also empowers support agents to focus on more complex tasks, increasing overall productivity and efficiency.  
   
## Next Steps  
   
- **Enhance the AI Model**: Customize the AI's responses by adjusting the system prompt or fine-tuning the model with your own data.  
- **Implement Feedback Handling**: Use the feedback collected to improve the bot's responses over time.  
- **Monitor Usage**: Track how users interact with the bot to identify areas for improvement.  
- **Ensure Security**: Securely store API keys and tokens, and handle user data in compliance with relevant regulations.  
   
## References  
   
- [Slack API Documentation](https://api.slack.com/)  
- [Zendesk API Documentation](https://developer.zendesk.com/api-reference/)  
- [Python Slack Bolt Library](https://slack.dev/bolt-python/concepts)  
- [OpenAI Python Library](https://github.com/openai/openai-python)  
   
---  
   


DRAFT

----------



# Building an AI-Powered Slack Bot for Ticket Deflection with Azure OpenAI and Multi-Ticketing System Integration  
   
In today’s fast-paced digital world, customer support teams are constantly seeking innovative solutions to enhance efficiency and elevate customer satisfaction. One powerful strategy is **ticket deflection**, which empowers customers to resolve their issues independently via self-service options, without the need for direct agent involvement. By leveraging artificial intelligence (AI) and automation, businesses can dramatically reduce support ticket volumes, enabling agents to focus on more complex queries. This blog post delves into crafting an AI-powered Slack bot using Python, Slack Bolt, and Azure OpenAI, designed for ticket deflection. We will also explore how integrating this bot with multiple ticketing systems like Zendesk, JIRA, Salesforce, and custom systems can streamline customer support operations further.  
   
## Understanding Ticket Deflection  
   
Ticket deflection is a customer service strategy aimed at minimizing the number of support tickets by offering self-service resources such as AI-powered chatbots, knowledge bases, FAQs, and community forums. By enabling customers to find answers independently, businesses can:  
   
- **Improve Customer Experience**: Provide immediate assistance without waiting for a support agent.  
- **Increase Agent Productivity**: Allow agents to focus on complex issues rather than repetitive inquiries.  
- **Scale Support Operations**: Handle multiple queries simultaneously without adding more staff.  
- **Reduce Operational Costs**: Lower the demand on support agents, reducing costs associated with large support teams.  
   
## Why Use AI for Ticket Deflection?  
   
Integrating AI into ticket deflection strategies amplifies these benefits:  
   
- **24/7 Support**: AI-powered bots are available around the clock, offering immediate responses regardless of time zones.  
- **Personalized Interactions**: AI can tailor responses based on user data and past interactions.  
- **Continuous Improvement**: Machine learning algorithms enable AI to improve over time by learning from interactions.  
- **Better Resource Allocation**: Agents can devote time to tasks requiring human empathy and complex problem-solving.  
   
## Overview of the AI-Powered Slack Bot  
   
Our goal is to build a Slack bot that:  
   
- Listens for mentions in Slack channels.  
- Uses Azure OpenAI to generate responses to user queries.  
- Provides interactive feedback options (e.g., thumbs up/down).  
- Supports multiple ticketing systems, allowing users to create tickets directly from Slack if their issue isn't resolved.  
   
By integrating Azure OpenAI's language capabilities with Slack and various ticketing systems, we create a seamless support experience that promotes ticket deflection and enhances customer satisfaction.  
   
## Prerequisites  
   
Before we begin, ensure you have:  
   
- **A Slack Workspace** where you can install and manage apps.  
- **Access to Azure OpenAI services** and the necessary API keys.  
- **Python 3.7** or higher installed.  
- Familiarity with Python programming and basic knowledge of APIs.  
   
## Setting Up the Slack App  
   
1. **Create a New Slack App**:  
   - Go to [Slack API - Your Apps](https://api.slack.com/apps) and click **"Create New App"**.  
   - Choose **"From scratch"**, provide an app name, and select your workspace.  
   
2. **Enable Socket Mode**:  
   - In your app settings, navigate to **"Socket Mode"** under **"Settings"**.  
   - Enable Socket Mode.  
   - Generate an **App-Level Token** with the `connections:write` scope.  
   - Note down this token (`SLACK_APP_TOKEN`).  
   
3. **Configure Bot Token Scopes**:  
   - Under **"OAuth & Permissions"**, add the following scopes to the **"Bot Token Scopes"**:  
     - `app_mentions:read`  
     - `chat:write`  
     - `reactions:write`  
   - Install the app to your workspace to get the `SLACK_BOT_TOKEN`.  
   
## Setting Up Azure OpenAI  
   
1. **Create an Azure OpenAI Resource**:  
   - Sign in to the [Azure Portal](https://portal.azure.com/).  
   - Create a new **Azure OpenAI** resource.  
   - Note the **Endpoint** and **API Key** (your `AZURE_OPENAI_API_KEY`).  
   
2. **Deploy a Model**:  
   - Within your Azure OpenAI resource, deploy a model (e.g., `gpt-4`).  
   - Ensure your API key has access to the deployed model.  
   
## Integrating with Multiple Ticketing Systems  
   
Our Slack bot supports multiple ticketing systems such as Zendesk, JIRA, Salesforce, and custom systems. This is achieved through a plugin-based architecture which allows dynamic loading and integration of various ticketing system plugins.  
   
### Configuration File (`config.yaml`)  
   
Create a `config.yaml` file to manage which ticketing systems are enabled and their respective connection details:  
   
```yaml  
ticketing_systems:  
  - name: zendesk_plugin  
    enabled: true  
    config:  
      subdomain: your_zendesk_subdomain  
      email: your_email@example.com  
      api_token: your_zendesk_api_token  
  - name: jira_plugin  
    enabled: true  
    config:  
      domain: your_jira_domain  
      email: your_email@example.com  
      api_token: your_jira_api_token  
      project_key: your_jira_project_key  
  - name: salesforce_plugin  
    enabled: false  
    config:  
      username: your_salesforce_username  
      password: your_salesforce_password  
      security_token: your_salesforce_security_token  
  - name: custom_plugin  
    enabled: false  
    config:  
      api_url: https://api.customsystem.com  
      api_key: your_custom_api_key  
```  
   
### Implementing the Slack Bot  
   
First, set up your development environment.  
   
1. **Create a Project Directory**:  
  
   ```bash  
   mkdir ai_slack_bot  
   cd ai_slack_bot  
   ```  
   
2. **Create and Activate a Virtual Environment**:  
  
   ```bash  
   python3 -m venv venv  
   source venv/bin/activate  
   ```  
   
3. **Install Required Libraries**:  
  
   ```bash  
   pip install slack_bolt flask openai requests PyYAML simple_salesforce  
   ```  
   
4. **Create the Python Script (`app.py`)**:  
  
   Implement the Slack bot using a plugin-based architecture for ticketing systems:  
  
   ```python  
   import os  
   import logging  
   from slack_bolt import App  
   from slack_bolt.adapter.socket_mode import SocketModeHandler  
   from flask import Flask  
   from threading import Thread  
   import yaml  
   import importlib  
   import pkgutil  
   from dotenv import load_dotenv  
   from openai import AzureOpenAI  
  
   load_dotenv()  
  
   # Initialize logging  
   logging.basicConfig(level=logging.INFO)  
   logger = logging.getLogger(__name__)  
  
   # Get environment variables  
   SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')  
   SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')  
   AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')  
   AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')  
  
   # Initialize the Slack app and Flask app  
   app = App(token=SLACK_BOT_TOKEN)  
   flask_app = Flask(__name__)  
  
   # Load and initialize ticketing system plugins  
   ticketing_plugins = {}  
  
   def load_plugins():  
       plugins = {}  
       package_dir = os.path.join(os.path.dirname(__file__), 'ticketing_systems')  
       for _, name, is_pkg in pkgutil.iter_modules([package_dir]):  
           if not is_pkg and name != 'base':  
               module_name = f'ticketing_systems.{name}'  
               module = importlib.import_module(module_name)  
               for attr in dir(module):  
                   attr_obj = getattr(module, attr)  
                   if isinstance(attr_obj, type):  
                       if issubclass(attr_obj, module.TicketingSystemPlugin) and attr_obj != module.TicketingSystemPlugin:  
                           plugins[name] = attr_obj  
       return plugins  
  
   def initialize_plugins():  
       global ticketing_plugins  
       available_plugins = load_plugins()  
       with open('config.yaml', 'r') as f:  
           configs = yaml.safe_load(f)  
  
       for system in configs.get('ticketing_systems', []):  
           if system.get('enabled'):  
               name = system['name']  
               config = system.get('config', {})  
               plugin_class = available_plugins.get(name)  
               if plugin_class:  
                   try:  
                       ticketing_plugins[name] = plugin_class(**config)  
                   except Exception as e:  
                       logger.error(f"Failed to initialize plugin {name}: {e}")  
  
   initialize_plugins()  
  
   # Define the AI response function  
   def get_answer(prompt):  
       azure_llm = AzureOpenAI(  
           azure_endpoint=AZURE_OPENAI_ENDPOINT,  
           api_key=AZURE_OPENAI_API_KEY,  
           api_version="2024-10-21",  
       )  
       response = azure_llm.chat.completions.create(  
           model="gpt-4o",  
           messages=[  
               {"role": "system", "content": "You are a helpful assistant."},  
               {"role": "user", "content": prompt}  
           ],  
           stream=False,  
           temperature=0.0  
       )  
       return response.choices[0].message.content  
  
   # Handle app mentions  
   @app.event("app_mention")  
   def handle_app_mention_events(body, say, logger):  
       event = body.get('event', {})  
       user = event.get('user')  
       text = event.get('text')  
       channel = event.get('channel')  
       ts = event.get('ts')  
  
       if event.get('subtype') == 'bot_message' or user is None:  
           return  
  
       try:  
           app.client.reactions_add(channel=channel, timestamp=ts, name="eyes")  
       except Exception as e:  
           logger.error(f"Error adding reaction: {e}")  
  
       def process_and_post_answer():  
           bot_user_id = app.client.auth_test()['user_id']  
           mention_text = f"<@{bot_user_id}>"  
           prompt = text.replace(mention_text, '').strip()  
           answer = get_answer(prompt)  
  
           options = []  
           for key in ticketing_plugins.keys():  
               display_name = key.capitalize()  
               options.append({"text": {"type": "plain_text", "text": display_name}, "value": f"{key}|{prompt}"})  
  
           blocks = [  
               {"type": "section", "text": {"type": "mrkdwn", "text": f"*Response:*\n{answer}"}},  
               {  
                   "type": "actions",  
                   "elements": [  
                       {"type": "button", "text": {"type": "plain_text", "text": "👍", "emoji": True}, "action_id": "feedback_positive", "value": "positive_feedback"},  
                       {"type": "button", "text": {"type": "plain_text", "text": "👎", "emoji": True}, "action_id": "feedback_negative", "value": "negative_feedback"},  
                   ]  
               }  
           ]  
  
           if options:  
               blocks[1]["elements"].append({  
                   "type": "static_select",  
                   "placeholder": {"type": "plain_text", "text": "Create Ticket in..."},  
                   "action_id": "select_ticketing_system",  
                   "options": options  
               })  
  
           try:  
               app.client.chat_postMessage(channel=channel, thread_ts=ts, blocks=blocks, text="Response")  
           except Exception as e:  
               logger.error(f"Error posting message: {e}")  
  
       processing_thread = Thread(target=process_and_post_answer)  
       processing_thread.start()  
  
   @app.action("feedback_positive")  
   def handle_feedback_positive(ack, body, client, logger):  
       ack()  
       client.chat_postMessage(channel=body['channel']['id'], thread_ts=body['message']['ts'], text="Thank you for your feedback! 😊")  
  
   @app.action("feedback_negative")  
   def handle_feedback_negative(ack, body, client, logger):  
       ack()  
       client.chat_postMessage(channel=body['channel']['id'], thread_ts=body['message']['ts'], text="Sorry to hear that. Could you provide more details?")  
  
   @app.action("select_ticketing_system")  
   def handle_select_ticketing_system(ack, body, client, logger):  
       ack()  
       user_id = body['user']['id']  
       channel_id = body['channel']['id']  
       message_ts = body['message']['ts']  
       selected_value = body['actions'][0]['selected_option']['value']  
       system_key, prompt = selected_value.split('|', 1)  
  
       plugin = ticketing_plugins.get(system_key)  
       if not plugin:  
           client.chat_postMessage(channel=channel_id, thread_ts=message_ts, text=f"Ticketing system '{system_key}' is not configured.")  
           return  
  
       original_message = body['message']  
       blocks = original_message['blocks']  
  
       for block in blocks:  
           if block.get('type') == 'actions':  
               new_elements = [el for el in block['elements'] if el.get('action_id') != 'select_ticketing_system']  
               block['elements'] = new_elements if new_elements else []  
  
       blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": f"Selected ticketing system: *{system_key.capitalize()}*"}]})  
       blocks.append({"type": "actions", "elements": [{"type": "button", "text": {"type": "plain_text", "text": "Create Ticket"}, "style": "primary", "action_id": "create_ticket", "value": f"{system_key}|{prompt}"}]})  
  
       try:  
           client.chat_update(channel=channel_id, ts=message_ts, blocks=blocks, text=original_message.get('text', ''))  
       except Exception as e:  
           logger.error(f"Error updating message: {e}")  
  
   @app.action("create_ticket")  
   def handle_create_ticket(ack, body, client, logger):  
       ack()  
       user_id = body['user']['id']  
       channel_id = body['channel']['id']  
       message_ts = body['message']['ts']  
       action_value = body['actions'][0]['value']  
       system_key, prompt = action_value.split('|', 1)  
  
       plugin = ticketing_plugins.get(system_key)  
       if not plugin:  
           client.chat_postMessage(channel=channel_id, thread_ts=message_ts, text=f"Ticketing system '{system_key}' is not configured.")  
           return  
  
       original_message = body['message']  
       blocks = original_message['blocks']  
  
       for block in blocks:  
           if block.get('type') == 'actions':  
               new_elements = [el for el in block['elements'] if el.get('action_id') != 'create_ticket']  
               block['elements'] = new_elements if new_elements else []  
  
       try:  
           client.chat_update(channel=channel_id, ts=message_ts, blocks=blocks, text=original_message.get('text', ''))  
       except Exception as e:  
           logger.error(f"Error updating message to remove 'Create Ticket' button: {e}")  
  
       progress_message = client.chat_postMessage(channel=channel_id, thread_ts=message_ts, text="Creating your ticket, please wait...")  
  
       try:  
           result_message = plugin.create_ticket(user_id, prompt)  
           client.chat_update(channel=channel_id, ts=progress_message['ts'], text=result_message)  
       except Exception as e:  
           logger.error(f"Error creating ticket: {e}")  
           client.chat_update(channel=channel_id, ts=progress_message['ts'], text="Failed to create ticket. Please try again later.")  
  
   def run_slack_app():  
       handler = SocketModeHandler(app, SLACK_APP_TOKEN)  
       handler.start()  
  
   if __name__ == "__main__":  
       slack_thread = Thread(target=run_slack_app)  
       slack_thread.start()  
       flask_app.run(host='0.0.0.0', port=8080)  
   ```  
   
### Directory Structure  
   
Your project directory should have the following structure:  
   
```plaintext  
ai_slack_bot/  
├── app.py  
├── config.yaml  
├── ticketing_systems/  
│   ├── __init__.py  
│   ├── base.py  
│   ├── zendesk_plugin.py  
│   ├── jira_plugin.py  
│   ├── salesforce_plugin.py  
│   └── custom_plugin.py  
└── venv/  
```  
   
### Additional Files and Plugins  
   
**Base Plugin Class (`ticketing_systems/base.py`)**:  
   
```python  
from abc import ABC, abstractmethod  
   
class TicketingSystemPlugin(ABC):  
    @abstractmethod  
    def create_ticket(self, user_id, prompt):  
        pass  
```  
   
**Zendesk Plugin (`ticketing_systems/zendesk_plugin.py`)**:  
   
```python  
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
```  
   
**JIRA Plugin (`ticketing_systems/jira_plugin.py`)**:  
   
```python  
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
```  
   
**Salesforce Plugin (`ticketing_systems/salesforce_plugin.py`)**:  
   
```python  
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
```  
   
**Custom Plugin (`ticketing_systems/custom_plugin.py`)**:  
   
```python  
import requests  
from .base import TicketingSystemPlugin  
   
class CustomPlugin(TicketingSystemPlugin):  
    def __init__(self, api_url, api_key):  
        self.api_url = api_url  
        self.api_key = api_key  
  
    def create_ticket(self, user_id, prompt):  
        response = requests.post(  
            f"{self.api_url}/tickets",  
            json={"user_id": user_id, "description": prompt},  
            headers={"Authorization": f"Bearer {self.api_key}"}  
        )  
  
        if response.status_code == 201:  
            ticket_id = response.json()['id']  
            return f"Custom ticket #{ticket_id} created successfully."  
        else:  
            return "Failed to create ticket in custom system."  
```  
   
## Running and Testing the Bot  
   
1. **Activate Virtual Environment**:  
  
   ```bash  
   source venv/bin/activate  
   ```  
   
2. **Run the Bot**:  
  
   ```bash  
   python app.py  
   ```  
  
   Ensure there are no errors during startup.  
   
3. **Test in Slack**:  
   - In your Slack workspace, mention the bot in a channel:  
     ```  
     @your_bot_name How do I reset my password?  
     ```  
   - The bot should react with 👀 and then reply in a thread with an AI-generated answer.  
   - Use the feedback buttons to test the feedback functionality.  
   - Use the "Create Ticket in..." dropdown to select a ticketing system and create a ticket.  
   
4. **Verify Ticket Creation**:  
   - Check the respective ticketing system to ensure the ticket was created successfully.  
   
## Conclusion  
   
By integrating Azure OpenAI with Slack and multiple ticketing systems, we’ve crafted a powerful AI-driven support system that enhances ticket deflection. This solution not only provides instant, automated responses to user queries in Slack but also offers interactive feedback options and allows seamless ticket creation across various platforms. Implementing such a system not only improves customer experience but also empowers support agents to focus on more complex tasks, increasing overall productivity and efficiency.  
   
## Next Steps  
   
- **Enhance the AI Model**: Customize the AI’s responses by adjusting the system prompt or fine-tuning the model with your own data.  
- **Implement Feedback Handling**: Use the feedback collected to improve the bot’s responses over time.  
- **Monitor Usage**: Track how users interact with the bot to identify areas for improvement.  
- **Ensure Security**: Securely store API keys and tokens, and handle user data in compliance with relevant regulations.  
   
## Notes  
   
- **Error Handling**: Each plugin should handle exceptions and return meaningful error messages.  
- **Logging**: Adjust logging levels as necessary for debugging.  
- **Extensibility**: The plugin architecture makes it easy to add support for additional ticketing systems.  
   
In conclusion, the integration of AI with Slack and multiple ticketing systems offers a robust mechanism for ticket deflection, leading to improved customer service and operational efficiency. As technology continues to advance, embracing such solutions can provide businesses with a significant competitive edge.
