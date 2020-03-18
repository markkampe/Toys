from random import seed
from random import randint


class GameAction:
    """
    A GameAction is an action possibility that is available to a GameActor.
    It has attributes that control its effects, and when its act() method
    is called, it delivers that action to the intended target.
    """
    verb = None
    source = None
    attributes = {}

    def __init__(self, source, verb):
        """
        create a new GameAction
        @param source(GameObject): the instrument for the action
        @param verb(string): the name of the action
        """
        self.source = source
        self.verb = verb

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

    def act(self, initiator, target, context):
        """
        Initiate an action against a target
        @param initiator (GameActor): who initiates the action
        @param target (GameObject): the target of the action
        @param context (GameContext): most local context
        @return (string): result of the action
        """
        # generic attack
        if self.verb == "ATTACK":
            # get and validate the basic combat parameters
            thac0 = initiator.get("thac0")
            if thac0 is None:
                return initiator.name + " is not capable of attacks"
            ac = target.get("ac")
            if ac is None:
                return target.name + " has no armor class"
            damage = self.source.get("damage")
            if damage is None:
                return self.source.name + " is not capable of doing damage"
            bonus = self.source.get("bonus")
            if bonus is None:
                bonus = 0

            # roll and see if we hit
            roll = randint(1, 20)
            if roll + bonus + ac < thac0:
                return "miss! {}+{} does not hit AC{}".format(roll, bonus, ac)

            # compute the damage
            self.set("damage", randint(1, damage) + bonus)
            return target.accept_action(self, initiator, context)

        # catch-all ... just pass it on to the target
        return target.accept_action(self, initiator, context)
