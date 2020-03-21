from GameObject import GameObject
from GameAction import GameAction


class Skills(GameObject):
    """
    This is the base class for attribue based skills
    with a single attack, bonus and damage
    """
    def __init__(self, name, descr=None):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        """
        if descr is None:
            descr = "character skills"
        super().__init__(name, descr)

    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (GameActions[]): list of possible actions
        """
        # get my list of allowed skill-based actions
        actions = super().possible_actions(actor, context)

        # figure out what skills apply wo which actions
        for action in actions:
            if 'SEARCH' in action.verb:
                perception = actor.get("perception")
                action.set("skill", 0 if perception is None else perception)

        return actions
