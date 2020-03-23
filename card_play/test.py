from GameObject import GameObject
from GameActor import GameActor
from GameAction import GameAction
from GameContext import GameContext
from Weapon import Weapon
from Skills import Skills
from random import randint


if __name__ == "__main__":
    # SETUP
    # create a context
    village = GameContext("Snaefelness", "village on north side of island")
    local = GameContext("town square", "center of village", village)

    # create a single NPC with some attributes and armor
    guard = GameActor("Guard", "test target")
    guard.set_context(local)
    guard.set("life", 16)
    guard.set("evasion", 50)
    guard.set("dexterity", 15)
    guard.set("wisdom", 10)
    guard.set("evasion.slash", 20)  # harder to dodge
    guard.set("protection", 2)
    guard.set("protection.pierce", 4)  # chainmail
    local.add_npc(guard)

    # create a single PC with some skills and attributes
    actor = GameActor("Hero", "initiator")
    actor.set("perception", 25)     # attribute for searching
    actor.set("CHEAT", 25)          # specific skill ability
    actor.set("PUSH", 40)           # sepeciic skill ability
    actor.set_context(local)
    skills = Skills(actor.name)
    skills.set("actions", "SEARCH,PUSH,CHEAT,UNKNOWN-ACTION")
    local.add_member(actor)

    # create obvious and hidden objects in the local context
    bench = GameObject("bench", "obvious object")
    local.add_object(bench)
    trap_door = GameObject("trap-door", "hidden object")
    trap_door.set("concealment", 50)
    local.add_object(trap_door)

    # SEE WHAT WE CAN LEARN FROM THE LOCAL CONTEXT
    print("{} ... {}".format(local.name, local.description))
    party = local.get_party()
    print("    party:")
    for person in party:
        print("\t{} ... {}".format(person.name, person.description))

    npcs = local.get_npcs()
    print("\n    NPCs:")
    for person in npcs:
        print("\t{} ... {}".format(person.name, person.description))

    stuff = local.get_objects()
    print("\n    objects:")
    for thing in stuff:
        print("\t{} ... {}".format(thing.name, thing.description))
    print()

    # DO A SEARCH AND SEE IF WE CAN FIND ANYTHING ELSE
    actions = skills.possible_actions(actor, local)
    for action in actions:
        if action.verb == "SEARCH":
            result = actor.take_action(action, local)
            print("{} searches(skill={}) {}\n    {}"
                  .format(actor.name,
                          action.get("skill"),
                          local.name, result))

    # now see what we can see
    stuff = local.get_objects()
    print("\n    objects:")
    for thing in stuff:
        print("\t{} ... {}".format(thing.name, thing.description))
    print()

    # EXERCISE OUR OTHER NON-COMBAT SKILLS
    for action in actions:
        if action.verb != "SEARCH":
            result = actor.take_action(action, guard)
            print("{} tries to {}(skill={}) {}\n    {}"
                  .format(actor.name, action.verb,
                          action.get("skill"),
                          guard.name, result))
            print()

    # CREATE A WEAPON AND USE IT TO ATTACK THE GUARD
    weapon = Weapon("sword", damage="D6")
    weapon.set("actions", "ATTACK.slash,ATTACK.chop,ATTACK.pierce")
    weapon.set("damage.slash", "D6")
    weapon.set("damage.chop", "D4")
    weapon.set("damage.pierce", "4")
    weapon.set("hit_bonus", 10)
    weapon.set("damage_bonus", 2)

    target = npcs[0]
    actions = weapon.possible_actions(actor, local)
    while target.get("life") >= 1:
        # choose a random attack
        attack = actions[randint(0, len(actions)-1)]
        result = actor.take_action(attack, target)
        print("{} uses {} to {} {}, delivered={}+{}\n    {}"
              .format(actor.name, weapon.name, attack.verb, target.name,
                      attack.get("damage"), attack.get("special_damage"),
                      result))
        print()
