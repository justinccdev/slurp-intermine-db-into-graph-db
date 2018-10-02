def print_selections_counts(selections):
    """
    Print the current selections as feedback.
    :param selections:
    :return:
    """
    count = 0
    for referenced_class in filter(lambda c: len(selections[c]) > 0, selections.keys()):
        n = len(selections[referenced_class])
        count += n
        print('For %s got %d selections' % (referenced_class, n))

    print('Got %d total selections' % count)