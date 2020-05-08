""" This module implements the GameContext class """
from random import randint
from gameobject import GameObject


class GameContext(GameObject):
    """
    A GameContext corresponds to a geographic location and is a collection
    of GameObjects, GameActors and state attributes.   They exist in
    higherarchical relationships (e.g. kingdom, village, buiding, room).
    """

    # skills that might be applicable in any context
    # TODO search no longer has a mapped save
    skill_map = {
        "SEARCH": "perception"
        }

    def __init__(self, name, descr=None, parent=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        super(GameContext, self).__init__(name, descr)
        self.parent = parent
        self.objects = []
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

    def get_objects(self):
        """
        @return: list of GameOjects in this context
        """
        visible = []
        for thing in self.objects:
            concealed = thing.get("concealment")
            if concealed is None or concealed == 0:
                visible.append(thing)
        return visible

    def add_object(self, item):
        """
        add another object to this context
        """
        if item not in self.objects:
            self.objects.append(item)

    def possible_actions(self, actor, context):
        """
        return a list of possible actions in this context

        @param actor: GameActor initiating the action
        @param context: GameContext for this action (should be "self")
        @return: list of possible GameActions
        """
        # get the list of actions for this context
        actions = super(GameContext, self).possible_actions(actor, context)

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

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action: GameAction being performed
        @param actor: GameActor initiating the action
        @param context: GameContext in which the action is happening
        @return: (string) description of the effect
        """

        # A locale can be searched, turning up concealed things.
        # a Search action will have a "skill" attribute, indicating
        # the searcher's skills at searching.
        if action.verb == "SEARCH":
            ability = action.get("skill")
            if ability is None:
                ability = 0
            found = None
            for thing in self.objects:
                concealment = thing.get("concealment")
                if concealment is not None and concealment > 0:
                    roll = randint(1, 100)
                    if roll + ability > concealment:
                        if found is None:
                            found = thing.name
                        else:
                            found += ", " + thing.name
                        thing.set("concealment", 0)

            if found is None:
                result = "You found nothing"
            else:
                result = "You found " + found
        else:
            # if we don't recognize this action, pass it up the chain
            result = super(GameContext, self).accept_action(action,
                                                            actor, context)
        return result

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
