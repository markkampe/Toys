from Dice import Dice
from random import randint


class GameAction:
    """
    A GameAction is an action possibility that is available to a GameActor.
    It has attributes that control its effects, and when its act() method
    is called, it delivers that action to the intended target.

    It is not a GameObject because it does not support operations to
    generate and receive actions, and get() operations are not passed
    on to the superclass.
    """

    """
    Lists of actions with known saves and conditions they cause
        if an action/attribute pair is on the first list, the save
        will be recorded in the GameAction so that the recipient
        automatically knows what save he needs to try to make
        against it.
    """
    saves = {
                "PUSH": "dexterity",
                "CHEAT": "wisdom"
            }

    def __init__(self, source, verb):
        """
        create a new GameAction
        @param source(GameObject): the instrument for the action
        @param verb(string): the name of the action
        """
        self.source = source
        self.verb = verb
        self.attributes = {}

        # if this action has a known save, record it for use by the target
        if verb in self.saves.keys():
            self.set("save", self.saves[verb])

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
            hit_bonus = self.get("hit_bonus")
            if hit_bonus is not None:
                roll += hit_bonus
            self.set("success", roll)

            # compute the base damage
            hit_dice = Dice(damage_spec)
            roll = hit_dice.roll()
            dbg = "roll={}". format(roll)

            # compute the sub-class damage
            special_spec = self.get("special_damage")
            if special_spec is not None:
                hit_dice = Dice(special_spec)
                special = hit_dice.roll()
                roll += special
                dbg += ", spcl={}".format(special)

            # add in any damage bonus
            damage_bonus = self.get("damage_bonus")
            if damage_bonus is not None:
                roll += damage_bonus
                dbg += ", bonus={}".format(damage_bonus)

            # deliver it to the target
            self.set("delivered_damage", roll)
            return target.accept_action(self, initiator, context)
        elif "SAVE" in self.verb or self.get("save") is not None:
            roll = randint(1, 100)

            # if a skill is associated with this verb, add it to roll
            skill = self.get("skill")
            if skill is not None:
                roll += skill
            self.set("success", roll)
            return target.accept_action(self, initiator, context)

        # catch-all ... just pass it on to the target
        return target.accept_action(self, initiator, context)
