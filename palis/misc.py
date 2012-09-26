from functools import partial
from flask import session, flash, redirect, url_for
from palis.models import PaperDispatchEntity, User

def gen_filename(paper, author):
    _ = lambda what: '_'.join(what.split(' '))
    paper = _(paper)
    author = _(author)

    return '-'.join((paper, author))


def need_login(as_admin=False):
    def wrapper(func):
        def _f(*args, **kwargs):
            if 'username' not in session:
                flash('You are not logged in')
                return redirect(url_for('login'))
            if as_admin:
                if session['username'] != 'admin':
                    flash('You are not authorized')
                    return redirect(url_for('login'))
            return func(*args, **kwargs)
        return _f
    return wrapper


def silent_on_not_iterable(func):
    def _f(sortable, *args, **kwargs):
        try:
            _ = 1 in sortable
            return func(sortable, *args, **kwargs)
        except TypeError:
            return ()
    return _f


@silent_on_not_iterable
def _sorted(sortable, attr, reverse=True):
    return sorted(sortable,
                  cmp=lambda x, y: cmp(getattr(x, attr, ''),
                                       getattr(y, attr, '')),
                  reverse=reverse)

sorted_paper_by_date = partial(_sorted, attr='upload_date')
sorted_dispatch_by_date = partial(_sorted, attr='dispatch_date')
sorted_user_by_name = partial(_sorted, attr='username', reverse=False)


if __name__ == '__main__':
    print sorted_dispatch_by_date(PaperDispatchEntity.query.all())
    print sorted_user_by_name(User.query.all())


