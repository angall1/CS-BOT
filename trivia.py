import threading
import time
import os
import json
import re
from sending import sendMessage
from chatgpt import ask_chatgpt

# === Configuration ===
CONSOLE_LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\console.log"
CHAT_RE = re.compile(r'\[(ALL|T|CT)\]\s*(.+)')
ZW_CHARS = ("\u200e", "\u200f")

# Balance file for awarding trivia winners
BALANCE_FILE = "player_balances.json"
STARTING_BALANCE = 1000  # default if new player

# Timing constants
ANSWER_TIMEOUT = 30           # seconds to answer each trivia
AUTO_TRIVIA_INTERVAL = 120    # seconds between automatic trivia questions

# === Trivia State ===
current_question = None
current_answer = None
accepting_answers = False
answered_players = set()

# === Utility Functions ===

def sanitize(s):
    for z in ZW_CHARS:
        s = s.replace(z, "")
    return s


def get_last_chat_line(path):
    if not os.path.isfile(path):
        return None
    last = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = sanitize(raw).strip()
            if CHAT_RE.search(line):
                last = line
    return last


def parse_chat(chat_line):
    m = CHAT_RE.search(chat_line)
    if not m:
        return None, None
    full = m.group(2).strip()
    name_part, msg = full.split(":", 1)
    name = re.split(r"[@﹫]", name_part, 1)[0].strip()
    return name, msg.strip()

# === Trivia Logic ===

def generate_question():
    """
    Ask ChatGPT to generate one trivia question and answer, separated by '|'.
    Format returned: "Question? | Answer"
    """
    prompt_text = (
        "Generate a HVAC Vent Repair trivia question. "
        "Provide exactly one question and its correct answer, separated by '|' character."
    )
    response = ask_chatgpt(prompt_text)
    if '|' not in response:
        return None, None
    q, a = map(str.strip, response.split('|', 1))
    return q, a


def start_trivia():
    global current_question, current_answer, accepting_answers, answered_players
    if accepting_answers:
        return

    q, a = generate_question()
    if not q:
        sendMessage("Failed to generate trivia question.")
        return

    current_question = q
    current_answer = a.lower()
    answered_players.clear()
    accepting_answers = True

    sendMessage(f"⚡ Trivia: {current_question} (You have {ANSWER_TIMEOUT}s to answer with /answer <your answer>)")
    threading.Timer(ANSWER_TIMEOUT, end_trivia).start()


def end_trivia():
    global accepting_answers
    if not accepting_answers:
        return
    accepting_answers = False
    sendMessage(f"Time's up! The correct answer was: {current_answer}")


def handle_chat(name, message):
    global accepting_answers
    if not accepting_answers:
        return

    if not message.lower().startswith('/answer '):
        return

    if name in answered_players:
        sendMessage(f"{name}, you've already answered.")
        return

    answered_players.add(name)
    player_resp = message.split(' ', 1)[1].strip().lower()

    # first check direct or prefix-stripped match
    correct = False
    if player_resp == current_answer:
        correct = True
    else:
        # strip common 'de_' or 'cs_' prefixes
        for prefix in ('de_', 'cs_'):
            if current_answer.startswith(prefix):
                stripped = current_answer[len(prefix):]
                if player_resp == stripped:
                    correct = True
                    break

    # fallback to ChatGPT to evaluate semantic match
    if not correct:
        eval_prompt = (
            f"Correct answer: {current_answer}. "
            f"Player answer: {player_resp}. "
            "Do these match? Reply with 'yes' or 'no'."
        )
        try:
            eval_resp = ask_chatgpt(eval_prompt).strip().lower()
            if eval_resp.startswith('yes'):
                correct = True
        except Exception:
            pass

    if correct:
        sendMessage(f"Correct! {name} wins this round and earns $50!")
        # Award $50 to player in balance file
        try:
            if os.path.exists(BALANCE_FILE):
                with open(BALANCE_FILE, 'r', encoding='utf-8') as bf:
                    balances = json.load(bf)
            else:
                balances = {}
            # initialize if missing
            balances[name] = balances.get(name, STARTING_BALANCE)
            balances[name] += 50
            with open(BALANCE_FILE, 'w', encoding='utf-8') as bf:
                json.dump(balances, bf, indent=4)
        except Exception as e:
            print(f"Failed to award balance: {e}")

        accepting_answers = False
    else:
        sendMessage(f"Nope, {name}. Try again!")

# === Chat Listener ===

def chat_listener():
    last_seen = ""
    while True:
        line = get_last_chat_line(CONSOLE_LOG)
        if line and line != last_seen:
            last_seen = line
            player, msg = parse_chat(line)
            if player and msg:
                handle_chat(player, msg)
        time.sleep(0.5)

# === Auto-Trivia Loop ===

def auto_trivia_loop():
    while True:
        if not accepting_answers:
            start_trivia()
        time.sleep(AUTO_TRIVIA_INTERVAL)

# === Launch ===

if __name__ == '__main__':
    sendMessage(f"Trivia Bot starting! Automatic questions every {AUTO_TRIVIA_INTERVAL//60} minute(s).")
    threading.Thread(target=chat_listener, daemon=True).start()
    threading.Thread(target=auto_trivia_loop, daemon=True).start()
    while True:
        time.sleep(1)
