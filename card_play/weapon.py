""" This module implements (the general case of a) Weapon
"""
from gameobject import GameObject


class Weapon(GameObject):
    """
    This is the base class for simple weapons

    In addition to (the standard) ACTIONS, a weapon is
    is expected to have a few other standard properties:
          DAMAGE      ... a base (Dice) damage expression
          ACCURACY    ... a base (percentage) accuracy
          DAMAGE.xxx  ... a (Dice) damage expression for ATTACK.xxx
          ACCURACY.xxx ...a (percentage) accuracy for ATTACK.xxx
    """
    def __init__(self, name, descr=None, damage=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        @param damage: damage formula for simple ATTACK
        """
        if descr is None:
            descr = "simple weapon"
        super(Weapon, self).__init__(name, descr)

        if damage is not None:
            self.set("ACTIONS", "ATTACK")
            self.set("DAMAGE", damage)

    def __str__(self):
        """
        return string description of this weapon
        """
        result = self.name

        actions = self.get("ACTIONS")
        if actions is not None:
            first = True
            for action in actions.split(","):
                result += "(" if first else ", "
                result += action
                first = False
            result += ")"

        return result

    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is taken
        @return: list of possible GameActions
        """

        # get a list of possible actions with this weapon
        actions = super(Weapon, self).possible_actions(actor, context)

        base_damage = self.get("DAMAGE")
        base_accuracy = self.get("ACCURACY")

        for action in actions:
            verb = action.verb
            # attacks require special handling
            if 'ATTACK' not in verb:
                continue

            # check for additional sub-type specific damage
            damage = None
            accuracy = None
            if 'ATTACK.' in verb:
                sub_type = verb.split('.')[1]
                damage = self.get("DAMAGE." + sub_type)
                accuracy = self.get("ACCURACY." + sub_type)

            action.set("DAMAGE",
                       base_damage if damage is None else damage)
            action.set("ACCURACY",
                       base_accuracy if accuracy is None else accuracy)

        return actions


# pylint: disable=superfluous-parens; for consistency, I always use print()
def main():
    """
    test for weapon actions and damage
    """
    # by default a weapon has no actions or attributes
    w_0 = Weapon("Null Weapon")
    assert w_0.name == "Null Weapon", \
        "Incorrect name: expected w_0"
    assert w_0.get("DAMAGE") is None, \
        "Incorrect default damage: expected None"
    assert w_0.get("ACCURACY") is None, \
        "Incorrect default accuracy, expected None"
    actions = w_0.possible_actions(None, None)
    assert len(actions) == 0, \
        "incorrect default actions, expected None"
    print("test #1: " + str(w_0) + " ... CORRECT")

    # if a weapon is created with damage, it has ATTACK
    w_1 = Weapon("Simple Weapon", damage="666")
    w_1.set("ACCURACY", 66)
    assert w_1.get("DAMAGE") == "666", \
        "Incorrect default damage: expected '666'"
    assert w_1.get("ACCURACY") == 66, \
        "Incorrect default accuracy, expected 66"
    actions = w_1.possible_actions(None, None)
    assert len(actions) == 1, \
        "incorrect default actions, expected ['ATTACK'], got " + str(actions)
    assert actions[0].verb == "ATTACK", \
        "incorrect default action, expected 'ATTACK', got " + str(actions[0])
    assert actions[0].get("DAMAGE") == "666", \
        "incorrect base damage, expected '666', got " + str(actions[0])
    assert actions[0].get("ACCURACY") == 66, \
        "incorrect base accuracy, expected 66, got " + str(actions[0])
    print("test #2: " + str(w_1) + " ... CORRECT")

    # multi-attack weapons have damage and accuracy for each attack
    # pylint: disable=bad-whitespace
    w_2 = Weapon("multi-attack weapon")

    attacks = [
        # verb,    accuracy, damage
        ("ATTACK",       50,     "5"),
        ("ATTACK.60",    60,     "6"),
        ("ATTACK.70",    70,     "7")]
    verbs = None
    for (verb, accuracy, damage) in attacks:
        if verbs is None:
            verbs = verb
        else:
            verbs += "," + verb
        if "." in verb:
            sub_verb = verb.split(".")[1]
            w_2.set("ACCURACY." + sub_verb, accuracy)
            w_2.set("DAMAGE." + sub_verb, damage)
        else:
            w_2.set("ACCURACY", accuracy)
            w_2.set("DAMAGE", damage)

    w_2.set("ACTIONS", verbs)
    actions = w_2.possible_actions(None, None)
    assert len(actions) == 3, \
        "incorrect actions list, expected 3, got " + str(actions)

    # pylint: disable=consider-using-enumerate; two parallel lists
    for index in range(len(actions)):
        (verb, accuracy, damage) = attacks[index]
        action = actions[index]
        assert action.verb == verb, \
            "action {}, verb={}, expected {}".format(index, action.verb, verb)
        assert action.get("ACCURACY") == accuracy, \
            "action {}, expected ACCURACY={}, got {}". \
            format(action.verb, accuracy, action.get("ACCURACY"))
        assert action.get("DAMAGE") == damage, \
            "action {}, expected DAMAGE={}, got {}". \
            format(action.verb, damage, action.get("DAMAGE"))
    print("test #3: " + str(w_2) + " ... CORRECT")

    print("All Weapon test cases passed")


if __name__ == "__main__":
    main()
