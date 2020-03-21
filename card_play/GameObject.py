from GameAction import GameAction


class GameObject:
    """
    This is the base class for all objects and actors.
    All it has is a name, description, and attributes.
    """

    def __init__(self, name, descr=None):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        """
        self.name = name
        self.description = descr
        self.attributes = {}

    def get(self, attribute):
        """
        return the value of an attribute

        @param attribute(string): name of attribute to be fetched
        @return (string): value (or none)
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            return None

    def set(self, attribute, value):
        """
        set the value of an attribute

        @param attribute(string): name of attribute to be fetched
        @param value(string): value to be stored for that attribute
        """
        self.attributes[attribute] = value

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action (GameAction): the action being performed
        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (string): description of the effect
        """
        # all action processing must be implemented in sub-classes
        return "{} cannot process ".format(self.name) \
               + "{} event".format(action.verb) \
               + "\n\tfrom {} ".format(actor.name) \
               + " using {}".format(action.source.name) \
               + "\n\tin {} of {}".format(context.name, context.parent.name)

    def possible_actions(self, actor, context):
        """
        return a list of (all) possible actions

        @param actor (GameActor): the actor initiating the action (ignored)
        @param context(GameContext): the most local context (ignored)
        @return (GameActions[]): list of possible actions
        """
        actions = []
        value = self.get("actions")
        if value is not None:
            for action in value.split(','):
                actions.append(GameAction(self, action))
        return actions


# basic GameObject test cases
if __name__ == "__main__":

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
