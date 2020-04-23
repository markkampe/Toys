from GameObject import GameObject
from GameAction import GameAction


class Interaction(GameObject):
    """
    This is the base class for NPC interactions
    """

    skill_map = {
            "PERSUADE": "charisma",
            "FLATTER": "charisma",
            "BEG": "disguise",
            "OUTRANK": "disguise",
            "INTIMIDATE": "disguise",
            "THREATEN": "sterngth"
            }

    def __init__(self, name, npc, descr=None):
        """
        create a new GameObject
        @param name(string): name of the interactee
        @param npc(GameActor): actor with whom we are interacting
        @param descr(string): human description of interactions
        """
        if descr is None:
            descr = "interaction"
        super().__init__(name, descr)

        # crude list of standard interactions ... beef this up
        self.actions = []
        self.set("actions", "PURSUADE,FLATTER,OUTRANK,BEG,INTIMIDATE,THREATEN")

    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (GameActions[]): list of possible actions
        """
        # get my list of allowed interactions
        interactions = super().possible_actions(actor, context)

        # if this verb has a skill associated with it, add it to the action
        for action in interactions:
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

        return interactions
