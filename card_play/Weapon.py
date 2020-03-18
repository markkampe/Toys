from GameObject import GameObject
from GameAction import GameAction


class Weapon(GameObject):
    """
    This is the base class for simple weapons
    with a single attack, bonus and damage
    """
    def __init__(self, name, descr=None, damage=8, bonus=0):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        @param damage(int): max damage
        @param bonus(int): hit/damage bonus
        """
        if descr is None:
            descr = "simple weapon"
        super().__init__(name, descr)
        self.set("damage", damage)
        self.set("bonus", bonus)

    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (GameActions[]): list of possible actions
        """
        actions = []
        attack = GameAction(self, "ATTACK")
        actions.append(attack)
        return actions
