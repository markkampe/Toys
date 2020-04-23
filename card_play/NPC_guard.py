from GameActor import GameActor
from Weapon import Weapon
from Interaction import Interaction
from random import randint


class NPC_guard(GameActor):
    """
    A guard is a low-level NPC fighter who will quickly
    engage and can call for reinforcements.
    """
    def __init__(self, name, descr=None):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        """
        super().__init__(name, descr)
        self.context = None

        # default attributes ... easily changed after instantiation
        self.set("life", 16)
        self.set("evasion", 50)
        self.set("evasion.slash", 20)   # slashes are harder to dodge
        self.set("dexterity", 15)
        self.set("wisdom", 10)
        self.set("protection", 2)       # by default, cheap armor
        self.set("reinforcements", 0)   # by default, alone

        self.weapon = Weapon("sword", damage="D6")
        self.weapon.set("actions", "ATTACK.slash")
        self.weapon.set("damage.slash", "D6")

        # sub-class combat attributes
        self.help_arrived = False
        self.target = None

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action (GameAction): the action being performed
        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (string): description of the effect

        The only special things about a guard ar that, if attacked
         (1) he counter-attacks
         (2) he can call for reinforcements.

        """
        # remember where this is happening
        self.context = context

        # start with standard GameActor responses
        result = super().accept_action(action, actor, context)

        # figure out the action verb and sub-type
        if '.' in action.verb:
            parts = action.verb.split('.')
            base_verb = parts[0]
            sub_type = parts[1]
        else:
            base_verb = action.verb
            sub_type = None

        # if I have been attacked, and am not dead
        if base_verb == "ATTACK" and \
           self.get("life") > 0:
            # counter attack when our turn comes
            self.target = actor

            # see if we can call for help
            if self.get("reinforcements") > 0 and not self.help_arrived:
                result += "\n    " + self.name + " calls for help"
                roll = randint(1, 100)
                if roll <= self.get("reinforcements"):
                    helper = NPC_guard("Guard #2", "test reinforcement")
                    helper.target = actor
                    result += ", and " + helper.name + " arrives"
                    context.add_npc(helper)
                    helper.set_context(context)
                    self.help_arrived = True

        # and return our (perhaps updated) result
        return result

    def take_turn(self):
        """
        Take action when your turn comes.
        The only actions this test Guard can take are fighting back
        """
        if self.target is not None:
            weapon = self.weapon
            actions = weapon.possible_actions(self.target, self.context)
            attack = actions[randint(0, len(actions)-1)]
            result = self.take_action(actions[0], self.target)
            return ("\n{} uses {} to {} {}, delivered={}+{}\n    {}"
                    .format(self.name, weapon.name, attack.verb,
                            self.target.name, attack.get("damage"),
                            attack.get("special_damage"), result))
        else:
            return super().take_turn()

    def interact(self, actor):
        """
        enable interactions with this NPC
        @param actor (GameActor): actor initiating the interactions
        @return Interaction object
        """
        return Interaction(self.name, self)
