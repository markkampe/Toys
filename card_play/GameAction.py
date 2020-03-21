from Dice import Dice
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
        if "ATTACK" in self.verb:
            # get and validate the basic combat parameters
            damage_spec = self.get("damage")
            if damage_spec is None:
                return self.source.name + " is not capable of doing damage"

            # compute the success roll
            roll = randint(1, 100)
            skill_bonus = self.get("skill_bonus")
            self.set("success",
                     roll if skill_bonus is None else roll + skill_bonus)
            # compute the damage
            hit_dice = Dice(damage_spec)
            roll = hit_dice.roll()
            damage_bonus = self.get("damage_bonus")
            self.set("delivered_damage",
                     roll if damage_bonus is None else roll + damage_bonus)

            # deliver it to the target
            return target.accept_action(self, initiator, context)

        # catch-all ... just pass it on to the target
        return target.accept_action(self, initiator, context)
