import time
import pyautogui
import random
import os

EXEC_FILE= r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\zeusSay.cfg"

import random

from dotenv import load_dotenv

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")


rage_lines = [
    "Haha {name}, you just got fried by the world’s weakest gun. Pathetic.",
    "Look at you, {name}, vaporized by a glorified taser. What a joke.",
    "One zap erased {name} from existence. Garbage play.",
    "Even my grandma’s Prius battery would Zeus you better, {name}.",
    "{name}, you got insta-fried like burnt toast. Embarrassing.",
    "Clown move: {name} got solo’d by 200 volts of pure shame.",
    "Did you think your AK could outgun electricity, {name}? Nope.",
    "Zap! {name} hit the dirt faster than your mom’s baking.",
    "{name}, you just got served electric justice. No mercy.",
    "No bullets needed—just a spark and {name} is toast.",
    "{name}, the Zeus drank you for breakfast. Downsized to zero.",
    "Say goodbye to {name}’s ego—one spark humiliated you.",
    "Who needs aim with 220 volts? Bye-bye {name}.",
    "Charge complete, {name} out cold. Should’ve stayed comfy.",
    "Electric smackdown had {name} begging for mercy. LOL.",
    "My stun gun vs. your life, {name}. Guess who won?",
    "Short-circuited {name} before they could blink. Ouch.",
    "Battery’s still full; {name} already dead. Too easy.",
    "No armor saved you, {name}. You got flash-fried.",
    "{name}, you got vaporized harder than your browser tabs.",
    "Need a charger, {name}? Because you’re out of juice now.",
    "That zap rewrote your death certificate, {name}. R.I.P.",
    "Electric rage mode: {name} was liquidated. Boo-hoo.",
    "One click, {name} was history. Simplicity at its finest.",
    "Clapped by a stun gun? Welcome to reality, {name}.",
    "{name}, you just got #ZeusClapped. Embrace the shame.",
    "Run and hide? Zeus laughs at {name}’s feeble attempts.",
    "Battery’s got more game than you, {name}. Get wrecked.",
    "Point. Click. Zap. {name} vaporized. GG.",
    "{name}, you just fed my Zeus kill compilation. Tyvm.",
    "Electric hum took you down, {name}. Next time pay attention.",
    "Zap so hard it broke your self-esteem, {name}.",
    "Your K/D ratio just got reset by a spark, {name}.",
    "I’m the electric boogaloo and {name} is the punchline.",
    "Your gun’s on cooldown, {name}; my volts never sleep.",
    "Shock therapy courtesy of me; {name} owes me a thank you.",
    "That electro-blast was the highlight of my day, {name}.",
    "Gravity met electricity and {name} met the floor.",
    "My lightning finger targeted you, {name}, and you dropped.",
    "I delivered the wattage, {name}, you delivered the corpse.",
    "Short on bullets. Long on volts. {name} paid the price.",
    "That zap was patented rage, {name}. Too hot to handle.",
    "Your final heartbeat was synced to my electrical beat, {name}.",
    "Battery’s still charged. {name} isn’t.",
    "You hit the ground faster than my charging cycle, {name}.",
    "That spark line was the punchline, {name}, you’re the joke.",
    "Electric arrow struck true. {name} wishes they dodged.",
    "Your respawn timer starts now, {name}. Hope you learned.",
    "Zeus: built-in headshot. Sorry {name}, no refund.",
    "No recoil, no problem. {name} still folded.",
    "You just got electrified and meme’d, {name}.",
    "The sound of electricity ≫ the sound of your cries, {name}.",
    "One click, one demise. {name}, you were lightning food.",
    "Voltage drop: {name}’s health bar to zero.",
    "Electric slip ’n slide landed {name} on their face.",
    "I stunned you so good, {name}, even Zeus is proud.",
    "My kill feed reads Zeus → {name}. Period.",
    "You brought a toolkit to a voltage fight, {name}.",
    "That high-voltage handshake ended {name}’s career.",
    "Zap, borrow, die. {name} just got loaned a ticket to spawn."
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


def sendMessage(content):
    #print(content)
    write_command("say " + content)
    press_key()

import json

def generate_halftime_leaderboard(current_game_kills: dict, base_total_kills):
    # Load the all-time leaderboard from the JSON file
    leaderboard_path = "zeus_kills.json"
    with open(leaderboard_path, 'r', encoding='utf-8') as f:
        leaderboard_dict = json.load(f)

    # Filter for only players in the current game
    filtered = {
        name: current_game_kills[name]
        for name in current_game_kills
        if name in current_game_kills.keys()
    }

    # Sort by kill count (descending) and take top 3
    top_3 = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:3]

    # Sum all kills in JSON + base_total_kills
    total_kills = sum(leaderboard_dict.values()) + base_total_kills

    # Build the output as a list of strings
    lines = ["⚡💀 ZEUS LEADERBOARD 💀⚡"]
    for name, count in top_3:
        lines.append(f"{name}: {count}")
    lines.append(f"Total kills: {total_kills}")

    return lines


def generate_end_leaderboard(current_game_kills: dict, base_total_kills):
    # (The base_total_kills argument isn’t used in this snippet—
    #  you can remove it if it’s not needed.)

    # Sort by kill count (descending) and take only the top player
    top = sorted(current_game_kills.items(),
                 key=lambda x: x[1],
                 reverse=True)[:1]

    if not top:
        return ["⚡💀 MOST ZEUSED PLAYER 💀⚡", "No kills this game"]

    # Unpack the single tuple into name and kills
    topname, topkills = top[0]

    # Build the output
    lines = ["⚡💀 MOST ZEUSED PLAYER 💀⚡"]
    lines.append(f"{topname}: {topkills}")

    return lines



def sendHalfLeaderboard(current_game_kills):
    if not len(current_game_kills) == 0:
        hardcoded_base_kills = 294  # Your base number
        lines_to_print = generate_halftime_leaderboard( current_game_kills, hardcoded_base_kills)
        for line in lines_to_print:
            write_command("say " + str(line))
            press_key_noDelay()


def sendEndLeaderboard(current_game_kills):
    if not len(current_game_kills) == 0:
        hardcoded_base_kills = 294  # Your base number
        lines_to_print = generate_end_leaderboard( current_game_kills, hardcoded_base_kills)
        for line in lines_to_print:
            write_command("say " + str(line))
            press_key_noDelay()

