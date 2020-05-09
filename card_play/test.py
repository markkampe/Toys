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


def objects_in_context(context):
    """
    print out a list of the (visable and invisable) objects in the context
    @param context: to be enumerated
    """
    stuff = context.get_objects()
    print("\n    objects:")
    for thing in stuff:
        hidden = thing.get("RESISTANCE.SEARCH")
        found = thing.get("SEARCH")
        if hidden is None or hidden == 0:
            print("\t{} ... {}".format(thing.name, thing.description))
        elif found is not None and found > 0:
            print("\t{} ... {} has now been discovered".
                  format(thing.name, thing.description))
    return


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
    guard.set("PROTECTION.pierce", 4)   # chainmail
    guard.set("reinforcements", 50)     # help is available
    local.add_npc(guard)

    # create a single PC with some skills and attributes
    actor = GameActor("Hero", "initiator")
    actor.set("LIFE", 32)           # initial hit points
    actor.set("EVASION", 20)        # good dodge
    actor.set("PROTECTION", 4)      # reasonable armor
    actor.set("ACCURACY", 50)       # good with a sword
    actor.set("POWER.SEARCH", 25)   # OK searching
    actor.set_context(local)

    skills = GameObject(actor.name)
    skills.set("ACTIONS", "PUSH,CHEAT,UNKNOWN-ACTION")
    local.add_member(actor)

    # create obvious and hidden objects in the local context
    bench = GameObject("bench", "obvious object")
    local.add_object(bench)
    trap_door = GameObject("trap-door", "hidden object")
    trap_door.set("RESISTANCE.SEARCH", 75)
    local.add_object(trap_door)
    coin = GameObject("coin", "non-obvious object")
    coin.set("RESISTANCE.SEARCH", 1)
    local.add_object(coin)
    local.set("ACTIONS", "SEARCH")

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

    objects_in_context(local)
    print()

    # try the context-afforded actins (incl SEARCH)
    actions = local.possible_actions(actor, local)
    for action in actions:
        result = actor.take_action(action, local)
        print("{} tries to {}(power={}) {}\n    {}"
              .format(actor.name,
                      action.verb, actor.get("POWER."+action.verb),
                      local.name, result))

    # now see what we can see
    objects_in_context(local)
    print()

    # EXERCISE OUR PERSONAL NON-COMBAT SKILLS
    actions = skills.possible_actions(actor, local)
    for action in actions:
        result = actor.take_action(action, guard)
        print("{} tries to {}(power={}) {}\n    {}"
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
    weapon.set("ACTIONS", "ATTACK.slash,ATTACK.chop,ATTACK.pierce")
    weapon.set("DAMAGE.slash", "D6+2")
    weapon.set("DAMAGE.chop", "D4+2")
    weapon.set("DAMAGE.pierce", "4")
    weapon.set("ACCURACY", 10)      # a good sword

    # play out the battle until hero or all guards are dead
    target = npcs[0]
    actions = weapon.possible_actions(actor, local)
    while target is not None and actor.get("LIFE") > 0:
        # choose a random attack
        attack = actions[randint(0, len(actions)-1)]
        result = actor.take_action(attack, target)
        print("\n{} uses {} to {} {}, delivered={}\n    {}"
              .format(actor.name, weapon.name, attack.verb, target.name,
                      attack.get("HIT_POINTS"), result))

        # give each NPC an action and choose a target for nextg round
        target = None
        npcs = local.get_npcs()
        for npc in npcs:
            if not npc.incapacitated:
                print(npc.take_turn())
                if target is None:
                    target = npc

    print("\nAfter the combat:")
    print("    {} has {} HP".format(actor.name, actor.get("LIFE")))

    npcs = local.get_npcs()
    for npc in npcs:
        if npc.alive:
            print("    {} has {} HP".format(npc.name, npc.get("LIFE")))
        else:
            print("    {} is dead".format(npc.name))


if __name__ == "__main__":
    main()
