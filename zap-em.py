# app.py  
  
import os  
import logging  
from slack_bolt import App  
from slack_bolt.adapter.socket_mode import SocketModeHandler  
from flask import Flask  
from threading import Thread  
import requests  
import yaml  
import importlib  
import pkgutil  
  
from openai import AzureOpenAI  
  
# Load environment variables from .env file if it exists  
from dotenv import load_dotenv  
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
# Function to get answer using azure_llm  
def get_answer(prompt):  
    azure_llm = AzureOpenAI(  
        azure_endpoint=AZURE_OPENAI_ENDPOINT,  
        api_key=AZURE_OPENAI_API_KEY,  
        api_version="2024-10-21",  
    )  
    response = azure_llm.chat.completions.create(  
        model="gpt-4o",  # Replace with your model name  
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
  
    # Acknowledge the user's message with a reaction  
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
  
        # Automatically generate options based on configured plugins  
        options = []  
        for key in ticketing_plugins.keys():  
            display_name = key.capitalize()  
            options.append({  
                "text": {"type": "plain_text", "text": display_name},  
                "value": f"{key}|{prompt}"  
            })  
  
        # Build the response blocks  
        blocks = [  
            {  
                "type": "section",  
                "text": {"type": "mrkdwn", "text": f"*Response:*\n{answer}"}  
            },  
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
                ]  
            }  
        ]  
  
        if options:  
            blocks[1]["elements"].append(  
                {  
                    "type": "static_select",  
                    "placeholder": {  
                        "type": "plain_text",  
                        "text": "Create Ticket in..."  
                    },  
                    "action_id": "select_ticketing_system",  
                    "options": options  
                }  
            )  
  
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
    # Thank the user  
    client.chat_postMessage(  
        channel=body['channel']['id'],  
        thread_ts=body['message']['ts'],  
        text="Thank you for your feedback! 😊"  
    )  
  
# Handle negative feedback  
@app.action("feedback_negative")  
def handle_feedback_negative(ack, body, client, logger):  
    ack()  
    # Ask for more details  
    client.chat_postMessage(  
        channel=body['channel']['id'],  
        thread_ts=body['message']['ts'],  
        text="Sorry to hear that. Could you provide more details?"  
    )  
  
# Handle ticketing system selection  
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
        client.chat_postMessage(  
            channel=channel_id,  
            thread_ts=message_ts,  
            text=f"Ticketing system '{system_key}' is not configured."  
        )  
        return  
  
    # Remove the select menu to prevent multiple submissions  
    original_message = body['message']  
    blocks = original_message['blocks']  
  
    for block in blocks:  
        if block.get('type') == 'actions':  
            new_elements = []  
            for el in block['elements']:  
                if el.get('action_id') != 'select_ticketing_system':  
                    new_elements.append(el)  
            block['elements'] = new_elements  
  
    # Add a context block to show the selected ticketing system  
    blocks.append({  
        "type": "context",  
        "elements": [  
            {  
                "type": "mrkdwn",  
                "text": f"Selected ticketing system: *{system_key.capitalize()}*"  
            }  
        ]  
    })  
  
    # Add 'Create Ticket' button  
    blocks.append({  
        "type": "actions",  
        "elements": [  
            {  
                "type": "button",  
                "text": {"type": "plain_text", "text": "Create Ticket"},  
                "style": "primary",  
                "action_id": "create_ticket",  
                "value": f"{system_key}|{prompt}"  
            }  
        ]  
    })  
  
    try:  
        client.chat_update(  
            channel=channel_id,  
            ts=message_ts,  
            blocks=blocks,  
            text=original_message.get('text', '')  
        )  
    except Exception as e:  
        logger.error(f"Error updating message: {e}")  
  
# Handle 'Create Ticket' button click  
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
        client.chat_postMessage(  
            channel=channel_id,  
            thread_ts=message_ts,  
            text=f"Ticketing system '{system_key}' is not configured."  
        )  
        return  
  
    # Remove the 'Create Ticket' button to prevent multiple submissions  
    original_message = body['message']  
    blocks = original_message['blocks']  
  
    for block in blocks:  
        if block.get('type') == 'actions':  
            new_elements = [el for el in block['elements'] if el.get('action_id') != 'create_ticket']  
            block['elements'] = new_elements if new_elements else []  
  
    try:  
        client.chat_update(  
            channel=channel_id,  
            ts=message_ts,  
            blocks=blocks,  
            text=original_message.get('text', '')  
        )  
    except Exception as e:  
        logger.error(f"Error updating message to remove 'Create Ticket' button: {e}")  
  
    # Notify the user that ticket creation is in progress  
    progress_message = client.chat_postMessage(  
        channel=channel_id,  
        thread_ts=message_ts,  
        text="Creating your ticket, please wait..."  
    )  
  
    # Create the ticket using the selected plugin  
    try:  
        result_message = plugin.create_ticket(user_id, prompt)  
        # Update the user with success message  
        client.chat_update(  
            channel=channel_id,  
            ts=progress_message['ts'],  
            text=result_message  
        )  
    except Exception as e:  
        logger.error(f"Error creating ticket: {e}")  
        # Update the user with error message  
        client.chat_update(  
            channel=channel_id,  
            ts=progress_message['ts'],  
            text="Failed to create ticket. Please try again later."  
        )  
  
# Run the Slack app  
def run_slack_app():  
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)  
    handler.start()  
  
if __name__ == "__main__":  
    slack_thread = Thread(target=run_slack_app)  
    slack_thread.start()  
    flask_app.run(host='0.0.0.0', port=8080)  