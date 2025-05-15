import random
import re

# === Card setup ===
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = []

player_hand = []
dealer_hand = []
player_bet = 0
game_active = False

def draw_card():
	global deck
	if not deck:
		deck = [r for r in ranks] * 4
		random.shuffle(deck)
	return deck.pop()

def hand_value(hand):
	val, aces = 0, 0
	for card in hand:
		if card in ['J', 'Q', 'K']:
			val += 10
		elif card == 'A':
			aces += 1
			val += 11
		else:
			val += int(card)
	while val > 21 and aces:
		val -= 10
		aces -= 1
	return val

def display_hands(show_dealer=False):
	player = " | ".join(player_hand)
	dealer = dealer_hand[0] + " | " + (" | ".join(dealer_hand[1:]) if show_dealer else " ")
	print(f"\nYour hand : | {player} |  → ({hand_value(player_hand)})")
	print(f"Dealer hand : | {dealer} |\n")

def reset_game():
	global player_hand, dealer_hand, player_bet, game_active
	player_hand = [draw_card(), draw_card()]
	dealer_hand = [draw_card(), draw_card()]
	game_active = True
	display_hands()

def handle_command(cmd: str):
	global game_active, player_bet

	if cmd.startswith("/bet"):
		match = re.match(r"/bet\s+(\d+)", cmd)
		if match:
			player_bet = int(match.group(1))
			reset_game()
		else:
			print("Usage: /bet [amount]")

	elif cmd == "/hit":
		if not game_active:
			print("No game active. Use /bet to start.")
			return
		player_hand.append(draw_card())
		display_hands()
		val = hand_value(player_hand)
		if val > 21:
			print("💥 You bust! Dealer wins.\n")
			game_active = False

	elif cmd == "/stand":
		if not game_active:
			print("No game active. Use /bet to start.")
			return
		while hand_value(dealer_hand) < 17:
			dealer_hand.append(draw_card())
		display_hands(show_dealer=True)

		p_val = hand_value(player_hand)
		d_val = hand_value(dealer_hand)

		if d_val > 21:
			print("🏆 Dealer busts! You win.")
		elif p_val > d_val:
			print("🏆 You win!")
		elif p_val < d_val:
			print("💀 Dealer wins.")
		else:
			print("🤝 Push (tie).")
		game_active = False

	else:
		print("Unknown command. Use /bet, /hit, or /stand.")

# === Demo loop ===
if __name__ == "__main__":
	print("Blackjack started. Use /bet 100 to begin.")
	while True:
		cmd = input("> ").strip()
		handle_command(cmd)
