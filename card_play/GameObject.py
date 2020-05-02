""" This module implements the (foundation) GameObject Class """
from GameAction import GameAction


class GameObject(object):
    """
    This is the base class for all objects and actors.
    All it has is a name, description, and attributes.
    """

    def __init__(self, name, descr=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        self.name = name
        self.description = descr
        self.attributes = {}

    # pylint: disable=duplicate-code; GameAction needs this as well
    def get(self, attribute):
        """
        return: value of an attribute

        @param attribute: name of attribute to be fetched
        @return: (string) value (or none)
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            return None

    # pylint: disable=duplicate-code; GameAction needs this as well
    def set(self, attribute, value):
        """
        set the value of an attribute

        @param attribute: name of attribute to be fetched
        @param value: value to be stored for that attribute
        """
        self.attributes[attribute] = value

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which action is occuring
        @return: (string) description of the effect
        """
        # all action processing must be implemented in sub-classes
        return "{} cannot process ".format(self.name) \
               + "{} event".format(action.verb) \
               + "\n\tfrom {} ".format(actor.name) \
               + " using {}".format(action.source.name) \
               + "\n\tin {} of {}".format(context.name, context.parent.name)

    # pylint: disable=unused-argument; sub-classes are likely to use them
    def possible_actions(self, actor, context):
        """
        return a list of (all) possible actions

        @param actor: GameActor initiating the action (ignored)
        @param context: GameContext in which actions will be taken
        @return: list of possible GameActions
        """
        actions = []
        value = self.get("actions")
        if value is not None:
            for action in value.split(','):
                actions.append(GameAction(self, action))
        return actions


# pylint: disable=superfluous-parens; I prefer to consistently use print()
def main():
    """
    basic test GameObject test cases
    """

    describe = "simple get/set test object"
    go1 = GameObject("GameObject 1", describe)
    go2 = GameObject("GameObject 2")

    # new object has name, description, and nothing else
    print("Created 'GameObject 1', descr={}\n    got '{}', descr={}"
          .format(describe, go1.name, go1.description))
    assert (go1.name == "GameObject 1"), \
        "New object does not have assigned name"
    assert (go1.description == describe), \
        "New object does not have assigned description"

    # a new set correctly adds a value
    print("    before set(): get('attribute#1') -> {}"
          .format(go1.get("attribute#1")))
    assert (go1.get("attribute#1") is None), \
        "New object has attribute values before set"
    go1.set("attribute#1", "value1")
    print("    after set('attribute#1', 'value1'): get('attribute#1') -> '{}'"
          .format(go1.get("attribute#1")))
    assert (go1.get("attribute#1") == "value1"), \
        "set does not correctly set new value"

    # a second set correctly changes a value
    go1.set("attribute#1", "value2")
    print("    after set('attribute#1', 'value2'): get('attribute#1') -> '{}'"
          .format(go1.get("attribute#1")))
    assert (go1.get("attribute#1") == "value2"), \
        "set does not correctly change value"

    # description defaults to None
    print("Created 'GameObject, descr=None\n    got '{}', descr={}"
          .format(go2.name, go2.description))
    assert (go2.name == "GameObject 2"), \
        "New object does not have assigned name"
    assert (go2.description is None), \
        "New description does not default to None"

    # defaults to no actions
    actions = go1.possible_actions(None, None)
    assert (len(actions) == 0), \
        "New object returns non-empty action list"

    # added actions are returned
    test_actions = "ACTION,SECOND ACTION"
    go1.set("actions", test_actions)
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

    print("\nAll test cases passed")

if __name__ == "__main__":
    main()
