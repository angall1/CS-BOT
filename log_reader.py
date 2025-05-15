import os
import re
import keyboard
import time
from chatgpt import ask_chatgpt
from sending import sendMessage

# Path to your console.log
CONSOLE_LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\console.log"

# regex to match chat lines
CHAT_RE = re.compile(r'\[(ALL|T|CT)\]\s*(.+)')

# zero-width LTR/RTL marks CS injects
ZW_CHARS = ("\u200e", "\u200f")

def sanitize(s):
	for z in ZW_CHARS:
		s = s.replace(z, "")
	return s

def get_last_chat_line(path):
	if not os.path.isfile(path):
		raise FileNotFoundError(f"No such file: {path!r}")
	last = None
	with open(path, encoding="utf-8", errors="ignore") as f:
		for raw in f:
			line = sanitize(raw).strip()
			if CHAT_RE.search(line):
				last = line
	return last

def parse_chat(chat_line):
	"""
	Returns (name, message) from a chat line like:
	  [ALL] Name: msg
	  [CT] Name﹫Loc: msg
	"""
	m = CHAT_RE.search(chat_line)
	if not m:
		return "", ""
	full = m.group(2).strip()
	name_part, msg = full.split(":", 1)
	name = re.split(r"[@﹫]", name_part, 1)[0].strip()
	return name, msg.strip()

def on_hotkey():
	try:
		chat = get_last_chat_line(CONSOLE_LOG)
		if not chat:
			print("<< no chat messages found >>")
		else:
			name, message = parse_chat(chat)
			sendMessage(ask_chatgpt(name + " : " + message))
			print([name, message])
	except Exception as e:
		print(f"Error: {e}")


if __name__ == "__main__":
	print("Listening for F5 or Shift+F5… ")
	# bind F5 and Shift+F5
	#keyboard.add_hotkey("F5", on_hotkey)
	keyboard.add_hotkey("shift+F5", on_hotkey)
	
	# exit on Esc
	keyboard.wait("shift+F6")
