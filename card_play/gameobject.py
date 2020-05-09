""" This module implements the (foundation) GameObject Class """
from random import randint
from base import Base
from gameaction import GameAction


class GameObject(Base):
    """
    This is the base class for all objects and actors.
    Its only abilities are to offer and accept actions.
    """
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
            return "{} resists {} {}" \
                   .format(self.name, action.source.name, action.verb)

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

        return "{} resists {}/{} stacks of {} from {} in {}" \
               .format(self.name, incoming - received, incoming,
                       action.verb, actor, context)

    # pylint: disable=unused-argument; sub-classes are likely to use them
    def possible_actions(self, actor, context):
        """
        return a list of (all) possible actions

        @param actor: GameActor initiating the action (ignored)
        @param context: GameContext in which actions will be taken
        @return: list of possible GameActions
        """
        actions = []
        value = self.get("ACTIONS")
        if value is not None:
            for action in value.split(','):
                actions.append(GameAction(self, action))
        return actions


def main():
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

    print("All GameObject test cases passed")


if __name__ == "__main__":
    main()
