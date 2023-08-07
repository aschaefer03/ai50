from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

Rules = And(
    Biconditional(AKnight, Not(AKnave)), Biconditional(AKnave, Not(AKnight)),
    Biconditional(BKnight, Not(BKnave)), Biconditional(BKnave, Not(BKnight)),
    Biconditional(CKnight, Not(CKnave)), Biconditional(CKnave, Not(CKnight))
)


def a_said(statement):
    return And(Biconditional(AKnight, statement), Biconditional(AKnave, Not(statement)))


def b_said(statement):
    return And(Biconditional(BKnight, statement), Biconditional(BKnave, Not(statement)))


def c_said(statement):
    return And(Biconditional(CKnight, statement), Biconditional(CKnave, Not(statement)))


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Rules, a_said(And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Rules, a_said(And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Rules, a_said(Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    b_said(Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
aSayKnight = Symbol("A said 'I am a knight'")
aSayKnave = Symbol("A said 'I am a knave'")
Rule2 = And(Biconditional(aSayKnight, Not(aSayKnave)), Biconditional(aSayKnave, Not(aSayKnight)))
knowledge3 = And(
    Rules, Rule2, Or(And(a_said(AKnight), aSayKnight), And(a_said(AKnave), aSayKnave)), b_said(aSayKnave),
    b_said(CKnave), c_said(AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
