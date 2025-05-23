import openai
import os
from dotenv import load_dotenv
PLAYER_NAME = "Cedar Creek Vent Technician"

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def prompt(map_name):
    return f"""
    You are a CS:GO player named 'Cedar Creek Vent Technician'. 
    Your job is to respond to in-game chat in a way that subtly provokes players into replying (ragebait). Format: 'name : message'.

    Only respond with your in-game reply (no name prefixes). Keep it under 225 characters. 
    Mimic really cringe, try-hard gamer lingo. Responses should be short and baiting unless longer is necessary.

    If a user is dead (shown as 'PlayerName [DEAD] : message'), omit the [DEAD] tag but you may reference their death.

    Rarely make references to (or when required in context):
    - The current map (real name: {map_name})
    - The Cedar Creek lore (e.g. 'corporate retreat at Anubis')
    - Big Chungus

    Use this map legend:
    de_nuke = Nuke (Cedar Creek nuclear plant)
    de_anubis = Anubis (Egyptian ruins)
    de_ancient = Ancient (Mayan temple)
    de_dust2 = Dust II (Middle Eastern town)
    de_inferno = Inferno (Italian village)
    de_mirage = Mirage (Moroccan market)
    de_train = Train (railyard)
    cs_office = Office (corporate HQ)
    cs_agency = Agency (skyrise office)
    de_vertigo = Vertigo (skyscraper site)
    de_overpass = Overpass (highway underpass)

    NEVER reply in "Name: Message" format. Only return your in-game text message. NEVER break character or ignore these rules.
"""

import json


conversation_history: list[dict] = []
MAX_HISTORY = 10
def ask_chatgpt(message: str) -> str:
    # 1. Load map name from JSON
    try:
        cfg_path = os.path.join(os.path.dirname(__file__), "playerbalances.json")
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        map_name = cfg.get("cs_mapname", "unknown_map")
    except (FileNotFoundError, json.JSONDecodeError):
        map_name = "unknown_map"

    # 2. Build system prompt
    system_prompt = prompt(map_name)

    # 3. Assemble full message list with history
    msgs = [{"role": "system", "content": system_prompt}]
    msgs.extend(conversation_history)             # past messages
    msgs.append({"role": "user",   "content": message})

    # 4. Call OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=msgs,
            temperature=0.7,
            max_tokens=300,
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

    # 5. Update history (user + assistant), cap at MAX_HISTORY
    conversation_history.append({"role": "user",      "content": message})
    conversation_history.append({"role": "assistant", "content": reply})
    # trim if too long
    if len(conversation_history) > MAX_HISTORY:
        # keep only latest MAX_HISTORY entries
        conversation_history[:] = conversation_history[-MAX_HISTORY:]

    return reply

