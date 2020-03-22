from GameObject import GameObject
from GameActor import GameActor
from GameAction import GameAction
from GameContext import GameContext
from Weapon import Weapon
from Skills import Skills
from random import randint


if __name__ == "__main__":
    # create a context
    village = GameContext("Snaefelness", "village on north side of island")
    local = GameContext("town square", "center of village", village)

    # create a single NPC
    guard = GameActor("Guard", "test target")
    guard.set_context(local)
    guard.set("life", 16)
    guard.set("evasion", 50)
    guard.set("dexterity", 15)
    guard.set("evasion.slash", 20)  # harder to dodge
    guard.set("protection", 2)
    guard.set("protection.pierce", 4)  # chainmail
    local.add_npc(guard)

    # create a (single-actor) party
    actor = GameActor("Hero", "initiator")
    actor.set("perception", 25)
    actor.set("actions","SAVE.dexterity")   # just an example
    actor.set_context(local)
    local.add_member(actor)

    skills = Skills(actor.name)
    skills.set("actions", "SEARCH")

    # create obvious and hidden objects in the local context
    bench = GameObject("bench", "obvious object")
    local.add_object(bench)

    trap_door = GameObject("trap-door", "hidden object")
    trap_door.set("concealment", 50)
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
    actions = skills.possible_actions(actor, local)
    search = actions[0]
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
    gizmo.set("actions", "CONFUSE")
    non_actions = gizmo.possible_actions(actor, local)
    result = actor.take_action(non_actions[0], guard)
    print("{} uses {} to {} to {}\n    {}"
          .format(actor.name, gizmo.name,
                  non_actions[0].verb, guard.name, result))
    print()

    # force a dex save on the guard
    tricks = actor.possible_actions(actor, local)
    result = actor.take_action(tricks[0], guard)
    print("{} forces {} to {}\n    {}"
          .format(actor.name, guard.name, tricks[0].verb, result))
    print()

    # create a sword for the hero to use
    weapon = Weapon("sword", damage="D6")
    weapon.set("actions", "ATTACK.slash,ATTACK.chop,ATTACK.pierce")
    weapon.set("damage.slash", "D6")
    weapon.set("damage.chop", "D4")
    weapon.set("damage.pierce", "4")
    weapon.set("hit_bonus", 10)
    weapon.set("damage_bonus", 2)

    # use it to kill the guard
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
