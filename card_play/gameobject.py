""" This module implements the (foundation) GameObject Class """
import sys
from random import randint
from base import Base
from gameaction import GameAction


class GameObject(Base):
    """
    This is the base class for all objects and actors.
    Its only abilities are
        to own objects
        to offer and accept actions.
    """
    def __init__(self, name="actor", descr=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        super(GameObject, self).__init__(name, descr)
        self.objects = []

    def __str__(self):
        """
        return string description of this weapon
        """
        return self.name

    def get_objects(self, hidden=False):
        """
        @param hidden: hidden (rather than obvious) objects
        @return: list of GameOjects in this context
        """
        reported = []
        for thing in self.objects:
            atr = thing.get("RESISTANCE.SEARCH")
            concealed = atr is not None and atr > 0
            atr = thing.get("SEARCH")
            found = atr is not None and atr > 0

            if hidden:
                if concealed and not found:
                    reported.append(thing)
            else:
                if found or not concealed:
                    reported.append(thing)

        return reported

    def add_object(self, item):
        """
        add another object to this context
        """
        if item not in self.objects:
            self.objects.append(item)

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which action is occuring
        @return: (string) description of the effect
        """
        # get the base verb and sub-type
        if '.' in action.verb:
            base_verb = action.verb.split('.')[0]
            sub_type = action.verb.split('.')[1]
        else:
            base_verb = action.verb
            sub_type = None

        # check our base resistance
        res = self.get("RESISTANCE")
        resistance = 0 if res is None else int(res)

        # see if we have a base-type resistance
        res = self.get("RESISTANCE." + base_verb)
        if res is not None:
            resistance += int(res)

        # see if we have a sube-type resistance
        if sub_type is not None:
            res = self.get("RESISTANCE." + base_verb + "." + sub_type)
            if res is not None:
                resistance += int(res)

        # see if we can resist it entirely
        power = int(action.get("TO_HIT")) - resistance
        if power <= 0:
            return (False, "{} resists {} {}"
                    .format(self.name, action.source.name, action.verb))

        # see how many stacks we can resist
        received = 0
        incoming = int(action.get("TOTAL"))
        for _ in range(incoming):
            roll = randint(1, 100)
            if roll <= power:
                received += 1

        # deliver the updated condition
        if received > 0:
            have = self.get(action.verb)
            if have is None:
                self.set(action.verb, received)
            else:
                self.set(action.verb, received + int(have))

        return (received > 0,
                "{} resists {}/{} stacks of {} from {} in {}"
                .format(self.name, incoming - received, incoming,
                        action.verb, actor, context))

    # pylint: disable=unused-argument; sub-classes are likely to use them
    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is taken
        @return: list of possible GameActions

        PROBLEM:
            Base and sub-type ACCURACY values add, as they should.
            This is harder to do with DAMAGE because those are not
            (easily added) values, but dice formulae.  For now,
            we simply use the sub-type value if present, else the
            base value.
        """
        # get our base accuracy and damage (for ATTACK actions)
        base_damage = self.get("DAMAGE")
        base_accuracy = self.get("ACCURACY")

        # get a list of possible actions with this weapon
        actions = []
        verbs = self.get("ACTIONS")
        if verbs is None:
            return []

        for verb in verbs.split(','):
            action = GameAction(self, verb)

            # if is an ATTACK, we need to add ACCURACY and DAMAGE
            if verb.startswith("ATTACK"):
                # see if we hae sub-type accuracy/damage
                sub_accuracy = None
                sub_damage = None
                if verb.startswith('ATTACK.'):
                    sub_type = verb.split('.')[1]
                    sub_accuracy = self.get("ACCURACY." + sub_type)
                    sub_damage = self.get("DAMAGE." + sub_type)

                # combine the base and sub-type values
                accuracy = 0 if base_accuracy is None else int(base_accuracy)
                accuracy += 0 if sub_accuracy is None else int(sub_accuracy)
                action.set("ACCURACY", int(accuracy))

                # FIX GameAction.DAMAGE is a formula and cannot be added
                if sub_damage is not None:
                    action.set("DAMAGE", sub_damage)
                elif base_damage is not None:
                    action.set("DAMAGE", base_damage)
                else:
                    action.set("DAMAGE", "0")

            actions.append(action)

        return actions

    def load(self, filename):
        """
        read attributes from a file
        @param filename: name of file to be read
        """
        cur_object = self

        try:
            infile = open(filename, "r")
            for line in infile:
                # see if we can lex it into two white-space separated fields
                (name, value) = lex(line)
                if name is None:
                    continue

                # check for a few special names
                if name == "NAME":
                    cur_object.name = value
                elif name == "DESCRIPTION":
                    cur_object.description = value
                elif name == "OBJECT":
                    cur_object = GameObject()
                    self.add_object(cur_object)
                else:
                    cur_object.set(name, value)

            infile.close()
        except IOError:
            sys.stderr.write("Unable to read attributes from {}\n".
                             format(filename))


def lex(line):
    """
    try to lex a name and (potentially quoted) value from a line
    @param line: string to be lexed
    @return: (name, value)
    """
    # find the start of the first token
    start = 0
    eol = len(line)
    while start < eol and line[start].isspace():
        start += 1

    # see if this is a comment or blank line
    if start >= eol or line[start] == "#":
        return (None, None)

    # find the end of this token
    end = start + 1
    while end < eol and not line[end].isspace():
        end += 1
    name = line[start:end]

    # find the start of the next token
    start = end
    while start < eol and line[start].isspace():
        start += 1

    # see if there is no next token
    if start >= eol or line[start] == "#":
        return (name, None)

    # does the next token start with a quote
    if line[start] == '"' or line[start] == "'":
        # scan until the closing quote (or EOL)
        quote = line[start]
        start += 1
        end = start + 1
        while end < eol and line[end] != quote:
            end += 1
        value = line[start:end]
    else:
        # scan until a terminating blank (or EOL)
        end = start + 1
        while end < eol and not line[end].isspace():
            end += 1

        # if it is an un-quoted number, convert it
        try:
            value = int(line[start:end])
        except ValueError:
            value = line[start:end]

    return (name, value)


def action_test():
    """
    basic test GameObject test cases
    """

    describe = "simple get/set test object"
    go1 = GameObject("GameObject 1", describe)

    # defaults to no actions
    actions = go1.possible_actions(None, None)
    assert (not actions), \
        "New object returns non-empty action list"

    # added actions are returned
    test_actions = "ACTION,SECOND ACTION"
    go1.set("ACTIONS", test_actions)
    print("Set actions='{}', possible_actions returns:".format(test_actions))
    actions = go1.possible_actions(None, None)
    for action in actions:
        print("    {}".format(action.verb))
    assert (len(actions) == 2), \
        "possible_actions returns wrong number of actions"
    assert (actions[0].verb == "ACTION"), \
        "first action not correctly returned"
    assert (actions[1].verb == "SECOND ACTION"), \
        "second action not correctly returned"


def weapon_test():
    """
    test for weapon actions and damage
    """
    # by default a weapon has no actions or attributes
    w_0 = GameObject("Null Weapon")
    assert w_0.name == "Null Weapon", \
        "Incorrect name: expected w_0"
    assert w_0.get("DAMAGE") is None, \
        "Incorrect default damage: expected None"
    assert w_0.get("ACCURACY") is None, \
        "Incorrect default accuracy, expected None"
    actions = w_0.possible_actions(None, None)
    assert not actions, \
        "incorrect default actions, expected None"
    print("test #1: " + str(w_0) +
          " ... NO ATTACKS, ACCURACY or DAMAGE - CORRECT")

    # if a weapon is created with damage, it has ATTACK
    w_1 = GameObject("Simple Weapon")
    w_1.set("ACTIONS", "ATTACK")
    w_1.set("ACCURACY", 66)
    w_1.set("DAMAGE", "666")
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
    print("test #2: " + str(w_1) +
          " ... BASE ATTACK, ACCURACY and DAMAGE - CORRECT")

    # multi-attack weapons have (addative) damage and accuracy for each attack
    # pylint: disable=bad-whitespace
    w_2 = GameObject("multi-attack weapon")

    attacks = [
        # verb,    accuracy, damage, exp acc, exp dmg
        ("ATTACK",       50,   "D5",      50,    "D5"),
        ("ATTACK.60",    10,   "D6",      60,    "D6"),
        ("ATTACK.70",    20,   "D7",      70,    "D7")]
    verbs = None
    for (verb, accuracy, damage, exp_acc, exp_dmg) in attacks:
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
        (verb, accuracy, damage, exp_acc, exp_dmg) = attacks[index]
        action = actions[index]
        assert action.verb == verb, \
            "action {}, verb={}, expected {}".format(index, action.verb, verb)
        assert action.get("ACCURACY") == exp_acc, \
            "action {}, expected ACCURACY={}, got {}". \
            format(action.verb, exp_acc, action.get("ACCURACY"))
        assert action.get("DAMAGE") == exp_dmg, \
            "action {}, expected DAMAGE={}, got {}". \
            format(action.verb, exp_dmg, action.get("DAMAGE"))
        print("test #3: {} {} ... ACCURACY({}) and DAMAGE({}) - CORRECT".
              format(w_2.name, action.verb,
                     "base plus sub-type" if "." in verb else "base only",
                     "sub-type only" if "." in verb else "base only"))


if __name__ == "__main__":
    action_test()
    weapon_test()
    print("All GameObject test cases passed")
