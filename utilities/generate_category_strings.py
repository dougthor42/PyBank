# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 22:47:34 2015

@author: dthor
"""
import types


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


def trampoline(generator, *args, **kwargs):
    """
    See http://www.usrsb.in/blog/blog/2012/08/12/bouncing-pythons-generators-with-a-trampoline/

    1. This technique only works for tail-recursive functions. The recursive
       call *must* be the last thing the function does.
    2. The translation to a trampolined generator is easy! Just turn the
       return statements into yield expression.
    3. Although this will protect your stack, creating a generator for
       each call is probably slow.
    """
    g = generator(*args, **kwargs)
    while isinstance(g, types.GeneratorType):
        g = next(g)
    return g


def build_category_strings(cat_list,
                           delimiter=".",
                           parent_item=None,
                           sent_str=None,
                           retval=None,
                           ):
    """
    Recursively concatenates categories together and returns a list of them.

    This function requires:
        1) a single root item with parent = 0
        2) primary keys to be 1-indexed

    Parameters:
    -----------
    cat_list : list of (id, name, parent) tuples
        The data to create strings from. This must be a list (or list-like)
        of (id, name, parent_id) tuples (or list-like).

    delimiter: string
        The string to put between each item.

    parent_item :
        Only used during recursion.

    sent_str :
        Only used during recursion

    retlist :
        Only used during recursion.

    Returns:
    --------
    retlist : list of strings
        A list of dot-notation strings.

    Examples:
    ---------

    >>> data = [(1, "A", 0), (2, "B", 1), (3, "C", 1), (4, "D", 2),
    ...         (5, "E", 2), (6, "F", 3), (7, "G", 2), (8, "H", 6),
    ...         ]
    >>> build_category_strings(data)
    ['A', 'A.B', 'A.B.D', 'A.B.E', 'A.B.G', 'A.C', 'A.C.F', 'A.C.F.H']

    """
    if retval is None:
        retval = []

    if parent_item is None:
        parent_item = cat_list[0]
        retval.append(parent_item[1])

    parent_id = parent_item[0]
    parent_name = parent_item[1]

    if sent_str is None:
        sent_str = parent_name

    # Find the children
    children = [_x for _x in cat_list if _x[2] == parent_id]

    if len(children) == 0:
        # base case (no children), so we return the full path
        return ["{}{}{}".format(sent_str, delimiter, parent_name)]
    else:
        # children exist so we need to iterate through them.
        for child in children:
            # create an incomplete path string and add it to our return value
            str_to_send = "{}{}{}".format(sent_str, delimiter, child[1])
            retval.append(str_to_send)
            # recurse using the current child as the new parent
            build_category_strings(cat_list,
                                   delimiter,
                                   child,
                                   str_to_send,
                                   retval)
        return retval


if __name__ == "__main__":
#    data = [(1, "A", 0), (2, "B", 1), (3, "C", 1), (4, "D", 2),
#            (5, "E", 2), (6, "F", 3), (7, "G", 2), (8, "H", 6),
#            ]

#    print(generate_category_strings(data))
#    print(generate_category_strings(data, ":"))

    trampoline(countdown_gen, 5)