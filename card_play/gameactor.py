""" This module implements the GameActor class """
from random import randint
from gameobject import GameObject
from gameaction import GameAction
from gamecontext import GameContext


class GameActor(GameObject):
    """
    A GameActor (typically a PC or NPC) is an agent that has a
    context and is capable of initiating and receiving actions.
    """

    def __init__(self, name="actor", descr=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        super(GameActor, self).__init__(name, descr)
        self.context = None
        self.alive = True
        self.incapacitated = False

    def accept_attack(self, action, actor, context):
        """
        Accept an attack, figure out if it hits, and how bad
        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which action is being taken
        @return:  (boolean, string) succewss and description of the effect

        """
        # A standard attack comes with at-least two standard attributes:
        #    TO_HIT ... the (pre defense) to-hit probability
        #    HIT_POINTS ... the (pre-armor) damage being delivered
        #
        # The target will apply evasion to determine if it is hit,
        # protection to see how much damage gets through, and then
        # update its life points.

        # get the victim's base evasion
        evade = self.get("EVASION")
        evasion = 0 if evade is None else int(evade)

        # add in any sub-type evasion
        if "ATTACK." in action.verb:
            evade = self.get("EVASION." + action.verb.split(".")[1])
            if evade is not None:
                evasion += int(evade)

        # see if TO_HIT can beat the evasion
        to_hit = action.get("TO_HIT") - evasion
        if to_hit < 100 and randint(1, 100) > to_hit:
            return (False, "{} evades {} {}"
                    .format(self.name, action.source.name, action.verb))

        # get the victim's base protection
        prot = self.get("PROTECTION")
        protection = 0 if prot is None else int(prot)

        # add in any sub-type protection
        if "ATTACK." in action.verb:
            prot = self.get("PROTECTION." + action.verb.split(".")[1])
            if prot is not None:
                protection += int(prot)

        # see how much of the delivered damage we actually take
        delivered = action.get("HIT_POINTS")

        if protection >= delivered:
            return (False, "{}'s protection absorbs all damage from {}"
                    .format(self.name, action.verb))

        # take the damage and see if we survive
        old_hp = self.get("LIFE")
        if old_hp is None:
            old_hp = 0
        new_hp = old_hp - (delivered - protection)
        self.set("LIFE", new_hp)

        result = "{} hit by {} from {} using {} for {}-{} life-points in {}" \
                 .format(self.name, action.verb, actor.name,
                         action.source.name,
                         delivered, protection, context.name) \
                 + "\n    {} life: {} - {} = {}" \
                 .format(self.name, old_hp, delivered - protection, new_hp)
        if new_hp <= 0:
            result += ", and is killed"
            self.alive = False
            self.incapacitated = True
        return (True, result)

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which action is being taken
        @return:  (boolean, string) description of the effect
        """
        # get the base action verb
        base_verb = action.verb.split('.')[0] \
            if '.' in action.verb else action.verb

        # attacks are based on HIT/EVADE and DAMAGE/PROTECTION
        if base_verb == "ATTACK":
            return self.accept_attack(action, actor, context)

        # see if our super class knows what to do with it
        return super(GameActor, self).accept_action(action, actor, context)

    # pylint: disable=unused-argument; I expect actor to be used later
    def interact(self, actor):
        """
        enable interactions with this NPC
        @param actor: GameActor initiating the interactions
        @return: Interaction object
        """
        interactions = GameObject("interactions w/" + self.name)
        verbs = self.get("INTERACTIONS")
        actions = ""
        if verbs is not None:
            for verb in verbs.split(','):
                actions += "VERBAL." if actions == "" else ",VERBAL."
                actions += verb
        interactions.set("ACTIONS", actions)
        return interactions

    def set_context(self, context):
        """
        establish the local context
        """
        self.context = context

    def take_action(self, action, target):
        """
        Initiate an action against a target
        @param action: GameAction to be initiated
        @param target: GameObject target of the action
        @return: (boolean, string) result of the action
        """
        return action.act(self, target, self.context)

    def take_turn(self):
        """
        called once per round in initiative order
        """
        return self.name + " takes no action"


def simple_attack_tests():
    """
    Base attacks with assured outcomes
    """
    attacker = GameActor("attacker")
    target = GameActor("target")
    context = GameContext("unit-test")

    # attack guarnteed to fail
    target.set("LIFE", 10)
    source = GameObject("weak-attack")
    action = GameAction(source, "ATTACK")
    action.set("ACCURACY", -100)
    action.set("DAMAGE", "1")
    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    (_, desc) = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + desc)
    print()

    # attack guaranteed to succeed
    source = GameObject("strong-attack")
    action = GameAction(source, "ATTACK")
    action.set("ACCURACY", 100)
    action.set("DAMAGE", "1")
    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    (_, desc) = action.act(attacker, target, context)
    assert target.get("LIFE") == 9, \
        "{} took incorrect damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + desc)
    print()

    # attack that will be evaded
    source = GameObject("evadable-attack")
    action = GameAction(source, "ATTACK")
    action.set("ACCURACY", 0)
    action.set("DAMAGE", "1")
    target.set("EVASION", 100)
    target.set("LIFE", 10)
    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    (_, desc) = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + desc)
    print()

    # attack that will be absorbabed
    source = GameObject("absorbable-attack")
    action = GameAction(source, "ATTACK")
    action.set("ACCURACY", 100)
    action.set("DAMAGE", "1")
    target.set("EVASION", 0)
    target.set("LIFE", 10)
    target.set("PROTECTION", 1)
    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    (_, desc) = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + desc)
    print()


def sub_attack_tests():
    """
    Attacks that draw on sub-type EVASION and PROTECTION
    """
    attacker = GameActor("attacker")
    target = GameActor("target")
    context = GameContext("unit-test")

    # evasion succeeds because base and sub-type add
    source = GameObject("evadable")
    action = GameAction(source, "ATTACK.subtype")
    action.set("ACCURACY", 0)
    action.set("DAMAGE", "1")

    target.set("LIFE", 10)
    target.set("EVASION", 50)
    target.set("EVASION.subtype", 50)

    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    (_, desc) = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + desc)

    # protection is sum of base and sub-type
    source = GameObject("absorbable")
    action = GameAction(source, "ATTACK.subtype")
    action.set("ACCURACY", 0)
    action.set("DAMAGE", "4")

    target.set("LIFE", 10)
    target.set("EVASION", 0)
    target.set("EVASION.subtype", 0)
    target.set("PROTECTION", 1)
    target.set("PROTECTION.subtype", 1)

    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    (_, desc) = action.act(attacker, target, context)
    assert target.get("LIFE") == 8, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 8, target.get("LIFE"))
    print("    " + desc)
    print()


def random_attack_tests():
    """
    attacks that depend on dice-rolls
    """
    attacker = GameActor("attacker")
    target = GameActor("target")
    context = GameContext("unit-test")

    target.set("LIFE", 10)
    source = GameObject("fair-fight")
    action = GameAction(source, "ATTACK")
    action.set("ACCURACY", 0)
    action.set("DAMAGE", "1")
    target.set("EVASION", 50)
    target.set("LIFE", 10)
    target.set("PROTECTION", 0)
    rounds = 10
    for _ in range(rounds):
        print("{} tries to {} {} with {}".
              format(attacker, action, target, source))
        (_, desc) = action.act(attacker, target, context)
        print("    " + desc)

    life = target.get("LIFE")
    assert life < 10, "{} took no damage in {} rounds".format(target, rounds)
    assert life > 10 - rounds, "{} took damage every round".format(target)
    print("{} was hit {} times in {} rounds".format(target, 10 - life, rounds))
    print()


def simple_condition_tests():
    """
    conditions that are guaranteed to happen or not
    """
    sender = GameActor("sender")
    target = GameActor("target")
    context = GameContext("unit-test")

    # impossibly weak condition will not happen
    source = GameObject("weak-condition")
    action = GameAction(source, "MENTAL.CONDITION-1")
    action.set("POWER", -100)
    action.set("STACKS", "10")
    print("{} tries to {} {} with {}".
          format(sender, action, target, source))
    (success, desc) = action.act(sender, target, context)
    assert not success, \
        "{} was successful against {}".\
        format(action.verb, target)
    assert target.get(action.verb) is None, \
        "{} RECEIVED {}={}". \
        format(target, action.verb, target.get(action.verb))
    print("    " + desc)

    # un-resisted condition will always happen
    source = GameObject("strong-condition")
    action = GameAction(source, "MENTAL.CONDITION-2")
    action.set("POWER", 0)
    action.set("STACKS", "10")
    print("{} tries to {} {} with {}".
          format(sender, action, target, source))
    (success, desc) = action.act(sender, target, context)
    assert success, \
        "{} was unsuccessful against {}".\
        format(action.verb, target)
    assert target.get(action.verb) == 10, \
        "{} RECEIVED {}={}". \
        format(target, action.verb, target.get(action.verb))
    print("    " + desc)

    # fully resisted condition will never happen
    source = GameObject("base-class-resisted-condition")
    action = GameAction(source, "MENTAL.CONDITION-3")
    action.set("POWER", 0)
    action.set("STACKS", "10")
    target.set("RESISTANCE.MENTAL", 100)
    print("{} tries to {} {} with {}".
          format(sender, action, target, source))
    (success, desc) = action.act(sender, target, context)
    assert not success, \
        "{} was successful against {}".\
        format(action.verb, target)
    assert target.get(action.verb) is None, \
        "{} RECEIVED {}={}". \
        format(target, action.verb, target.get(action.verb))
    print("    " + desc)

    print()


def sub_condition_tests():
    """
    conditions that draw on sub-type RESISTANCE
    """
    sender = GameActor("sender")
    target = GameActor("target")
    context = GameContext("unit-test")

    # MENTAL + sub-type are sufficient to resist it
    source = GameObject("sub-type-resisted-condition")
    action = GameAction(source, "MENTAL.CONDITION-4")
    action.set("POWER", 0)
    action.set("STACKS", "10")
    target.set("RESISTANCE.MENTAL", 50)
    target.set("RESISTANCE.MENTAL.CONDITION-4", 50)
    print("{} tries to {} {} with {}".
          format(sender, action, target, source))
    (success, desc) = action.act(sender, target, context)
    assert not success, \
        "{} was successful against {}".\
        format(action.verb, target)
    assert target.get(action.verb) is None, \
        "{} RECEIVED {}={}". \
        format(target, action.verb, target.get(action.verb))
    print("    " + desc)

    print()


def random_condition_tests():
    """
    conditions that depend on dice rolls
    """
    sender = GameActor("sender")
    target = GameActor("target")
    context = GameContext("unit-test")

    source = GameObject("partially-resisted-condition")
    action = GameAction(source, "MENTAL.CONDITION-5")
    action.set("POWER", 0)
    action.set("STACKS", "10")
    target.set("RESISTANCE.MENTAL", 25)
    target.set("RESISTANCE.MENTAL.CONDITION-5", 25)

    rounds = 5
    for _ in range(rounds):
        print("{} tries to {} {} with {}".
              format(sender, action, target, source))
        (success, desc) = action.act(sender, target, context)
        assert success, \
            "none of 10 stacks of {} got through".format(action.verb)
        print("    " + desc)

    delivered = rounds * 10
    expected = delivered / 2    # TO_HIT=100, RESISTANCE=50
    received = target.get(action.verb)
    assert received > 0.7 * expected, \
        "{} took {}/{} stacks".format(target, received, delivered)
    assert received < 1.3 * expected, \
        "{} took {}/{} stacks". format(target, received, delivered)
    print("{} took {}/{} stacks (vs {} expected)".
          format(target, received, delivered, int(expected)))

    print()


if __name__ == "__main__":
    simple_attack_tests()
    sub_attack_tests()
    random_attack_tests()
    simple_condition_tests()
    sub_condition_tests()
    random_condition_tests()
    print("All GameActor test cases passed")
