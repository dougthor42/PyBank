# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 22:47:34 2015

@author: dthor
"""

# See http://www.usrsb.in/blog/blog/2012/08/12/bouncing-pythons
#             -generators-with-a-trampoline/

# 1. This technique only works for tail-recursive functions. The recursive
#    call *must* be the last thing the function does.
# 2. The translation to a trampolined generator is easy! Just turn the
#    return statements into yield expression.
# 3. Although this will protect your stack, creating a generator for
#    each call is probably slow.

def countdown(start):
    print(start)
    if start == 0:
        return 0
    else:
        return countdown(start - 1)


def countdown_gen(start):
    print(start)
    if start == 0:
        yield 0
    else:
        yield countdown_gen(start - 1)


import types
def trampoline(generator, *args, **kwargs):
    g = generator(*args, **kwargs)
    while isinstance(g, types.GeneratorType):
        g = next(g)
    return g


if __name__ == "__main__":
#    data = [(1, "A", 0), (2, "B", 1), (3, "C", 1), (4, "D", 2),
#            (5, "E", 2), (6, "F", 3), (7, "G", 2), (8, "H", 6),
#            ]

#    print(generate_category_strings(data))
#    print(generate_category_strings(data, ":"))

    trampoline(countdown_gen, 5)