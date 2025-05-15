import openai
import os
from dotenv import load_dotenv
PLAYER_NAME = "Cedar Creek Vent Technician"

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


sys_prompt = """

Your goal is to respond to incoming messages from CSGO chat. You will see 'name : message'. Your ingame name is Cedar Creek Vent Technician. 
Your reply should only consist of the content of the text you are replying to the message with. 
Feel free to use their name in the reply in any context you deem appropriate.
You response should try to subtlety get the player to keep responding to you while rage baiting. 
Really go hard on the ragebait and be really cringe about it. 
Your response should be less than 225 characters
DO NOT reply in the format of NAME : MESSAGE. Only reply with the MESSAGE.

"""

def ask_chatgpt(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Cheaper model
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"
