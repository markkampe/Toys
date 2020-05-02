""" This module implements the GameActor class """
from gameobject import GameObject


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

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
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
            # A standard attack comes with at-least two standard attributes:
            #    success         ... the to-hit role (including all bonuses)
            #    delivered_damage .. the (pre-armor) damage being delivered
            #
            # The target will apply evasion to determine if it is hit,
            # protection to see how much damage gets through, and then
            # update its life points.

            # see if we are able to evade the attack
            attack = action.get("success")
            evasion = self.get("evasion." + sub_type)
            if evasion is None:
                evasion = self.get("evasion")
            if evasion is not None and attack <= int(evasion):
                return "{} evades {} {} ... evasion={} vs attack={}" \
                       .format(self.name, action.source.name, action.verb,
                               evasion, attack)

            # see how much of the delivered damage we take
            delivered = action.get("delivered_damage")
            protection = self.get("protection." + sub_type)
            if protection is None:
                protection = self.get("protection")
            reduction = 0 if protection is None else int(protection)
            damage = delivered - reduction

            old_hp = self.get("life")
            if delivered > reduction:
                new_hp = old_hp - damage
                self.set("life", new_hp)

                result = "{} hit by {} using {} for {}-{} life-points in {}" \
                         .format(self.name, actor.name, action.source.name,
                                 delivered, reduction, context.name) \
                         + "\n    {} life: {} - {} = {}"\
                           .format(self.name, old_hp, damage, new_hp)
                if new_hp <= 0:
                    result += ", and is killed"
                    self.alive = False
                    self.incapacitated = True
            else:
                result = "{}'s protection absorbs all damage from {}" \
                         .format(self.name, action.verb)
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