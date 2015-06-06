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



COUNT = 1000
REPEAT = 10

a = "qwertyuiop"
b = "qwertyuiop"

def run(cmd, setup, name, result):
    name = name + ":"
    c = timeit.repeat(cmd, setup, number=COUNT, repeat=REPEAT)
    c = pd.Series(c)
    time_ms = c.mean() * 1000
    print("  {: <21s}  {: <6.8F}ms  {}".format(name, time_ms, result))
#    print(c.describe())

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

    # FuzzyWuzzy
    fuzz_cmd = "fuzz.ratio('{}', '{}')".format(a, b)
    fuzz_setup = "from fuzzywuzzy import fuzz"
    result = fuzz.ratio(a, b)
    run(fuzz_cmd, fuzz_setup, "FuzzyWuzzy", result)

    # Levenshtein
    lev1_cmd = "lev1.distance('{}', '{}')".format(a, b)
    lev1_setup = "from Levenshtein import _levenshtein as lev1"
    result = lev1.distance(a, b)
    run(lev1_cmd, lev1_setup, "Levenshtein", result)

    # Damerau-Levenshtein
    lev2_cmd = "lev2('{}', '{}')".format(a, b)
    lev2_setup = "from pyxdameraulevenshtein import damerau_levenshtein_distance as lev2"
    result = lev2(a, b)
    run(lev2_cmd, lev2_setup, "Damerau-Levenshtein", result)



if __name__ == "__main__":
    print("Running Levenshtein Comparisons")
    print("   {} iterations and {} repetitions".format(COUNT, REPEAT))

    rand1 = "".join(random.choice(string.ascii_letters) for _ in range(25))
    rand2 = "".join(random.choice(string.ascii_letters) for _ in range(25))


    tests = [("Same String", "abcdefghijklmnopqrstuvwxyz","abcdefghijklmnopqrstuvwxyz"),
             ("Off by 1", "abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxya"),
             ("25 random", rand1, rand2),
             ("transpose", "qwerty", "qwrety"),
             ("Diff lengths", "short string", "a very long long long string"),
             ]

    for name, a, b in tests:
        main(name, a, b)

    for l in [1, 2, 3, 5, 10, 15, 50, 100, 500, 1000, 10000]:
        rand1 = "".join(random.choice(string.ascii_letters) for _ in range(l))
        rand2 = "".join(random.choice(string.ascii_letters) for _ in range(l))
        cmd = "lev2('{}', '{}')".format(rand1, rand2)
        setup = "from pyxdameraulevenshtein import damerau_levenshtein_distance as lev2"
        if l > 100:
            num = 30
        else:
            num = 1000
        a = timeit.timeit(cmd, setup, number=num)
        print("{},{}".format(l, a))