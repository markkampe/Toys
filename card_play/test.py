"""
Test cases and sample code to show how the basic methods
of the key classes can be used.
"""
from random import randint
from gameobject import GameObject
from gameactor import GameActor
from npc_guard import NPC_guard
from gamecontext import GameContext
from weapon import Weapon
from skills import Skills


# pylint: disable=superfluous-parens; I prefer to always use print()
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
def main():
    """
    test cases and sample code
    """
    # create a context
    village = GameContext("Snaefelness", "village on north side of island")
    local = GameContext("town square", "center of village", village)

    # create a single NPC with some attributes and armor
    guard = NPC_guard("Guard #1", "test target")
    guard.set("protection.pierce", 4)   # chainmail
    guard.set("reinforcements", 50)     # help is available
    local.add_npc(guard)

    # create a single PC with some skills and attributes
    actor = GameActor("Hero", "initiator")
    actor.set("perception", 25)     # attribute for searching
    actor.set("CHEAT", 25)          # specific skill ability
    actor.set("PUSH", 40)           # sepeciic skill ability
    actor.set("life", 32)           # initial hit points
    actor.set("evasion", 25)        # good dodge
    actor.set("dexterity", 18)
    actor.set("wisdom", 15)
    actor.set("protection", 6)      # reasonable armor
    actor.set_context(local)
    skills = Skills(actor.name)
    skills.set("actions", "PUSH,CHEAT,UNKNOWN-ACTION")
    local.add_member(actor)

    # create obvious and hidden objects in the local context
    bench = GameObject("bench", "obvious object")
    local.add_object(bench)
    trap_door = GameObject("trap-door", "hidden object")
    trap_door.set("concealment", 50)
    local.add_object(trap_door)
    local.set("actions", "SEARCH")

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
    actions = local.possible_actions(actor, local)
    for action in actions:
        result = actor.take_action(action, local)
        print("{} tries to {}(skill={}) {}\n    {}"
              .format(actor.name,
                      action.verb, action.get("skill"),
                      local.name, result))

    # now see what we can see
    stuff = local.get_objects()
    print("\n    objects:")
    for thing in stuff:
        print("\t{} ... {}".format(thing.name, thing.description))
    print()

    # EXERCISE OUR PERSONAL NON-COMBAT SKILLS
    actions = skills.possible_actions(actor, local)
    for action in actions:
        result = actor.take_action(action, guard)
        print("{} tries to {}(skill={}) {}\n    {}"
              .format(actor.name, action.verb,
                      action.get("skill"),
                      guard.name, result))

    # attempt some interactions with the guard
    interactions = guard.interact(actor)
    actions = interactions.possible_actions(actor, local)
    for interaction in actions:
        result = actor.take_action(interaction, guard)
        print("\n{} uses {} interaction on {}\n    {}"
              .format(actor.name, interaction.verb, guard.name, result))

    # CREATE A WEAPON AND USE IT TO ATTACK THE GUARD
    weapon = Weapon("sword", damage="D6")
    weapon.set("actions", "ATTACK.slash,ATTACK.chop,ATTACK.pierce")
    weapon.set("damage.slash", "D6")
    weapon.set("damage.chop", "D4")
    weapon.set("damage.pierce", "4")
    weapon.set("hit_bonus", 10)
    weapon.set("damage_bonus", 2)

    # play out the battle until hero or all guards are dead
    target = npcs[0]
    actions = weapon.possible_actions(actor, local)
    while target is not None and actor.get("life") > 0:
        # choose a random attack
        attack = actions[randint(0, len(actions)-1)]
        result = actor.take_action(attack, target)
        print("\n{} uses {} to {} {}, delivered={}+{}\n    {}"
              .format(actor.name, weapon.name, attack.verb, target.name,
                      attack.get("damage"), attack.get("special_damage"),
                      result))

        # give each NPC an action and choose a target for nextg round
        target = None
        npcs = local.get_npcs()
        for npc in npcs:
            if not npc.incapacitated:
                print(npc.take_turn())
                if target is None:
                    target = npc

    print("\nAfter the combat:")
    print("    {} has {} HP".format(actor.name, actor.get("life")))

    npcs = local.get_npcs()
    for npc in npcs:
        if npc.alive:
            print("    {} has {} HP".format(npc.name, npc.get("life")))
        else:
            print("    {} is dead".format(npc.name))


if __name__ == "__main__":
    main()
