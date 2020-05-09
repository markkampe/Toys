""" This module implements the GameAction class """
from dice import Dice
from base import Base


class GameAction(Base):
    """
    A GameAction is an action possibility that is available to a GameActor.
    It has attributes that control its effects, and when its act() method
    is called, it delivers that action to the intended target.

    The most interetsting method is act(initiator, target, context)
    which informs the target to process the effects of the action.
    """
    def __init__(self, source, verb):
        """
        create a new GameAction
        @param source: GameObject instrument for the action
        @param verb: the name of the action
        """
        super(GameAction, self).__init__(verb)
        self.source = source
        self.verb = verb
        self.attributes = {}

    def __str__(self):
        """
        return a string representation of this action
        """
        if "ATTACK" in self.verb:
            return "{} (ACCURACY={}%, DAMAGE={})".\
                format(self.verb, self.get("ACCURACY"), self.get("DAMAGE"))
        return "{} (POWER={}%, STACKS={})".\
            format(self.verb, self.get("POWER"), self.get("STACKS"))

    def accuracy(self, initiator):
        """
        Compute the accuracy of this attack
        @param initator: GameActor who is initiating the attack
        @return: (int) probability of hitting
        """
        # get base accuracy from the action
        acc = self.get("ACCURACY")
        if acc is None:
            w_accuracy = 0
        else:
            w_accuracy = int(acc)

        # get the initiator base accuracy
        acc = initiator.get("ACCURACY")
        if acc is None:
            i_accuracy = 0
        else:
            i_accuracy = int(acc)

        # add any initiator sub-type accuracy
        if 'ATTACK.' in self.verb:
            sub_type = self.verb.split('.')[1]
            if sub_type is not None:
                acc = initiator.get("ACCURACY." + sub_type)
                if acc is not None:
                    i_accuracy += int(acc)

        return w_accuracy + i_accuracy

    def damage(self, initiator):
        """
        compute the damage from this attack
        @param initator: GameActor who is initiating the attack
        @return: (int) total damage
        """
        # get the basic action damage formula and roll it
        dmg = self.get("DAMAGE")
        if dmg is None:
            w_damage = 0
        else:
            dice = Dice(dmg)
            w_damage = dice.roll()

        # get initiator base damage formula and roll it
        dmg = initiator.get("DAMAGE")
        if dmg is None:
            i_damage = 0
        else:
            dice = Dice(dmg)
            i_damage = dice.roll()

        # add any initiator sub-type damage
        if 'ATTACK.' in self.verb:
            sub_type = self.verb.split('.')[1]
            if sub_type is not None:
                dmg = initiator.get("DAMAGE." + sub_type)
                if dmg is not None:
                    dice = Dice(dmg)
                    i_damage += dice.roll()

        return w_damage + i_damage

    def power(self, initiator):
        """
        Compute the power with which this condition is being sent
        @param initator: GameActor who is sending the condition
        @return: (int) total probability of hitting
        """
        # figure out the condition type and subtype
        if '.' in self.verb:
            base_type = self.verb.split('.')[0]
            sub_type = self.verb.split('.')[1]
        else:
            base_type = self.verb
            sub_type = None

        # get base power from the action
        pwr = self.get("POWER")
        if pwr is None:
            power = 0
        else:
            power = int(pwr)

        # add the initiator base power
        pwr = initiator.get("POWER." + base_type)
        if pwr is not None:
            power += int(pwr)

        # add any initiator sub-type accuracy
        if sub_type is not None:
            pwr = initiator.get("POWER." + base_type + '.' + sub_type)
            if pwr is not None:
                power += int(pwr)

        return power

    def stacks(self, initiator):
        """
        Compute the number of stacks to be sent
        @param initator: GameActor who is sending the condition
        @return: (int) total number of stacks
        """
        # figure out the condition type and subtype
        if '.' in self.verb:
            base_type = self.verb.split('.')[0]
            sub_type = self.verb.split('.')[1]
        else:
            base_type = self.verb
            sub_type = None

        # get base stacks from the action
        stx = self.get("STACKS")
        if stx is None:
            stacks = 0
        else:
            dice = Dice(stx)
            stacks = dice.roll()

        # add the initiator base power
        stx = initiator.get("STACKS." + base_type)
        if stx is not None:
            dice = Dice(stx)
            stacks += dice.roll()

        # add any initiator sub-type accuracy
        if sub_type is not None:
            stx = initiator.get("STACKS." + base_type + '.' + sub_type)
            if stx is not None:
                dice = Dice(stx)
                stacks += dice.roll()

        return stacks

    def act(self, initiator, target, context):
        """
        Initiate an action against a target
        @param initiator: GameActor initiating the action
        @param target: GameObject target of the action
        @param context: GameContext in which this is happening
        @return: (string) result of the action

        The act() method knows how to process attacks and
        simple actions that require saves and produce
        conditions.  Any action requiring more complex
        processing (before calling the target) requires
        the implementation of a sub-class.
        """
        if "ATTACK" in self.verb:
            # ATTACK actions are likely to have the following properties:
            #    ACCURACY    ... a number to be added to a D100 success role
            #    DAMAGE      ... a (Dice) damage description
            #
            # the initiator may have his/hir own ACCURACY/DAMAGE adjustments
            #
            # by the time they are passed to the target, they will have:
            #    TO_HIT      ... the to-hit role (including all bonuses)
            #    HIT_POINTS  ... a number of hit points

            self.set("TO_HIT", 100 + self.accuracy(initiator))
            self.set("HIT_POINTS", self.damage(initiator))
        else:
            # CONDITION actions are likely to have the following properties:
            #   POWER   ... a number to be added to a D100 success roll
            #   STACKS  ... a (Dice) description of stacks to send
            #
            # the initiator may have his/her own POWER/STACKS adjustments
            #
            # by the time they are passed to the target, they will have:
            #     TO_HIT  ... the to-hit role (including all bonuses)
            #     TOTAL   ... the number of stacks are being sent
            self.set("TO_HIT", 100 + self.power(initiator))
            self.set("TOTAL", self.stacks(initiator))

        # and pass it on to the target
        return target.accept_action(self, initiator, context)


class TestRecipient(Base):
    """
    a minimal object that can receive, and report on actions
    """

    def accept_action(self, action, actor, context):
        """
        report on the action we received
        @param action: GameAction being sent
        @param actor: GameActor who set it
        @param context: GameContext in which this happened
        """
        if "ATTACK" in action.verb:
            return "{} receives {} (TO_HIT={}, DAMAGE={}) from {} in {}". \
                   format(self, action.verb,
                          action.get("TO_HIT"), action.get("DAMAGE"),
                          actor, context)
        return "{} receives {} (TO_HIT={}, STACKS={}) from {} in {}". \
               format(self, action.verb,
                      action.get("TO_HIT"), action.get("STACKS"),
                      actor, context)


def base_attacks():
    """
    GameAction test cases:
      TO_HIT and DAMAGE computations for base ATTACKs
    """

    # create a victim and context
    victim = TestRecipient("victim")
    context = Base("unit-test")

    # create an artifact with actions
    artifact = Base("test-case")

    # test attacks from an un-skilled attacker (base values)
    lame = Base("lame attacker")        # attacker w/no skills
    # pylint: disable=bad-whitespace
    lame_attacks = [
        # verb,       accuracy, damage, exp hit, exp dmg
        ("ATTACK",        None,    "1",     100,       1),
        ("ATTACK.ten",      10,   "10",     110,      10),
        ("ATTACK.twenty",   20,   "20",     120,      20),
        ("ATTACK.thirty",   30,   "30",     130,      30)]

    for (verb, accuracy, damage, exp_hit, exp_dmg) in lame_attacks:
        action = GameAction(artifact, verb)
        if accuracy is not None:
            action.set("ACCURACY", accuracy)
        action.set("DAMAGE", damage)
        result = action.act(lame, victim, context)

        # see if the action contained the expected values
        to_hit = action.get("TO_HIT")
        hit_points = action.get("HIT_POINTS")
        if action.verb == verb and to_hit == exp_hit and hit_points == exp_dmg:
            print(result + " ... CORRECT")
        else:
            print(result)
            assert action.verb == verb, \
                "incorrect action verb: expected " + verb
            assert action.get("TO_HIT") == exp_hit, \
                "incorrect base accuracy: expected " + str(exp_hit)
            assert action.get("HIT_POINTS") == exp_dmg, \
                "incorrect base damage: expected " + str(exp_dmg)

    print()


def subtype_attacks():
    """
    GameAction test cases:
      TO_HIT and DAMAGE computations for sub-type attacks
    """

    # create a victim and context
    victim = TestRecipient("victim")
    context = Base("unit-test")

    # create an artifact with actions
    artifact = Base("test-case")

    # test attacks from a skilled attacker, w/bonus values
    skilled = Base("skilled attacker")  # attacker w/many skills
    skilled.set("ACCURACY", 10)
    skilled.set("DAMAGE", "10")
    skilled.set("ACCURACY.twenty", 20)
    skilled.set("DAMAGE.twenty", "20")
    skilled.set("ACCURACY.thirty", 30)
    skilled.set("DAMAGE.thirty", "30")

    # pylint: disable=bad-whitespace
    skilled_attacks = [
        # verb,       accuracy, damage, exp hit, exp dmg
        ("ATTACK",        None,    "1",     110,      11),
        ("ATTACK.ten",      10,   "10",     120,      20),
        ("ATTACK.twenty",   20,   "20",     150,      50),
        ("ATTACK.thirty",   30,   "30",     170,      70)]

    for (verb, accuracy, damage, exp_hit, exp_dmg) in skilled_attacks:
        action = GameAction(artifact, verb)
        if accuracy is not None:
            action.set("ACCURACY", accuracy)
        action.set("DAMAGE", damage)
        result = action.act(skilled, victim, context)

        # see if the action contained the expected values
        to_hit = action.get("TO_HIT")
        hit_points = action.get("HIT_POINTS")
        if action.verb == verb and to_hit == exp_hit and hit_points == exp_dmg:
            print(result + " ... CORRECT")
        else:
            print(result)
            assert action.verb == verb, \
                "incorrect action verb: expected " + verb
            assert action.get("TO_HIT") == exp_hit, \
                "incorrect base accuracy: expected " + str(exp_hit)
            assert action.get("HIT_POINTS") == exp_dmg, \
                "incorrect base damage: expected " + str(exp_dmg)
    print()


def base_conditions():
    """
    GameAction test cases:
      TO_HIT and STACKS computations for base CONDITIONS
    """

    # create a victim and context
    victim = TestRecipient("victim")
    context = Base("unit-test")

    # create an artifact with actions
    artifact = Base("test-case")

    # test attacks from an un-skilled attacker (base values)
    lame = Base("unskilled sender")      # sender w/no skills
    # pylint: disable=bad-whitespace
    lame_attacks = [
        # verb,       power, stacks, exp hit, exp stx
        ("MENTAL",     None,    "1",     100,       1),
        ("MENTAL.X",     10,   "10",     110,      10),
        ("MENTAL.Y",     20,   "20",     120,      20),
        ("MENTAL.Z",     30,   "30",     130,      30)]

    for (verb, power, stacks, exp_hit, exp_stx) in lame_attacks:
        action = GameAction(artifact, verb)
        if power is not None:
            action.set("POWER", power)
        action.set("STACKS", stacks)
        result = action.act(lame, victim, context)

        # see if the action contained the expected values
        to_hit = action.get("TO_HIT")
        stacks = action.get("TOTAL")
        if action.verb == verb and to_hit == exp_hit and stacks == exp_stx:
            print(result + " ... CORRECT")
        else:
            print(result)
            assert action.verb == verb, \
                "incorrect action verb: expected " + verb
            assert action.get("TO_HIT") == exp_hit, \
                "incorrect base accuracy: expected " + str(exp_hit)
            assert action.get("TOTAL") == exp_stx, \
                "incorrect base stacks: expected " + str(exp_stx)
    print()


def subtype_conditions():
    """
    GameAction test cases:
      TO_HIT and TOTAL computations for sub-type attacks
    """

    # create a victim and context
    victim = TestRecipient("victim")
    context = Base("unit-test")

    # create an artifact with actions
    artifact = Base("test-case")

    # test attacks from a skilled attacker, w/bonus values
    skilled = Base("skilled sender")  # sender w/many skills
    skilled.set("POWER.MENTAL", 10)
    skilled.set("STACKS.MENTAL", "10")
    skilled.set("POWER.MENTAL.Y", 20)
    skilled.set("STACKS.MENTAL.Y", "20")
    skilled.set("POWER.MENTAL.Z", 30)
    skilled.set("STACKS.MENTAL.Z", "30")

    # pylint: disable=bad-whitespace
    skilled_attacks = [
        # verb,       power, stacks, exp hit, exp stx
        ("MENTAL",     None,    "1",     110,      11),
        ("MENTAL.X",     10,   "10",     120,      20),
        ("MENTAL.Y",     20,   "20",     150,      50),
        ("MENTAL.Z",     30,   "30",     170,      70)]

    for (verb, power, stacks, exp_hit, exp_stx) in skilled_attacks:
        action = GameAction(artifact, verb)
        if power is not None:
            action.set("POWER", power)
        action.set("STACKS", stacks)
        result = action.act(skilled, victim, context)

        # see if the action contained the expected values
        to_hit = action.get("TO_HIT")
        stacks = action.get("TOTAL")
        if action.verb == verb and to_hit == exp_hit and stacks == exp_stx:
            print(result + " ... CORRECT")
        else:
            print(result)
            assert action.verb == verb, \
                "incorrect action verb: expected " + verb
            assert action.get("TO_HIT") == exp_hit, \
                "incorrect base accuracy: expected " + str(exp_hit)
            assert action.get("TOTAL") == exp_stx, \
                "incorrect base stacks: expected " + str(exp_stx)
    print()


if __name__ == "__main__":
    base_attacks()
    subtype_attacks()
    base_conditions()
    subtype_conditions()
    print("All GameAction test cases passed")
