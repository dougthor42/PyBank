# -*- coding: utf-8 -*-
"""
Compares various levenshtein packages

Created on Fri Jun  5 11:42:33 2015

@author: dthor
"""

import timeit
from fuzzywuzzy import fuzz
from Levenshtein import _levenshtein as lev1
from pyxdameraulevenshtein import damerau_levenshtein_distance as lev2
import pandas as pd
import random
import string
import jellyfish as jelly
import ast



COUNT = 1000
REPEAT = 10

a = "qwertyuiop"
b = "qwertyuiop"


FUZZ_CMD = "fuzz.ratio('{}', '{}')"
FUZZ_SETUP = "from fuzzywuzzy import fuzz"

LEV1_CMD = "lev1.distance('{}', '{}')"
LEV1_SETUP = "from Levenshtein import _levenshtein as lev1"

LEV2_CMD = "lev2('{}', '{}')"
LEV2_SETUP = "from pyxdameraulevenshtein import damerau_levenshtein_distance as lev2"

JELLY_CMD = "jelly.damerau_levenshtein_distance('{}', '{}')"
JELLY_SETUP = "import jellyfish as jelly"


def run(cmd, setup, name, result):
    name = name + ":"
    c = timeit.repeat(cmd, setup, number=COUNT, repeat=REPEAT)
    c = pd.Series(c)
    time_ms = c.mean() * 1000
    print("  {: <21s}  {: <6.8F}ms  {}".format(name, time_ms, result))
#    print(c.describe())


def run_list(items, test_name, a, b):
    for (cmd, setup, algorithm_name) in items:
        cmd = cmd.format(a, b)
        result = eval(cmd)      # Evil! but oh well.
        run(cmd, setup, algorithm_name, result)


def main(name, a, b):
    """
    """
    print()
    print(name)
    print("-" * len(name))
    print("  `{}`".format(a))
    print("  `{}`".format(b))
    print()
    print("  {: <21s}  Avg / repeat  Result".format("Name"))
    print("  {: <21s}  ------------  ------".format("----"))

    items = [(FUZZ_CMD, FUZZ_SETUP, "FuzzyWuzzy (% same)"),
             (LEV1_CMD, LEV1_SETUP, "Levenshtein"),
             (LEV2_CMD, LEV2_SETUP, "Damerau-Levenshtein"),
             (JELLY_CMD, JELLY_SETUP, "Jellyfish D-L"),
             ]

    run_list(items, name, a, b)


if __name__ == "__main__":
    print("Running Levenshtein Comparisons")
    print("   {} iterations and {} repetitions".format(COUNT, REPEAT))

    rand1 = "".join(random.choice(string.ascii_letters) for _ in range(25))
    rand2 = "".join(random.choice(string.ascii_letters) for _ in range(25))


    tests = [("Same String", "abcdefghijklmnopqrstuvwxyz","abcdefghijklmnopqrstuvwxyz"),
             ("Off by 1", "abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxya"),
             ("25 random", rand1, rand2),
             ("transpose", "qwerty", "qwrety"),
             ("Diff lengths", "a short string", "a very long long long string"),
             ]

    for name, a, b in tests:
        main(name, a, b)

    items = [(FUZZ_CMD, FUZZ_SETUP, "FuzzyWuzzy (% same)"),
             (LEV1_CMD, LEV1_SETUP, "Levenshtein"),
             (LEV2_CMD, LEV2_SETUP, "Damerau-Levenshtein"),
             (JELLY_CMD, JELLY_SETUP, "Jellyfish D-L"),
             ]

    for (cmd, setup, algorithm_name) in items:
        print()
        print(algorithm_name)
        print(cmd)
        for l in [1, 2, 3, 5, 10, 15, 50, 100, 500, 1000, 10000]:
            rand1 = "".join(random.choice(string.ascii_letters) for _ in range(l))
            rand2 = "".join(random.choice(string.ascii_letters) for _ in range(l))
            num = 1000

            # Adjust number samples for the ones that take a long time.
            if l >= 100:
                num = 50
            elif l >= 1000:
                num = 5

            a = timeit.timeit(cmd.format(rand1, rand2), setup, number=num)
            print("StringLength: {}   Time (s): {}".format(l, a))
