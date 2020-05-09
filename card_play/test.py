"""
Test cases and sample code to show how the basic methods
of the key classes can be used.
"""
import argparse
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
    print("\n    recognized objects:")
    for thing in stuff:
        print("\t{} ... {}".format(thing.name, thing.description))

    stuff = context.get_objects(hidden=True)
    print("\n    undiscovered objects:")
    for thing in stuff:
        print("\t{} ... {}".format(thing.name, thing.description))
    return


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
def main():
    """
    test cases and sample code
    """
    # figure out what we have been asked to do
    parser = argparse.ArgumentParser(description='general test cases')
    parser.add_argument("--nocombat",
                        dest="no_combat", action="store_true", default=False)
    args = parser.parse_args()

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
    actor.set("DAMAGE", "D4")       # with some extra damage
    actor.set("POWER.SEARCH", 25)   # OK searching
    actor.set("POWER.PHYSICAL", 25)     # moderately strong & skilled
    actor.set("ACTIONS", "PHYSICAL.PUSH,PHYSICAL.TRIP")
    actor.set_context(local)

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
        (_, desc) = actor.take_action(action, local)
        print("{} tries to {}(power={}) {}\n    {}"
              .format(actor.name,
                      action.verb, actor.get("POWER."+action.verb),
                      local.name, desc))

    # now see what we can see
    objects_in_context(local)
    print()

    # attempt some interactions with the guard
    actor.set("POWER.VERBAL.CHEAT", 50)
    actor.set("STACKS.VERBAL.BEG", 5)
    guard.set("RESISTANCE.VERBAL", 50)
    guard.set("RESISTANCE.VERBAL.FLATTER", -10)
    guard.set("RESISTANCE.VERBAL.OUTRANK", 100)
    guard.set("RESISTANCE.VERBAL.INTIMMIDATE", 100)
    interactions = guard.interact(actor)
    actions = interactions.possible_actions(actor, local)
    for interaction in actions:
        (_, desc) = actor.take_action(interaction, guard)
        verb = interaction.verb
        print("\n{} uses {} interaction on {}\n    {}"
              .format(actor.name, verb, guard.name, desc))
        print("    {}.{} = {}".format(guard.name, verb, guard.get(verb)))

    # TRY PHYSICAL ACTIONS on the guard
    guard.set("RESISTANCE.PHYSICAL", 75)    # he's tough
    actions = actor.possible_actions(actor, local)
    for action in actions:
        (_, desc) = actor.take_action(action, guard)
        verb = action.verb
        print("\n{} tries to {} {}\n    {}"
              .format(actor.name, verb, guard.name, desc))
        print("    {}.{} = {}".format(guard.name, verb, guard.get(verb)))
    print()

    # CREATE A WEAPON AND USE IT TO ATTACK THE GUARD
    if args.no_combat:
        return

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
        (_, desc) = actor.take_action(attack, target)
        print("\n{} uses {} to {} {}, delivered={}\n    {}"
              .format(actor.name, weapon.name, attack.verb, target.name,
                      attack.get("HIT_POINTS"), desc))

        # give each NPC an action and choose a target for nextg round
        target = None
        npcs = local.get_npcs()
        for npc in npcs:
            if not npc.incapacitated:
                (_, desc) = npc.take_turn()
                print(desc)
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
