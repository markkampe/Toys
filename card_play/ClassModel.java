/**
 * @hidden
 *		python data type with no Java analog
 */
class Dict {}

/**
 * @opt constructors
 * @opt attributes
 * @opt operations
 * @opt types
 */
class GameObject {
	String name;
	String description;
	Dict attributes;

	GameObject(String name, String description) {};
    String get(String attribute) {};
    void set(String attribute, String value) {};
    String accept_action(GameAction action, GameActor actor, GameContext context) {};
    GameAction[] possible_actions(GameActor actor, GameContext context) {};
}

/**
 * @opt -constructors
 * @opt attributes
 * @opt operations
 * @opt types
 */
class GameActor extends GameObject {
	Dict make_conditions;
	Dict fail_conditions;

    void set_context(GameContext context) {};
    String take_action(GameAction action, GameActor target) {};
    String accept_action(GameAction action, GameActor actor, GameContext context) {};
}

/**
 * @opt -constructors
 * @opt -attributes
 * @opt operations
 * @opt types
 */
class Weapon extends GameObject {
    GameAction[] possible_actions(GameActor actor, GameContext context) {};
}

/**
 * @opt constructors
 * @opt operations
 * @opt types
 * @opt attributes
 */
class GameContext extends GameObject {
	GameContext parent;

	GameContext(String name, String description, GameContext parent) {};
    void add_object(GameObject item) {};
    GameObject[] get_objects() {};

    void add_member(GameActor member) {};
    GameActor[] get_party() {};

    void add_npc(GameActor npc) {};
    GameActor[] get_npcs() {};

    String accept_action(GameAction action, GameActor actor, GameContext context) {};
}

/**
 * @opt -constructors
 * @opt operations
 * @opt types
 * @opt attributes
 */
class Skills extends GameObject {
	Dict skill_map;

    GameAction[] possible_actions(GameActor actor, GameContext context) {};
}

/**
 * @opt constructors
 * @opt operations
 * @opt types
 * @opt attributes
 * @depend - - - Dice
 */
class GameAction {
	Dict saves;

	GameAction(GameObject source, String verb) {};
    String get(String attribute) {};
    void set(String attribute, String value) {};
    String act(GameActor initiator, GameObject target, GameContext context) {};
}

/**
 * @opt constructors
 * @opt operations
 * @opt types
 * @opt -attributes
 * @note Helper Class
 */
class Dice {
	Dice(String formula) {};
	int roll() {};
}
