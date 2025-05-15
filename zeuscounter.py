import cv2
import numpy as np
import easyocr
from mss import mss
from collections import defaultdict
import time
import datetime
from difflib import get_close_matches
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import os
from PIL import ImageGrab
import ctypes
from sending import writeRandomLineAndSay, sendEndLeaderboard, sendHalfLeaderboard


from chatgpt import ask_chatgpt

# ==== Configuration ====
PLAYER_NAME = "Cedar Creek Vent Technician"
KNOWN_NAMES = [PLAYER_NAME]

reader = easyocr.Reader(['en'], gpu=False)
zeus_kill_log = defaultdict(int)
last_kills = 0  # Used by GSIHandler
match_kill_log = defaultdict(int)
last_map_phase = ""

KILL_LOG_PATH = "zeus_kills.json"

def load_kill_log():
	if os.path.exists(KILL_LOG_PATH):
		with open(KILL_LOG_PATH, "r") as f:
			return json.load(f)
	return {}

def save_kill_log(data):
	with open(KILL_LOG_PATH, "w") as f:
		json.dump(data, f, indent=4)

# Initialize persistent log
persistent_kill_log = load_kill_log()

# ==== Utility Functions ====

def correct_name(name, confidence):
	name = name.strip()
	if name in KNOWN_NAMES or confidence >= 0.75:
		return name
	matches = get_close_matches(name, KNOWN_NAMES, n=1, cutoff=0.6)
	return matches[0] if matches else name

def preprocess_image(img_color):
	scale = 2
	upscaled = cv2.resize(img_color, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
	return upscaled

def get_victim_name(img_color):
	prepped = preprocess_image(img_color)
	results = reader.readtext(prepped)
	boxed = prepped.copy()

	player_y = None
	player_found = False
	victim_name = None
	best_x = -1
	victim_box = None
	victim_conf = 0.0

	print("EasyOCR detected words:")
	for (bbox, text, conf) in results:
		((x1, y1), (x2, y2), _, _) = bbox
		x, y = int(x1), int(y1)
		w, h = int(x2 - x1), int(y2 - y1)
		text_clean = text.strip()
		if not text_clean:
			continue
		print(f"  '{text_clean}' (conf {conf:.2f}) at ({x}, {y})")
		if text_clean.lower().startswith("cedar") or text_clean.lower().startswith("vent"):
			player_y = y
			player_found = True

	if player_found:
		for (bbox, text, conf) in results:
			((x1, y1), (x2, y2), _, _) = bbox
			x, y = int(x1), int(y1)
			if abs(y - player_y) <= 15 and x > best_x:
				best_x = x
				victim_name = text.strip()
				victim_box = (x, y, int(x2 - x1), int(y2 - y1))
				victim_conf = conf

	if victim_name and victim_box:
		if victim_conf < 0.6:
			timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
			cv2.imwrite(f"lowconf_debug_{timestamp}.png", prepped)
			print(f"[!] Low-confidence victim detected (< 0.6). Image saved.")

		corrected = correct_name(victim_name, victim_conf)
		print(f"OCR Final Victim: '{victim_name}' (conf {victim_conf:.2f}) → Matched: '{corrected}'")
		return corrected
	else:
		print("[!] Player name not found or victim box not detected.")
		return None

# ==== Killfeed Screenshot and OCR ====

ctypes.windll.shcore.SetProcessDpiAwareness(2)

def process_killfeed():
	screen_width = ImageGrab.grab().width
	left = screen_width - 600
	top = 50
	right = screen_width
	bottom = top + 200

	pil_img = ImageGrab.grab(bbox=(left, top, right, bottom))
	frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
	ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	#cv2.imwrite(f"killfeed_{ts}.png", frame)

	victim = get_victim_name(frame)
	if victim:
		zeus_kill_log[victim] += 1
		persistent_kill_log[victim] = persistent_kill_log.get(victim, 0) + 1
		match_kill_log[victim] += 1
		save_kill_log(persistent_kill_log)
		print(f"[Zeus Kill] {victim} → {zeus_kill_log[victim]} (Total: {persistent_kill_log[victim]})")
		writeRandomLineAndSay(victim)  # 👈 ADD THIS LINE
	else:
		print("[?] Zeus kill detected, but victim not recognized.")
		cv2.imwrite(f"killfeed_{ts}.png", frame)

# ==== CS2 GSI HTTP Listener ====

class GSIHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		global last_kills

		content_length = int(self.headers.get('Content-Length', 0))
		post_data = self.rfile.read(content_length)

		try:
			data = json.loads(post_data)
		except json.JSONDecodeError:
			self.send_response(400)
			self.end_headers()
			return

		global last_map_phase, match_kill_log

		# Detect halftime or game end
		map_phase = data.get("map", {}).get("phase", "").lower()

		if map_phase == "intermission" and last_map_phase != "intermission":
			print("[Match] Halftime reached.")
			sendHalfLeaderboard(match_kill_log)

		if map_phase == "gameover" and last_map_phase != "gameover":
			print("[Match] Game over.")
			sendEndLeaderboard(match_kill_log)
			time.sleep(5)
			match_kill_log.clear()

		player = data.get("player", {})
		match_stats = player.get("match_stats", {})
		weapons = player.get("weapons", {})

		kills = int(match_stats.get("kills", 0))

		active_weapon = None
		for weapon_data in weapons.values():
			if weapon_data.get("state") == "active":
				active_weapon = weapon_data.get("name")
				break

		if kills > last_kills and active_weapon == "weapon_taser":
			print(f"⚡ Zeus kill detected! Total kills: {kills}")
			time.sleep(0.5)
			process_killfeed()

		last_kills = kills
		last_map_phase = map_phase

		try:
			self.send_response(200)
			self.end_headers()
		except ConnectionResetError:
			print("[!] Client disconnected before response could be sent.")

# ==== Launch ====

def run_server():
	print("Listening for CS2 GSI on http://localhost:3000")
	server = HTTPServer(('', 3000), GSIHandler)
	server.serve_forever()

if __name__ == '__main__':
	run_server()