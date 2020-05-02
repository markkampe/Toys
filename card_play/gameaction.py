""" This module implements the GameAction class """
from random import randint
from dice import Dice


class GameAction(object):
    """
    A GameAction is an action possibility that is available to a GameActor.
    It has attributes that control its effects, and when its act() method
    is called, it delivers that action to the intended target.

    The most interetsting method is act(initiator, target, context)
    which informs the target to process the effects of the action.

    A GameAction is not a GameObject because
    (a) it does not support operations to generate and receive actions
    (b) get() operations are not passed up to the superclass.
    """

    # Lists of actions with known saves and conditions they cause
    #    if an action/attribute pair is on the first list, the save
    #    will be recorded in the GameAction so that the recipient
    #    automatically knows what save he needs to try to make
    #    against it.
    saves = {
        "PUSH": "dexterity",
        "CHEAT": "wisdom",
        "PURSUADE": "wisdom",
        "FLATTER": "wisdom",        # needs work
        "BEG": "wisdom",            # needs work
        "OUTRANK": "wisdom",        # needs work
        "INTIMIDATE": "strength",   # needs work
        "THREATEN": "strength"      # needs work
        }

    def __init__(self, source, verb):
        """
        create a new GameAction
        @param source: GameObject instrument for the action
        @param verb: the name of the action
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

        @param attribute: name of attribute to be fetched
        @return value (or none)
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        return None

    def set(self, attribute, value):
        """
        set the value of an attribute

        @param attribute: name of attribute to be fetched
        @param value: value to be stored for that attribute
        """
        self.attributes[attribute] = value

    def act(self, initiator, target, context):
        """
        Initiate an action against a target
        @param initiator: GameActor initiating the action
        @param target: GameObject target of the action
        @param context: GameContext in which this is happening
        @return: (string) result of the action

        The act() method knows how to process attacks and
        simple actions that require saves and produce
        conditions.  Any action requiring more complex
        processing (before calling the target) requires
        the implementation of a sub-class.
        """

        # ATTACK actions are likely to have the following properties:
        #    hit_bonus   ... a number to be added to a D100 success role
        #    damage      ... a (Dice) damage description
        #    special_damage  a (Dice) damage description to add to damage
        #    damage_bonus .. a (Dice) damage description to add to damage
        #
        # by the time they are passed to the target, they will have:
        #    success         ... the to-hit role (including all bonuses)
        #    delivered_damage .. the (pre-armor) damage being delivered
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
            # An action that requires a save may have been delivered
            # with some skill.  If the GameAction has the attribute
            # "skill", that number will be added to the D100 success roll.
            #
            # by the time they are passed to the target, they will have:
            #     success  ... the to-hit role (including all bonuses)
            #     save     ... the type of save the target must make
            roll = randint(1, 100)

            # if a skill is associated with this verb, add it to roll
            skill = self.get("skill")
            if skill is not None:
                roll += skill
            self.set("success", roll)
            return target.accept_action(self, initiator, context)

        # catch-all ... just pass it on to the target
        return target.accept_action(self, initiator, context)