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
                     + "\n    {} HP: {} - {} = {}"\
                       .format(self.name, old_hp, damage, new_hp)
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
    """
    GameActor/GameAction test
        create a context and two (combat capable) actors
        create a gizmo with a harmless action
        use the gizmo to perform that action on a target
        create a weapon which can do damage
        use the weapon to attack until the target hp->0
    """

    # create a context
    village = GameContext("Snaefelness", "village on north side of island")
    local = GameContext("town square", "center of village", village)

    # create an initiator actor
    actor = GameActor("Actor", "test initiator")
    actor.set_context(local)
    actor.set("thac0", 10)

    # create a target actor
    target = GameActor("Target", "test target")
    target.set_context(local)
    target.set("ac", 1)
    target.set("hp", 16)

    # start with a non-action that will be punted by the base class
    gizmo = GameObject("Gizmo", "test non-weapon")
    non_action = GameAction(gizmo, "DO SOMETHING")
    result = actor.take_action(non_action, target)
    print("{} uses {} to {} to {}\n    {}"
          .format(actor.name, gizmo.name,
                  non_action.verb, target.name, result))
    print()

    # do attacks, that will be handled by the ATTACK action
    weapon = GameObject("Weapon", "test weapon")
    weapon.set("damage", 8)
    weapon.set("bonus", 2)
    attack = GameAction(weapon, "ATTACK")
    while target.get("hp") >= 1:
        result = actor.take_action(attack, target)
        print("{} uses {} to {} to {}\n    {}"
              .format(actor.name, weapon.name, attack.verb,
                      target.name, result))
        print()
