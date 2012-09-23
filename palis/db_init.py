# encoding: utf-8
from sqlalchemy.exc import IntegrityError
from palis import db
from palis.models import User


def run():
    db.create_all()

    admin = User(u'admin', u'123456')
    test_user = User(u'test_user', u'123456')

    try:
        db.session.add(admin)
        db.session.add(test_user)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()

    print 'database initialized with admin and test_user'

