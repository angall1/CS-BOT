import time
import pyautogui
import random


EXEC_FILE= r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\zeusSay.cfg"

import random


rage_lines = [
    "{name} just got solo'd by a battery.",
    "Bro {name} got full-sent by 1 click of Zeus justice.",
    "I only needed one shot, {name} — and Zeus delivered.",
    "{name} lost to pure electricity. No bullets required.",
    "Imagine dying to a taser in 2025, {name}.",
    "Zeus-only run and {name} still folded. Embarrassing.",
    "You had rifles, I had lightning. You lost, {name}.",
    "No armor? No problem. {name} still cooked.",
    "Bro {name} got ratio’d by a glorified stun gun.",
    "{name} died for science — Zeus still works.",
    "{name} got sent back to T-spawn via electric mail.",
    "That was personal, {name}. Zeus-only means no mercy.",
    "Who needs aim when you have amperage? RIP {name}.",
    "{name}, ever heard of high-voltage takedowns?",
    "I came, I saw, I zapped {name}.",
    "Zeus in hand, {name} in the dirt.",
    "All I needed was 200 volts and bad decision-making from {name}.",
    "You brought a gun to a spark fight, {name}.",
    "Zeus-only challenge? Completed. Sorry, {name}.",
    "{name} got clapped by the most disrespectful weapon in CS.",
    "Point. Click. Zap. Bye {name}.",
    "You can dodge bullets, but not shame, {name}.",
    "That zap rewrote {name}'s config file.",
    "No crosshair, no recoil, just volts for {name}.",
    "Zeus > {name}’s K/D. Accept it.",
    "That spark was the last thing {name} saw.",
    "I could’ve knifed you, {name}, but I wanted the sound.",
    "{name}, you just fed my Zeus kill montage. Thanks.",
    "Zeus is love. Zeus is life. Not for {name}, though.",
    "{name}, peek again — my battery’s still full."
]

def write_command(command):
    with open(EXEC_FILE, 'w', encoding='utf-8') as f:
        f.write(command)

def press_key():
    time.sleep(0.2)
    pyautogui.press('multiply')

def press_key_noDelay():
    time.sleep(1)
    pyautogui.press('multiply')


def getRandomLine(name) -> str:
    line = random.choice(rage_lines).format(name=name)
    return line  # Optional, if you want to reuse the output

def writeRandomLineAndSay(name):
    write_command("say " +  getRandomLine(name))
    press_key()


import json

def generate_leaderboard(leaderboard_path, current_game_kills, base_total_kills):
    # Load the all-time leaderboard from the JSON file
    with open(leaderboard_path, 'r', encoding='utf-8') as f:
        leaderboard_dict = json.load(f)

    # Filter for only players in the current game
    filtered = {
        name: leaderboard_dict[name]
        for name in current_game_kills
        if name in leaderboard_dict
    }

    # Sort by kill count (descending) and take top 3
    top_3 = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:3]

    # Sum all kills in JSON + base_total_kills
    total_kills = sum(leaderboard_dict.values()) + base_total_kills

    # Build the output as a list of strings
    lines = ["-- LEADERBOARD --"]
    for name, count in top_3:
        lines.append(f"{name}: {count}")
    lines.append(f"Total kills: {total_kills}")

    return lines

def sendLeaderboard(current_game_kills):
    if not len(current_game_kills) == 0:
        hardcoded_base_kills = 294  # Your base number
        lines_to_print = generate_leaderboard("zeus_kills.json", current_game_kills, hardcoded_base_kills)
        for line in lines_to_print:
            write_command("say " + str(line))
            press_key_noDelay()


