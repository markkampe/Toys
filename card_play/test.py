from GameObject import GameObject
from GameActor import GameActor
from GameAction import GameAction
from GameContext import GameContext
from Weapon import Weapon


if __name__ == "__main__":
    # create a context
    village = GameContext("Snaefelness", "village on north side of island")
    local = GameContext("town square", "center of village", village)

    # create a single NPC
    guard = GameActor("Guard", "test target")
    guard.set_context(local)
    guard.set("ac", 1)
    guard.set("hp", 16)
    local.add_npc(guard)

    # create a (single-actor) party
    actor = GameActor("Actor", "initiator")
    actor.set("thac0", 10)
    actor.set_context(local)
    local.add_member(actor)

    # create obvious and hidden objects in the local context
    bench = GameObject("bench", "obvious object")
    local.add_object(bench)

    trap_door = GameObject("trap-door", "hidden object")
    trap_door.set("hidden", True)
    local.add_object(trap_door)

    # see what is in the local context
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

    # do a search and see if we turn up anything
    search = GameAction(actor, "SEARCH")
    result = actor.take_action(search, local)
    print("{} searches {}\n    {}".format(actor.name, local.name, result))
    stuff = local.get_objects()
    print("\n    objects:")
    for thing in stuff:
        print("\t{} ... {}".format(thing.name, thing.description))
    print()


    # create a gizmo and use it to perform an unsupported action
    #  (to test pass through to the base class)
    gizmo = GameObject("gizmo", "non-weapon")
    non_action = GameAction(gizmo, "CONFUSE")
    result = actor.take_action(non_action, guard)
    print("{} uses {} to {} to {}\n    {}"
          .format(actor.name, gizmo.name,
                  non_action.verb, guard.name, result))
    print()

    # create a weapon
    weapon = Weapon("sword", damage=8, bonus=2)
    actions = weapon.possible_actions(actor, local)

    # use it to kill the guard
    attack = actions[0]
    target = npcs[0]

    while target.get("hp") >= 1:
        result = actor.take_action(attack, target)
        print("{} uses {} to {} to {}\n    {}"
              .format(actor.name, weapon.name, attack.verb,
                      target.name, result))
        print()
