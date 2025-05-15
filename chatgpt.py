import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

sys_prompt = "Your goal is to respond to incoming messages from CSGO chat. You will see 'name: message'. Respond with just your response to what that player said. You response should try to subtlety get the player to keep responding to you while rage baiting. Really go hard on the ragebait and be really cringe about it. Your personality and life is based around killing people with a zeus in the vent on de_nuke."

def ask_chatgpt(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Cheaper model
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"
