class GameContext:

    name = None
    description = None
    parent = None
    attributes = {}
    objects = []
    party = []
    npcs = []

    def __init__(self, name, descr=None, parent=None):
        """
        create a new GameObject
        @param name(string): display name of this object
        @param descr(string): human description of this object
        """
        self.name = name
        self.description = descr
        self.parent = parent

    def get(self, attribute):
        """
        return the value of an attribute

        @param attribute(string): name of attribute to be fetched
        @return (string): value (or none)
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        elif parent is not None:
            return parent.get(attribute)
        else:
            return None

    def set(self, attribute, value):
        """
        set the value of an attribute

        @param attribute(string): name of attribute to be fetched
        @param value(string): value to be stored for that attribute
        """
        self.attributes[attribute] = value

    def get_objects(self):
        """
        @return: list of GameOjects in this context
        """
        return self.objects

    def add_object(self, item):
        if item not in objects:
            self.objects.append(item)

    def get_party(self):
        """
        @return: list of GameActors in the party
        """
        return self.party

    def add_member(self, member):
        if member not in party:
            self.party.append(member)

    def get_npcs(self):
        return self.npcs

    def add_npc(self, npc):
        """
        @return: list of (non-party) GameActors in the context
        """
        if npc not in npcs:
            self.npcs.append(npc)
