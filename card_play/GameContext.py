from GameObject import GameObject


class GameContext(GameObject):

    def __init__(self, name, descr=None, parent=None):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        """
        super().__init__(name, descr)
        self.parent = parent
        self.objects = []
        self.party = []
        self.npcs = []

    def get(self, attribute):
        """
        return the value of an attribute

        @param attribute(string): name of attribute to be fetched
        @return (string): value (or none)

        differs from base class because calls follow chain of parents
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        elif parent is not None:
            return parent.get(attribute)
        else:
            return None

    def get_objects(self):
        """
        @return: list of GameOjects in this context
        """
        visible = []
        for thing in self.objects:
            hidden = thing.get("hidden")
            if hidden is None or hidden is not True:
                visible.append(thing)
        return visible

    def add_object(self, item):
        if item not in self.objects:
            self.objects.append(item)

    def accept_action(self, action, actor, context):
        """
        receive and process the effects of an action

        @param action (GameAction): the action being performed
        @param actor (GameActor): the actor initiating the action
        @param context(GameContext): the most local context
        @return (string): description of the effect
        """
        if action.verb == "SEARCH":
            found = None
            for thing in self.objects:
                if thing.get("hidden") is True:
                    if found is None:
                        found = thing.name
                    else:
                        found += ", " + thing.name
                    thing.set("hidden", None)

            if found is None:
                result = "You found nothing"
            else:
                result = "You found " + found
        else:
            # if we don't recognize this action, pass it up the chain
            result = super().accept_action(action, actor, context)
        return result

    def get_party(self):
        """
        @return: list of GameActors in the party
        """
        return self.party

    def add_member(self, member):
        if member not in self.party:
            self.party.append(member)

    def get_npcs(self):
        return self.npcs

    def add_npc(self, npc):
        """
        @return: list of (non-party) GameActors in the context
        """
        if npc not in self.npcs:
            self.npcs.append(npc)