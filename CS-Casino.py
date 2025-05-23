import random
import time
import threading
import json
import os
import re
from sending import sendMessage


CONSOLE_LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\console.log"
CHAT_RE = re.compile(r'\[(ALL|T|CT)\]\s*(.+)')
ZW_CHARS = ("\u200e", "\u200f")

# External JSON path for player balances
BALANCE_FILE = "player_balances.json"
STARTING_BALANCE = 100

# === Game State ===
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = []
player_hands = {}
dealer_hands = {}
player_bets = {}
game_active = {}
current_player = None
last_action_time = {}
timeout_seconds = 20

# === Balance functions ===
def load_balances():
	if os.path.exists(BALANCE_FILE):
		with open(BALANCE_FILE, "r") as f:
			return json.load(f)
	else:
		return {}

def save_balances(data):
	with open(BALANCE_FILE, "w") as f:
		json.dump(data, f, indent=4)

balances = load_balances()

def draw_card():
	global deck
	if not deck:
		deck = ranks * 4
		random.shuffle(deck)
	return deck.pop()

def hand_value(hand):
	total, aces = 0, 0
	for card in hand:
		if card in ['J', 'Q', 'K']:
			total += 10
		elif card == 'A':
			total += 11
			aces += 1
		else:
			total += int(card)
	while total > 21 and aces:
		total -= 10
		aces -= 1
	return total
def display_hands(name, show_dealer=False):
	player_cards = "  ".join(f"| {card} |" for card in player_hands[name])
	if show_dealer:
		dealer_cards = "  ".join(f"| {card} |" for card in dealer_hands[name])
	else:
		dealer_cards = f"| {dealer_hands[name][0]} |  | ? |"
	sendMessage(f"{name}'s hand: {player_cards}  ({hand_value(player_hands[name])})  Dealer: {dealer_cards}")


def reset_game(name):
	player_hands[name] = [draw_card(), draw_card()]
	dealer_hands[name] = [draw_card(), draw_card()]
	game_active[name] = True
	last_action_time[name] = time.time()
	display_hands(name)


def timeout_check():
	while True:
		for name in list(game_active):
			if game_active.get(name) and (time.time() - last_action_time.get(name, 0) > timeout_seconds):
				sendMessage(f"{name}'s game timed out due to inactivity.")
				game_active[name] = False
		time.sleep(1)

def handle_command(name: str, cmd: str):
	# ignore dead players
	if name.endswith("[DEAD]"):
		return

	cmd = cmd.strip()
	raw_cmd = cmd
	cmd_l = cmd.lower()
	last_action_time[name] = time.time()

	# only treat slash‐commands
	if not cmd.startswith("/"):
		return

	# keep your balances data-structure up to date
	if name not in balances:
		balances[name] = STARTING_BALANCE

	# BALANCE
	if cmd.startswith("/balance"):
		sendMessage(f"{name}, you have ${balances[name]}")

	# GIVE
	elif cmd_l.startswith("/give"):
		parts = raw_cmd.split()
		if len(parts) != 3:
			sendMessage("Usage: /give PLAYER AMOUNT")
			return

		recipient_raw, amount_str = parts[1], parts[2]
		# find the “real” key in balances (case-insensitive match),
		# default to recipient_raw if not found
		recipient = next(
			(u for u in balances if u.lower() == recipient_raw.lower()),
			recipient_raw
		)

		try:
			amount = int(amount_str)
			if amount <= 0 or amount > balances[name]:
				sendMessage("Invalid transfer amount or insufficient funds.")
				return

			# perform the transfer on the correctly-cased key
			balances[name] -= amount
			balances[recipient] = balances.get(recipient, STARTING_BALANCE) + amount
			save_balances(balances)
			sendMessage(f"{name} gave ${amount} to {recipient}.")
		except ValueError:
			sendMessage("Invalid amount.")

	# BET
	elif cmd.startswith("/bet"):
		try:
			amount = int(cmd.split()[1])
			if amount > balances[name]:
				sendMessage(f"{name}, you don't have enough money to bet ${amount}.")
			else:
				balances[name] -= amount
				player_bets[name] = amount
				save_balances(balances)
				reset_game(name)
		except (IndexError, ValueError):
			sendMessage("Usage: /bet [amount]")

	# HIT
	elif cmd == "/hit":
		if not game_active.get(name):
			sendMessage(f"{name}, You don’t have an active game. Use /bet to start one.")
			return

		player_hands[name].append(draw_card())
		last_action_time[name] = time.time()
		display_hands(name)

		if hand_value(player_hands[name]) > 21:
			sendMessage(f"{name} busted. Dealer wins.")
			game_active[name] = False

	# STAND
	elif cmd == "/stand":
		if not game_active.get(name):
			sendMessage("You don’t have an active game. Use /bet to start one.")
			return

		while hand_value(dealer_hands[name]) < 17:
			dealer_hands[name].append(draw_card())

		last_action_time[name] = time.time()
		display_hands(name, show_dealer=True)

		p = hand_value(player_hands[name])
		d = hand_value(dealer_hands[name])

		if d > 21 or p > d:
			sendMessage(f"{name} wins and earns ${player_bets[name]*2}!")
			balances[name] += player_bets[name] * 2
		elif p < d:
			sendMessage(f"Dealer wins against {name}.")
		else:
			sendMessage(f"{name} tied with dealer. Bet refunded.")
			balances[name] += player_bets[name]

		save_balances(balances)
		game_active[name] = False

	# UNKNOWN
	else:
		sendMessage("Unknown command. Use /bet, /hit, /stand, /balance, or /give.")


# === Start timeout checker ===
threading.Thread(target=timeout_check, daemon=True).start()

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
		return "", ""
	full = m.group(2).strip()
	name_part, msg = full.split(":", 1)
	name = re.split(r"[@﹫]", name_part, 1)[0].strip()
	return name, msg.strip()


def chat_listener():
	last_seen = ""
	while True:
		line = get_last_chat_line(CONSOLE_LOG)
		if line and line != last_seen:
			last_seen = line
			name, message = parse_chat(line)
			# ignore dead players
			if name.endswith("[DEAD]"):
				continue
			# only handle real commands
			if message.lstrip().startswith("/"):
				handle_command(name, message)
		time.sleep(1)



if __name__ == "__main__":
	#sendMessage("CS Casino listener running. Watching for chat commands...`")
	threading.Thread(target=chat_listener, daemon=True).start()
	while True:
		time.sleep(10)

