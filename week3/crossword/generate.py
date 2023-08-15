import sys
from queue import Queue

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.domains[var].copy():
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        change = False
        if self.crossword.overlaps[x, y] is None:
            return change
        (x_int, y_int) = self.crossword.overlaps[x, y]
        for word in self.domains[x].copy():
            no_match = True
            for word_y in self.domains[y]:
                if word[x_int] == word_y[y_int] and word != word_y:
                    no_match = False
                    break
            if no_match:
                self.domains[x].remove(word)
                change = True
        return change

    def initialize_queue(self, queue):
        for var in self.crossword.variables:
            for var2 in self.crossword.neighbors(var):
                queue.put((var, var2))

    def initialize_queue_from_arcs(self, queue, arcs):
        for pair in arcs:
            queue.put(pair)

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = Queue()
        if arcs is None:
            self.initialize_queue(queue)
        else:
            self.initialize_queue_from_arcs(queue, arcs)
        if not queue.empty():
            (x, y) = queue.get()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.put((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        keys = list(assignment.keys())
        for x in keys:
            if len(assignment[x]) != x.length:
                return False
            for y in self.crossword.neighbors(x):
                (x_int, y_int) = self.crossword.overlaps[x, y]
                if assignment[x][x_int] != assignment[y][y_int]:
                    return False
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if assignment[keys[i]] == assignment[keys[j]]:
                    return False
        return True

    def overlap_count(self, var, assignment, word):
        c = 0
        for var2 in self.crossword.neighbors(var):
            if var2 in assignment.keys():
                continue
            (v_int, v2_int) = self.crossword.overlaps[var, var2]
            for word2 in self.domains[var2]:
                if word2[v2_int] != word[v_int]:
                    c += 1
        return c

    def word_equality_count(self, var, assignment, word):
        c = 0
        for var3 in self.crossword.variables:
            if var3 in assignment.keys() or var3 == var:
                continue
            for word3 in self.domains[var3]:
                if word3 == word:
                    c += 1
        return c

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ordered_tuples = []
        for word in self.domains[var]:
            c = 0
            c += self.overlap_count(var, assignment, word)
            c += self.word_equality_count(var, assignment, word)
            ordered_tuples.append((word, c))
        ordered_tuples.sort(key=lambda x: x[1])
        ordered_domain = [None]*len(ordered_tuples)
        for i in range(len(ordered_tuples)):
            ordered_domain[i] = ordered_tuples[i][0]
        return ordered_domain

    def lowest_vals(self, tuples):
        choices = []
        t_min = float('inf')
        for t in tuples:
            if t[1] < t_min:
                choices = [t[0]]
                t_min = t[1]
            elif t[1] == t_min:
                choices.append(t[0])
        return choices

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        tuples = []
        for var in self.crossword.variables:
            if var not in assignment.keys():
                tuples.append((var, len(self.domains[var])))
        choices = self.lowest_vals(tuples)
        if len(choices) == 1:
            return choices[0]
        tuples = []
        for choice in choices:
            tuples.append((choice, 0 - len(self.crossword.neighbors(choice))))
        return self.lowest_vals(tuples)[0]

    def word_consistent(self, var, word, assignment):
        if var.length != len(word):
            return False
        neighbors = self.crossword.neighbors(var)
        for k, v in assignment.items():
            if word == v:
                return False
            if k in neighbors:
                (var_int, k_int) = self.crossword.overlaps[var, k]
                if word[var_int] != v[k_int]:
                    return False
        return True

    def add_inferences(self, var, assignment):
        arcs = []
        for var2 in self.crossword.neighbors(var):
            arcs.append((var2, var))
        if not self.ac3(arcs):
            return None
        new_assignments = []
        for var3 in self.crossword.neighbors(var):
            var3_words = self.domains[var3]
            if len(var3_words) == 1 and var3 not in assignment.keys():
                new_assignments.append(var3)
                assignment[var3] = var3_words.pop()
        return new_assignments

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for word in self.domains[var].copy():
            if self.word_consistent(var, word, assignment):
                assignment[var] = word
                inf_changes = self.add_inferences(var, assignment)
                if inf_changes is None:
                    return None
            # print(assignment)
            #     self.print(assignment)
            #     print("\n")
            #     for v in self.crossword.variables:
            #         print(v, "-", self.domains[v])
            #     print("\n\n")
                result = self.backtrack(assignment)
                # print(assignment)
                if result is not None:
                    return assignment
                if result is None:
                    del assignment[var]
                    for var2 in inf_changes:
                        assignment.pop(var2)
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
