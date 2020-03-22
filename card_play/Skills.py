from GameObject import GameObject
from GameAction import GameAction


class Skills(GameObject):
    """
    This is the base class for attribue based skills
    with a single attack, bonus and damage
    """

    """
    A GameActor's ability to execute a GameAction might be
    based on:
        a specific skill (who's name is the same as the verb)
        a character attribute
    In support of the latter case, this list associates verbs with
    character attributes.
    """
    skill_map = {
            "SEARCH": "perception",
            "LOCKPICK": "dexterity",
            "INVESTIGATE": "intelligence",
            "PERSUADE": "charisma"
            }

    def __init__(self, name, descr=None):
        """
        create a new Skills GameObject
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

        # if this verb has a skill associated with it, add it to the action
        for action in actions:
            # does the character have this as an explicit skill
            skill = actor.get(action.verb)
            if skill is not None:
                action.set("skill", skill)
                continue

            # is this action a function of an attribute
            if action.verb in self.skill_map.keys():
                attribute = self.skill_map[action.verb]
                value = actor.get(attribute)
                if value is not None:
                    action.set("skill", value)

        return actions
