from datetime import date
from sqlalchemy.exc import IntegrityError
from palis import db
from palis.models import User, Paper, PaperDispatchEntity


if True:
    db.create_all()

    admin = User('admin', '123456')
    johann = User('johann', 'wolfgang')
    goethe = User('goethe', 'vonvon')

    try:
        db.session.add(goethe)
        db.session.add(admin)
        db.session.add(johann)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()

    paper1 = Paper('author1', 'title1', 'author1-title1.pdf', date(2012, 6, 2))
    paper2 = Paper('author1', 'title2', 'author1-title2.pdf', date(2012, 6, 2))
    paper3 = Paper('author2', 'title3', 'author2-title3.pdf', date(2012, 6, 5))

    try:
        db.session.add(paper1)
        db.session.add(paper2)
        db.session.add(paper3)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()

    pde1 = PaperDispatchEntity(1, 2, 1, 0x0, date(2012, 6, 12))
    pde2 = PaperDispatchEntity(1, 3, 1, 0x0, date(2012, 6, 12))
    pde3 = PaperDispatchEntity(3, 1, 2, 0x0, date(2012, 6, 15))

    try:
        db.session.add(pde1)
        db.session.add(pde2)
        db.session.add(pde3)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()



