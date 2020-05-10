"""
Test cases and sample code to show how the basic methods
of the key classes can be used.
"""
import argparse
from random import randint
from gameactor import GameActor
from npc_guard import NPC_guard
from gamecontext import GameContext


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
    local = GameContext(parent=village)
    local.load("TEST_context.dat")

    # create a single NPC with some attributes and armor
    guard = NPC_guard()
    guard.load("TEST_guard.dat")
    local.add_npc(guard)

    # create a single PC with some skills and attributes
    actor = GameActor()
    actor.load("TEST_hero.dat")
    actor.set_context(local)
    local.add_member(actor)

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
    interactions = guard.interact(actor)
    actions = interactions.possible_actions(actor, local)
    for interaction in actions:
        (_, desc) = actor.take_action(interaction, guard)
        verb = interaction.verb
        print("\n{} uses {} interaction on {}\n    {}"
              .format(actor.name, verb, guard.name, desc))
        print("    {}.{} = {}".format(guard.name, verb, guard.get(verb)))

    # TRY PHYSICAL ACTIONS on the guard
    actions = actor.possible_actions(actor, local)
    for action in actions:
        (_, desc) = actor.take_action(action, guard)
        verb = action.verb
        print("\n{} tries to {} {}\n    {}"
              .format(actor.name, verb, guard.name, desc))
        print("    {}.{} = {}".format(guard.name, verb, guard.get(verb)))
    print()

    # find the Hero's sword
    weapon = actor.get_objects()[0]

    # play out the battle until hero or all guards are dead
    if args.no_combat:
        return

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
