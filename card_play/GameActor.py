from GameObject import GameObject
from GameAction import GameAction
from GameContext import GameContext


class GameActor(GameObject):
    """
    A GameActor (typically a PC or NPC) is an agent that has a
    context and is capable of initiating and receiving actions.
    """
    context = None

    def __init__(self, name, descr=None):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        """
        super().__init__(name, descr)

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action (GameAction): the action being performed
        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (string): description of the effect
        """
        if action.verb == "ATTACK":
            damage = action.get("damage")
            old_hp = self.get("hp")
            new_hp = old_hp - damage
            self.set("hp", new_hp)
            result = "{} is hit by {} using {} for {}HP in {}" \
                     .format(self.name, actor.name,
                             action.source.name, damage, context.name) \
                     + "\n    HP: {} - {} = {}".format(old_hp, damage, new_hp)
            if new_hp <= 0:
                result += ", and is killed"
        else:
            # if we don't recognize this action, pass it up the chain
            result = super().accept_action(action, actor, context)
        return result

    def set_context(self, context):
        """
        establish the local context
        """
        self.context = context

    def take_action(self, action, target):
        """
        Initiate an action against a target
        @param action (GameAction): the action to be initiated
        @param target (GameObject): the target of the action
        @return (string): result of the action
        """
        result = action.act(self, target, self.context)
        return result


if __name__ == "__main__":

    village = GameContext("Snaefelness", "village on north side of island")
    local = GameContext("town square", "center of village", village)

    actor = GameActor("GameActor 1", "test initiator")
    actor.set_context(local)

    gizmo = GameObject("Gizmo 1", "test non-weapon")
    non_action = GameAction(gizmo, "DO SOMETHING")

    weapon = GameObject("Weapon 2", "test weapon")
    attack = GameAction(weapon, "ATTACK")
    attack.set("damage", 10)

    target = GameActor("GameActor 2", "test target")
    target.set("hp", 16)

    result = actor.take_action(non_action, target)
    print("{} uses {} to {} to {}\n    {}"
          .format(actor.name, gizmo.name,
                  non_action.verb, target.name, result))

    result = actor.take_action(attack, target)
    print("{} uses {} to {} to {}\n    {}"
          .format(actor.name, weapon.name, attack.verb, target.name, result))

    result = actor.take_action(attack, target)
    print("{} uses {} to {} to {}\n    {}"
          .format(actor.name, weapon.name, attack.verb, target.name, result))
