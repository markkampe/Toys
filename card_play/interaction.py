""" This module implements the Interaction class """
from gameobject import GameObject


class Interaction(GameObject):
    """
    An Interaction is a GameObject that returns a list of possible modes
    of interaction (e.g. with NPCs)
    """

    # TODO: improve list of interactions
    interactions = ["PURSUADE", "FLATTER", "BEG",
                    "OUTRANK", "INTIMIDATE", "THREATEN",
                    "CHEAT"]

    # pylint: disable=unused-argument; I expect to need this in the future
    def __init__(self, name, npc, descr=None):
        """
        create a new Interaction GameObject
        @param name: name of the interactee
        @param npc: GameActor with whom we are interacting
        @param descr: human description of interactions
        """
        if descr is None:
            descr = "interaction with " + npc.name
        super(Interaction, self).__init__(name, descr)

        actions = ""
        for action in self.interactions:
            if actions != "":
                actions += ","
            actions += "VERBAL." + action
        self.set("ACTIONS", actions)
