from palis import db

class User(db.Model):
    __tablename__ = 'user'

    _id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    dispatches = db.relationship('PaperDispatchEntity',
                                 primaryjoin='User._id == PaperDispatchEntity.from_uid',
                                 backref='from_user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def __repr__(self):
        return '''<User('%s', '%s', '%s')>''' % (self._id, self.username, self.password)



class PaperDispatchEntity(db.Model):
    __tablename__ = 'pde'

    _id = db.Column(db.Integer, primary_key=True)

    to_uid = db.Column(db.Integer, db.ForeignKey('user._id'))
    from_uid = db.Column(db.Integer, db.ForeignKey('user._id'))
    paper_id = db.Column(db.Integer, db.ForeignKey('paper._id'))

    status = db.Column(db.Integer) # 0x0 n/a 0x1 not reading 0x2 reading 0x3 read
    dispatch_date = db.Column(db.Date)

    paper = db.relationship('Paper',
                            backref='dispatched_entities')
    to_user = db.relationship('User',
                              primaryjoin='PaperDispatchEntity.to_uid == User._id',
                              backref='papers')

    __table_args__ = (db.UniqueConstraint('from_uid',
                                          'to_uid',
                                          'paper_id',
                                          'dispatch_date',
                                          name='pde_unique_constraint'),)

    def __init__(self, from_uid, to_uid, paper_id, status, dispatch_date):
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.paper_id = paper_id

        self.status = status
        self.dispatch_date = dispatch_date


    def __repr__(self):
        return '''<PDE('%s, '%s', '%s', '%s', '%s')>''' % (self.from_uid,
                                                           self.to_uid,
                                                           self.paper_id,
                                                           self.status,
                                                           self.dispatch_date)



class Paper(db.Model):
    __tablename__ = 'paper'

    _id = db.Column(db.Integer, primary_key=True)

    author = db.Column(db.String)
    title = db.Column(db.String)

    filename = db.Column(db.String, unique=True)
    upload_date = db.Column(db.Date)

    __table_args__ = (db.UniqueConstraint('author',
                                          'title',
                                          name='paper_unique_constraint'),)

    def __init__(self, author, title, filename, upload_date):
        self.author = author
        self.title = title

        self.filename = filename
        self.upload_date = upload_date


    def __repr__(self):
        return '''<Paper('%s', '%s', '%s', '%s')>''' % (self.author,
                                                        self.title,
                                                        self.filename,
                                                        self.upload_date)


