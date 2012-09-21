# encoding: utf-8
from datetime import date
from sqlalchemy.exc import IntegrityError
from palis import db
from palis.models import User, Paper, PaperDispatchEntity


if True:
    db.create_all()

    admin = User(u'admin', u'123456')
    johann = User(u'johann', u'wolfgang')
    goethe = User(u'goethe', u'von von')
    shell = User(u'shell', u'123456')
    tty = User(u'tty', u'123456')

    try:
        db.session.add(goethe)
        db.session.add(admin)
        db.session.add(johann)
        db.session.add(tty)
        db.session.add(shell)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()

    paper1 = Paper(u'张章', u'哈哈', u'zhang_zhang_ha-ha.pdf', date(2012, 6, 2), admin._id)
    paper2 = Paper(u'李丽', u'哼哼', u'Learning.GNU.Emacs.3rd.edition.pdf', date(2012, 6, 2), johann._id)
    paper3 = Paper(u'Andrew S. Tanenbaum', u'Modern Operating Systems',
                   u'andrew_s_tanenbaum_Modern-Operating-Systems.pdf', date(2012, 6, 5), admin._id)

    try:
        db.session.add(paper1)
        db.session.add(paper2)
        db.session.add(paper3)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()

    print admin._id, johann._id, goethe._id

    pde1 = PaperDispatchEntity(admin._id, johann._id, paper1._id, 0x1, date(2012, 6, 12))
    pde2 = PaperDispatchEntity(admin._id, goethe._id, paper1._id, 0x1, date(2012, 6, 12))
    pde3 = PaperDispatchEntity(admin._id, johann._id, paper2._id, 0x1, date(2012, 6, 15))
    pde4 = PaperDispatchEntity(admin._id, goethe._id, paper2._id, 0x1, date(2012, 6, 15))
    pde5 = PaperDispatchEntity(goethe._id, johann._id, paper3._id, 0x1, date(2012, 6, 17))

    print pde1
    print pde2
    print pde3
    print pde4
    print pde5

    try:
        db.session.add(pde1)
        db.session.add(pde2)
        db.session.add(pde3)
        db.session.add(pde4)
        db.session.add(pde5)
        db.session.commit()
    except IntegrityError as err:
        print err
        db.session.rollback()



