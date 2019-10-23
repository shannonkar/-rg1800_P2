#!/usr/bin/env python

import sys


# Valid relations
relations = ["child", "sibling", "ancestor", "cousin", "unrelated"]


# Maps a name to a 2-tuple parents' names or None if person is a root node.
family_tree = {}


# Add a new person to the family tree specified parents or as root node.
#
# Parents should already be in tree or this will cause problems.
def add_person(name, parents=None):
    global family_tree

    family_tree[name] = parents


# Recursively get all ancestors of the specified person.
#
# Each ancestor name is mapped to a list of "degrees", which indicate the
# number of branches back that the ancestor appears in the query target's family
# tree.
#
# It's a list because inbreeding can cause an ancestor to have multiple degrees
# of relation to a descendant, e.g. father and great grandfather.
#
# Don't call this function directly.
# Call the higher-level get_ancestors function instead.
def _get_ancestors(person, degree=0):
    if person not in family_tree:
        return None

    ancestors = {}

    if family_tree[person] is not None:
        parent1, parent2 = family_tree[person]

        ancestors[parent1] = [degree]
        ancestors[parent2] = [degree]

        parent1_ancestors = _get_ancestors(parent1, degree + 1)
        parent2_ancestors = _get_ancestors(parent2, degree + 1)

        # If one parent is an ancestor of the other...
        # Ancestors might have multiple degrees of relation
        if parent2 in parent1_ancestors:
            # Add the other degrees for this ancestor
            ancestors[parent2] += parent1_ancestors[parent2]
            del parent1_ancestors[parent2]

        # Do the same for other parent
        if parent1 in parent2_ancestors:
            ancestors[parent1] += parent2_ancestors[parent1]
            del parent2_ancestors[parent1]

        # Remove duplicate degrees, to be safe
        ancestors[parent1] = list(set(ancestors[parent1]))
        ancestors[parent2] = list(set(ancestors[parent2]))

        # Now add the rest of the ancestors that weren't already present
        ancestors.update(parent1_ancestors)
        ancestors.update(parent2_ancestors)

    return ancestors


# Get all ancestors of the specified degree.
#
# Degree of -1 (default) means get all ancestors.
def get_ancestors(person, degree=-1):
    ancestor_degrees = _get_ancestors(person)
    return [ancestor for ancestor, degrees in ancestor_degrees.items() 
            if degree in degrees or degree == -1]


# Checks if 'ancestor' is an ancestor of 'descendant'.
#
# If degree is -1, simply checks for ancestry in general. Otherwise, checks for
# ancestry of the specified degree.
def is_ancestor(ancestor, descendant, degree=-1):
    return ancestor in get_ancestors(descendant, degree)


# Checks if person1 is unrelated to person2 (bijective so also vice versa).
def is_unrelated(person1, person2):
    ancestors1 = get_ancestors(person1)
    ancestors2 = get_ancestors(person2)
    return not (person2 in ancestors1 
                or person1 in ancestors2 
                or person1 == person2
                or set(ancestors1) & set(ancestors2)) 


# Get names of all family tree members unrelated to 'person'.
def get_unrelated(person):
    return [name for name in family_tree.keys() if is_unrelated(name, person)]


# Checks if 'child' is a child of 'parent'.
def is_child(child, parent):
    return False if family_tree[child] is None else parent in family_tree[child]


# Get names of all children.
def get_children(parent):
    return [name for name in family_tree.keys() if is_child(name, parent)]


# Checks if person1 is a sibling of person2 (& vice versa).
def is_sibling(person1, person2):
    return (person1 != person2 
            and (family_tree[person1] is not None 
                 and family_tree[person2] is not None)
            and set(family_tree[person1]) & set(family_tree[person2]))


# Get names of all siblings.
def get_siblings(person):
    return [name for name in family_tree.keys() if is_sibling(name, person)]


# Handles 'E' queries, which are the only ones that actually modify the tree.
#
# No output.
def handle_E_query(names):
    if names[0] not in family_tree:
        add_person(names[0])

    if names[1] not in family_tree:
        add_person(names[1])

    if len(names) == 3:
        # This should always be true, but just being safe
        if names[2] not in family_tree:
            add_person(names[2], parents=(names[0], names[1]))


# Handles 'X' queries, including output.
def handle_X_query(relation, names, degree=-1):
    # Invalid relation
    if relation not in relations:
        return

    if relation == "ancestor":
        result = "Yes" if is_ancestor(names[0], names[1]) else "No"
    elif relation == "unrelated":
        result = "Yes" if is_unrelated(names[0], names[1]) else "No"
    elif relation == "child":
        result = "Yes" if is_child(names[0], names[1]) else "No"
    elif relation == "sibling":
        result = "Yes" if is_sibling(names[0], names[1]) else "No"
    else:
        result = "..."

    print("{}\n".format(result))


# Handles 'W' queries, including output.
def handle_W_query(relation, name, degree=-1):
    if relation not in relations:
        return

    if relation == "ancestor":
        result = get_ancestors(name)
    elif relation == "unrelated":
        result = get_unrelated(name)
    elif relation == "child":
        result = get_children(name)
    elif relation == "sibling":
        result = get_siblings(name)
    else:
        result = ["..."]

    if result:
        for name in sorted(result):
            print(name)
    else:
        print("Nobody")
    print()


# Prepares input to be passed to query handling functions and performs some
# preliminary validation.
def handle_query(query):
    args = query.rstrip().split(' ')

    query_type = args.pop(0)

    # Unrecognized query type
    if query_type not in ['E', 'X', 'W']:
        return

    n_args = len(args)
    degree = -1

    if query_type == 'X':
        print(query.rstrip())

        if n_args == 3:
            relation = args.pop(1)

        elif n_args == 4:
            relation = args.pop(1)

            try:
                degree = int(args.pop(2))
            except ValueError:
                return

        # Too many/too few arguments
        else:
            return

        # Name not in family tree
        if any([arg not in family_tree for arg in args]):
            return

        handle_X_query(relation, args, degree)

    elif query_type == 'W':
        print(query.rstrip())

        if n_args == 2:
            relation = args.pop(0)

        elif n_args == 3:
            relation = args.pop(0)

            try:
                degree = int(args.pop(1))
            except ValueError:
                return

        else:
            return

        if args[0] not in family_tree:
            return

        handle_W_query(relation, args[0], degree)

    else: # E
        if n_args != 2 and n_args != 3:
            return
        
        handle_E_query(args)


# The 'main' program functionality. Simply processes each line of input from
# stdin as query.
if __name__ == "__main__":
    try:
        for line in sys.stdin:
            handle_query(line)
    except KeyboardInterrupt:
        print()

