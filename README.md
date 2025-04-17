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
   
