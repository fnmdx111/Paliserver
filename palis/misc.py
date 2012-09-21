
def gen_filename(paper, author):
    _ = lambda what: '_'.join(what.split(' '))
    paper = _(paper)
    author = _(author)

    return '-'.join((paper, author))


