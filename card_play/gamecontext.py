""" This module implements the GameContext class """
from gameobject import GameObject


class GameContext(GameObject):
    """
    A GameContext corresponds to a geographic location and is a collection
    of GameObjects, GameActors and state attributes.   They exist in
    higherarchical relationships (e.g. kingdom, village, buiding, room).
    """

    def __init__(self, name="context", descr=None, parent=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        super(GameContext, self).__init__(name, descr)
        self.parent = parent
        self.party = []
        self.npcs = []

    def get(self, attribute):
        """
        return the value of an attribute

        @param attribute: name of attribute to be fetched
        @return: (string) value (or none)

        differs from base class because calls follow chain of parents
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        elif self.parent is not None:
            return self.parent.get(attribute)
        return None

    def possible_actions(self, actor, context):
        """
        return a list of possible actions in this context

        @param actor: GameActor initiating the action
        @param context: GameContext for this action (should be "self")
        @return: list of possible GameActions
        """
        # get the list of actions for this context
        actions = super(GameContext, self).possible_actions(actor, context)
        return actions

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is happening
        @return: (string) description of the effect
        """

        # A locale can be searched, turning up concealed things.
        if action.verb == "SEARCH":
            found_stuff = False
            result = ""
            for thing in self.objects:
                concealment = thing.get("RESISTANCE.SEARCH")
                if concealment is not None and concealment > 0:
                    (success, descr) = thing.accept_action(action, actor,
                                                           context)
                    if success:
                        found_stuff = True
                    if result == "":
                        result = descr
                    else:
                        result += "\n    " + descr
            return(found_stuff, result)

        # if we don't recognize this action, pass it up the chain
        return super(GameContext, self).accept_action(action,
                                                      actor, context)

    def get_party(self):
        """
        @return: list of GameActors in the party
        """
        return self.party

    def add_member(self, member):
        """
        Add an player character to this context
        @param member: player GameActor
        """
        if member not in self.party:
            self.party.append(member)

    def get_npcs(self):
        """
        return a list of the NPCs in this context
        """
        return self.npcs

    def add_npc(self, npc):
        """
        Add an NPC to this context
        @param npc: the NPC GameActor to be added
        @return: list of (non-party) GameActors in the context
        """
        if npc not in self.npcs:
            self.npcs.append(npc)
