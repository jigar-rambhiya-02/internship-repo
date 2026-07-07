# Task 5: Mini Dungeon Game (state machine + persistent stats)

## Goal
Build a small text-based game where a player fights random monsters in rounds, state (health, gold, level) changes over time, and progress is saved between sessions. This is the hardest task — it combines classes, inheritance, randomness, game-loop logic, and persistence.

## Files to create
- player.py
- monster.py
- game_engine.py
- storage.py
- main.py

---

## player.py

```python
class Player:
    def __init__(self, name, health=100, gold=0, level=1, xp=0):
        # store all values
        pass

    def is_alive(self):
        # return True if health > 0
        pass

    def take_damage(self, amount):
        # subtract amount from health, don't let it go below 0
        pass

    def heal(self, amount):
        # add amount to health, don't let it go above 100
        pass

    def gain_xp(self, amount):
        # add xp
        # if xp >= 100: level up! reset xp to 0 (or xp - 100), increase level by 1,
        #   print a level up message, and fully heal the player
        pass

    def to_dict(self):
        pass

    def __str__(self):
        # format: "Hero | Lvl 1 | HP: 100 | Gold: 0 | XP: 0"
        pass
```

---

## monster.py

```python
import random

class Monster:
    def __init__(self, name, health, attack_power, gold_reward, xp_reward):
        pass

    def is_alive(self):
        pass

    def take_damage(self, amount):
        pass

    def attack(self):
        # return a random damage amount between attack_power-2 and attack_power+2
        # (use random.randint) — minimum should never go below 1
        pass

    def __str__(self):
        pass


def generate_random_monster():
    # pick randomly from a small hardcoded list of monster templates, e.g.:
    # ("Goblin", 20, 5, 10, 20), ("Wolf", 15, 4, 5, 15), ("Orc", 35, 8, 20, 40)
    # use random.choice() on the list of tuples, then create and return a Monster object
    pass
```

---

## game_engine.py

```python
def battle(player, monster):
    # loop while both player.is_alive() and monster.is_alive():
    #   print current HP of both
    #   ask player: "1. Attack  2. Flee"
    #   if attack: deal a random amount of damage to monster (random.randint(5, 15)),
    #              print result, then if monster still alive, monster attacks back
    #   if flee: print "You fled the battle!" and return without rewards
    #
    # after the loop:
    #   if player died: print "You have been defeated..." 
    #   if monster died: print victory message, call player.gain_xp(monster.xp_reward),
    #                     add monster.gold_reward to player.gold
    pass
```

Note: you'll need `import random` in game_engine.py too, and probably `from monster import generate_random_monster` in main.py.

---

## storage.py

```python
import json
from player import Player

def save_player(player):
    # save player.to_dict() to save_game.json
    pass

def load_player():
    # try loading save_game.json, rebuild a Player object from it
    # catch FileNotFoundError -> return None (main.py will create a new player if None)
    pass
```

---

## main.py

```python
from player import Player
from monster import generate_random_monster
from game_engine import battle
from storage import save_player, load_player

def main():
    player = load_player()
    if player is None:
        name = input("Enter your hero's name: ")
        player = Player(name)

    while True:
        print(f"\n{player}")
        print("1. Explore (find a monster)")
        print("2. View Stats")
        print("3. Rest (heal 20 HP)")
        print("4. Save & Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            if not player.is_alive():
                print("You are defeated and cannot explore. Rest first!")
                continue
            monster = generate_random_monster()
            print(f"A wild {monster.name} appears!")
            battle(player, monster)
        elif choice == "2":
            print(player)
        elif choice == "3":
            player.heal(20)
            print("You rest and recover some health.")
        elif choice == "4":
            save_player(player)
            print("Game saved. Goodbye, adventurer!")
            break

if __name__ == "__main__":
    main()
```

---

## SAMPLE RUN (this one involves randomness, so exact numbers will differ — match the STRUCTURE and LOGIC, not exact numbers)

**Input sequence (first run, no save file):**
```
Enter your hero's name: Rin

Choose an option: 1
[A monster appears, e.g. Goblin]
[Battle loop happens - choose "1" a few times to attack until one side dies]

Choose an option: 2
Choose an option: 3
Choose an option: 4
```

**Expected structure of output for option 1 (Explore) — example with a Goblin:**
```
A wild Goblin appears!
Player HP: 100 | Goblin HP: 20
1. Attack  2. Flee
Choose: 1
You dealt 11 damage to Goblin!
Goblin HP: 9
Goblin attacks you for 4 damage!
Player HP: 96 | Goblin HP: 9
1. Attack  2. Flee
Choose: 1
You dealt 13 damage to Goblin!
You defeated the Goblin!
You gained 20 XP and 10 gold!
```

**Expected output for option 2 (View Stats) after that fight:**
```
Rin | Lvl 1 | HP: 96 | Gold: 10 | XP: 20
```
(exact HP/gold/xp numbers will vary because damage is randomized — check that gold increased by the monster's gold_reward, and xp by its xp_reward, and HP decreased by whatever damage you took)

**Expected output for option 3 (Rest):**
```
You rest and recover some health.
```
And HP should increase by 20 (capped at 100) — e.g. if HP was 96, it stays at 100 (capped), not 116.

**Expected contents of save_game.json after option 4:**
```json
{"name": "Rin", "health": 100, "gold": 10, "level": 1, "xp": 20}
```

**Second run:** running `python main.py` again should skip the "Enter your hero's name" prompt and go straight to the menu, loading Rin with gold=10, xp=20 already — proving persistence works.

**Level-up check:** keep fighting until xp reaches 100+. You should see a level-up message, level become 2, xp reset, and HP fully restored to 100.

## New concept notes
- `random.randint(a, b)` gives you a random integer between a and b (inclusive) — core to any game with variability.
- A "game loop" (`while player.is_alive() and monster.is_alive()`) is the same pattern used in real games, just text-based here.
- Capping values (health can't go below 0 or above 100) is a very common real-world validation pattern — use `max()` and `min()`:
  - `self.health = max(0, self.health - amount)` for damage
  - `self.health = min(100, self.health + amount)` for healing

## Bonus (optional)
- Add an inventory system where defeating monsters sometimes drops a "Health Potion" item the player can use during battle.
- Add a "Boss" monster (subclass of Monster with 2x stats) that appears after level 3.