""" This module implements the Interaction class """
from gameobject import GameObject


class Interaction(GameObject):
    """
    An Interaction is a GameObject that returns interaction actions to a player
    """

    skill_map = {
        "PERSUADE": "charisma",
        "FLATTER": "charisma",
        "BEG": "disguise",
        "OUTRANK": "disguise",
        "INTIMIDATE": "disguise",
        "THREATEN": "sterngth"
        }

    # pylint: disable=unused-argument; I expect to need this in the future
    def __init__(self, name, npc, descr=None):
        """
        create a new Interaction GameObject
        @param name: name of the interactee
        @param npc: GameActor with whom we are interacting
        @param descr: human description of interactions
        """
        if descr is None:
            descr = "interaction"
        super(Interaction, self).__init__(name, descr)

        # crude list of standard interactions ... beef this up
        self.actions = []
        self.set("actions", "PURSUADE,FLATTER,OUTRANK,BEG,INTIMIDATE,THREATEN")

    def possible_actions(self, actor, context):
        """
        receive and process the effects of an action

        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is taken
        @return list of possible GameActions
        """
        # get my list of allowed interactions
        interactions = super(Interaction, self).possible_actions(actor,
                                                                 context)

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
