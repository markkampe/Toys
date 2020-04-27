from GameObject import GameObject
from GameAction import GameAction


class Weapon(GameObject):
    """
    This is the base class for simple weapons
    with a single attack, bonus and damage
    """
    def __init__(self, name, descr=None, damage=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        if descr is None:
            descr = "simple weapon"
        super().__init__(name, descr)
        if damage is not None:
            self.set("damage", damage)

    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is taken
        @return: list of possible GameActions
        """

        # get a list of possible actions with this weapon
        actions = super().possible_actions(actor, context)

        """
        A Weapon is expected to have a few standard properties:
            damage      ... a base (Dice) damage expression
            damage.xxx  ... a (Dice) damage expression for ATTACK.xxx
            hit_bonus       bonuses added to the to-hit roll
            damage_bonus    bonuses added to the damage roll

        These will be added to any ATTACK GameAction as:
            damage      ... the base damage expression
            special_damage  additional sub-attack damage
            hit_bonus   ... percentage to add to hit rolls
            damage_bonus .. points to add to damage rolls
        """
        base_damage = self.get("damage")
        for action in actions:
            verb = action.verb
            # we only care about attacks
            if 'ATTACK' not in verb:
                continue

            action.set("damage", base_damage)

            # check for additional sub-type specific damage
            if 'ATTACK.' in verb:
                sub_type = verb.split('.')[1]
                sub_type_damage = self.get("damage." + sub_type)
                if sub_type_damage is not None:
                    action.set("special_damage", sub_type_damage)

            # include any hit and damage bonuses
            bonus = self.get("hit_bonus")
            if bonus is not None:
                action.set("hit_bonus", bonus)
            bonus = self.get("damage_bonus")
            if bonus is not None:
                action.set("damage_bonus", bonus)

        return actions
