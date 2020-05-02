""" this module implements the Skills class """
from gameobject import GameObject


class Skills(GameObject):
    """
    This is the base class for attribute based skills.

    The only value it adds (over the base GameObject) class is
    its ability to enhance possible_actions by figuring out what
    character skill or attribute might affect each action, and
    adding the appropriate bonuses.

    A GameActor's ability to execute a GameAction might be
    based on:
       - a specific skill (who's name is the same as the verb)
       - a character attribute
    In support of the latter case, this list associates verbs with
    character attributes.
    """
    skill_map = {
        "LOCKPICK": "dexterity",
        "INVESTIGATE": "intelligence",
        "PERSUADE": "charisma"
        }

    def __init__(self, name, descr=None):
        """
        create a new Skills GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        if descr is None:
            descr = "character skills"
        super(Skills, self).__init__(name, descr)

    def possible_actions(self, actor, context):
        """
        return a list of possible actions for this actor in this context

        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is being initiated
        @return: list of possible GameActions
        """
        # get my list of allowed skill-based actions
        actions = super(Skills, self).possible_actions(actor, context)

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
