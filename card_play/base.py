""" This module implements the base class that has only attributes """

class Base(object):
    """
    This is the base class for all other classes
    All it has is a name, description, and attributes.
    """

    def __init__(self, name, descr=None):
        """
        create a new GameObject
        @param name: display name of this object
        @param descr: human description of this object
        """
        self.name = name
        self.description = descr
        self.attributes = {}

    def get(self, attribute):
        """
        return: value of an attribute

        @param attribute: name of attribute to be fetched
        @return: (string) value (or none)
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        return None

    def set(self, attribute, value):
        """
        set the value of an attribute

        @param attribute: name of attribute to be fetched
        @param value: value to be stored for that attribute
        """
        self.attributes[attribute] = value


# pylint: disable=superfluous-parens; I prefer to consistently use print()
def main():
    """
    basic test GameObject test cases
    """

    describe = "simple get/set test object"
    go1 = Base("GameObject 1", describe)
    go2 = Base("GameObject 2")

    # new object has name, description, and nothing else
    print("Created 'Base 1', descr={}\n    got '{}', descr={}"
          .format(describe, go1.name, go1.description))
    assert (go1.name == "GameObject 1"), \
        "New object does not have assigned name"
    assert (go1.description == describe), \
        "New object does not have assigned description"

    # a new set correctly adds a value
    print("    before set(): get('attribute#1') -> {}"
          .format(go1.get("attribute#1")))
    assert (go1.get("attribute#1") is None), \
        "New object has attribute values before set"
    go1.set("attribute#1", "value1")
    print("    after set('attribute#1', 'value1'): get('attribute#1') -> '{}'"
          .format(go1.get("attribute#1")))
    assert (go1.get("attribute#1") == "value1"), \
        "set does not correctly set new value"

    # a second set correctly changes a value
    go1.set("attribute#1", "value2")
    print("    after set('attribute#1', 'value2'): get('attribute#1') -> '{}'"
          .format(go1.get("attribute#1")))
    assert (go1.get("attribute#1") == "value2"), \
        "set does not correctly change value"

    # description defaults to None
    print("Created 'GameObject, descr=None\n    got '{}', descr={}"
          .format(go2.name, go2.description))
    assert (go2.name == "GameObject 2"), \
        "New object does not have assigned name"
    assert (go2.description is None), \
        "New description does not default to None"

    print("\nAll test cases passed")


if __name__ == "__main__":
    main()
