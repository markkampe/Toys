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

    # if an action/condition pair is on the list and
    # a target fails his save, the named condition
    # will be instantiated in the target GameActor.
    # (tho giving that condition effect may still require
    # additional code somewhere else)
    fail_conditions = {
        "PUSH": "off-balance",
        "CHEAT": "fooled",
        "PURSUADE": "convinced",
        "FLATTER": "sympathetic",
        "BEG": "sympathetic",
        "OUTRANK": "respectful",
        "INTIMIDATE": "obedient",
        "THREATEN": "firghtened"
        }

    make_conditions = {
        "PUSH": "on-guard",
        "CHEAT": "suspicious",
        "PURSUADE": "skeptical",
        "FLATTER": "unsympathetic",
        "BEG": "unsympathetic",
        "OUTRANK": "hostile",
        "INTIMIDATE": "hostile",
        "THREATEN": "hostile"
        }

    def __init__(self, name, descr=None):
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
        @return:  (string) description of the effect

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
            return "{} evades {} {}" \
                   .format(self.name, action.source.name, action.verb)

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
            return "{}'s protection absorbs all damage from {}" \
                   .format(self.name, action.verb)

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
                 + "\n    {} life: {} - {} = {}"\
                 .format(self.name, old_hp, delivered - protection, new_hp)
        if new_hp <= 0:
            result += ", and is killed"
            self.alive = False
            self.incapacitated = True
        return result

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which action is being taken
        @return:  (string) description of the effect
        """
        # figure out the action verb and sub-type
        if '.' in action.verb:
            parts = action.verb.split('.')
            base_verb = parts[0]
            sub_type = parts[1]
        else:
            base_verb = action.verb
            sub_type = None

        # TODO: non-attacks have RESISTANCE (base+subtype)
        # saves or actions that require saves
        if base_verb == "SAVE":
            attribute = sub_type
        else:
            attribute = action.get("save")

        # a save-requiring action will generally have at least
        # two standard attributes:
        #    success  ... the to-hit role (including all bonuses)
        #    save     ... the type of save the target must make
        if attribute is not None:
            attack = action.get("success")
            save = self.get(attribute)
            if save is None:
                save = 0
            saved = attack <= save
            result = "{} {} his {} save ({} vs {})" \
                     .format(self.name,
                             "makes" if saved else "fails",
                             attribute, save, attack)

            # Depending on whether or not the save was made, we
            # may know what conditions to set to True or False
            if base_verb in self.make_conditions.keys():
                condition = self.make_conditions[base_verb]
                self.set(condition, saved)
                result += ", he is {} {}" \
                          .format("now" if saved else "not", condition)

            if base_verb in self.fail_conditions.keys():
                condition = self.fail_conditions[base_verb]
                self.set(condition, not saved)
                result += ", and is {} {}" \
                          .format("not" if saved else "now", condition)
        elif base_verb == "ATTACK":
            result = self.accept_attack(action, actor, context)
        else:
            # if we don't recognize this action, pass it up the chain
            result = super(GameActor, self).accept_action(action,
                                                          actor, context)
        return result

    def set_context(self, context):
        """
        establish the local context
        """
        self.context = context

    # TODO: actors now have skill based actions against NPCs

    def take_action(self, action, target):
        """
        Initiate an action against a target
        @param action: GameAction to be initiated
        @param target: GameObject target of the action
        @return: (string) result of the action
        """
        result = action.act(self, target, self.context)
        return result

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
    result = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + result)
    print()

    # attack guaranteed to succeed
    source = GameObject("strong-attack")
    action = GameAction(source, "ATTACK")
    action.set("ACCURACY", 100)
    action.set("DAMAGE", "1")
    print("{} tries to {} {} with {}".
          format(attacker, action, target, source))
    result = action.act(attacker, target, context)
    assert target.get("LIFE") == 9, \
        "{} took incorrect damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + result)
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
    result = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + result)
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
    result = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + result)
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
    result = action.act(attacker, target, context)
    assert target.get("LIFE") == 10, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 10, target.get("LIFE"))
    print("    " + result)

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
    result = action.act(attacker, target, context)
    assert target.get("LIFE") == 8, \
        "{} took damage, LIFE: {} -> {}". \
        format(target, 8, target.get("LIFE"))
    print("    " + result)
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
        result = action.act(attacker, target, context)
        print("    " + result)

    life = target.get("LIFE")
    assert life < 10, "{} took no damage in {} rounds".format(target, rounds)
    assert life > 10 - rounds, "{} took damage every round".format(target)
    print("{} was hit {} times in {} rounds".format(target, 10 - life, rounds))


if __name__ == "__main__":
    simple_attack_tests()
    sub_attack_tests()
    random_attack_tests()
    print("All GameActor test cases passed")
