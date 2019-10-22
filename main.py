#!/usr/bin/env python

import sys

family_tree = {}

def add_person(name, parents=None):
    global family_tree

    family_tree[name] = parents


def handle_E_query(args):
    global family_tree

    if args[0] not in family_tree:
        add_person(args[0])

    if args[1] not in family_tree:
        add_person(args[1])

    if len(args) == 3:
        # This should always be true, but just being safe
        if args[2] not in family_tree:
            add_person(args[2], parents=(args[0], args[1]))


def handle_X_query(args, degree=-1):
    print("...\n")


def handle_W_query(args, degree=-1):
    print("...\n")


def handle_query(query):
    args = query.rstrip().split(' ')

    query_type = args.pop(0)

    # Unrecognized query type
    if query_type not in ['E', 'X', 'W']:
        return

    n_args = len(args)
    degree = -1

    if query_type == 'X':
        # Too many/too few arguments
        if n_args != 3 and n_args != 4:
            return

        if n_args == 4:
            # Invalid degree
            try:
                degree = int(args.pop(2))
            except ValueError:
                return

        print(query.rstrip())
        handle_X_query(args, degree)

    elif query_type == 'W':
        if n_args != 2 and n_args != 3:
            return

        if n_args == 3:
            try:
                degree = int(args.pop(1))
            except ValueError:
                return

        print(query.rstrip())
        handle_W_query(args, degree)

    else: # E
        if n_args != 2 and n_args != 3:
            return
        
        handle_E_query(args)


if __name__ == "__main__":
    try:
        for line in sys.stdin:
            handle_query(line)
    except KeyboardInterrupt:
        print()

