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


    def force_statistics(self):
        self.forwarded = len(filter(lambda _: _,
                                    self.papers))
        self.reading = len(filter(lambda entity: entity.status == 0x2,
                                  self.papers))
        self.read = len(filter(lambda entity: entity.status == 0x3,
                               self.papers))
        self.statistics = '''<span style="text-align: center;">
        <strong style="margin-right: 7px;">%s</strong>/
        <strong style="margin-right: 7px; color: orange;">%s</strong>/
        <strong style="margin-right: 7px; color: green;">%s</strong>
        </span>''' % (
            self.forwarded,
            self.reading,
            self.read
        )


    def __repr__(self):
        return '''<User('%s', '%s', '%s')>''' % (self._id, self.username, self.password)



class PaperDispatchEntity(db.Model):
    STATUS_STR = {
        0x0: 'n/a',
        0x1: 'Not Started',
        0x2: 'Reading',
        0x3: 'Already Read'
    }
    STATUS_CLASS = {
        0x0: '',
        0x1: 'info',
        0x2: 'warning',
        0x3: 'success'
    }

    __tablename__ = 'pde'

    _id = db.Column(db.Integer, primary_key=True)

    to_uid = db.Column(db.Integer, db.ForeignKey('user._id'))
    from_uid = db.Column(db.Integer, db.ForeignKey('user._id'))
    paper_id = db.Column(db.Integer, db.ForeignKey('paper._id'))

    forward_status = db.Column(db.Integer) # 0x0 pending 0x1 refused

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


    def force_status_str(self):
        self.status_str = PaperDispatchEntity.STATUS_STR[self.status]
        self.status_class = PaperDispatchEntity.STATUS_CLASS[self.status]


    def __repr__(self):
        return '''<PDE('%s', '%s', '%s', '%s', '%s')>''' % (self.from_uid,
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
    uploader_id = db.Column(db.Integer, db.ForeignKey('user._id'))
    uploader = db.relationship('User',
                               primaryjoin='Paper.uploader_id == User._id',
                               backref='uploaded_papers')

    __table_args__ = (db.UniqueConstraint('author',
                                          'title',
                                          name='paper_unique_constraint'),)

    def __init__(self, author, title, filename, upload_date, uploader_id):
        self.author = author
        self.title = title

        self.filename = filename
        self.upload_date = upload_date
        self.uploader_id = uploader_id


    def force_statistics_data(self):
        self.forwarded = filter(lambda entity: entity.status == 0x1,
                                self.dispatched_entities)
        self.reading = filter(lambda entity: entity.status == 0x2,
                              self.dispatched_entities)
        self.read = filter(lambda entity: entity.status == 0x3,
                           self.dispatched_entities)
        self.statistics = '''<span style="text-align: center;">
        <strong style="margin-right: 7px;">%s</strong>/
        <strong style="margin-right: 7px; color: orange;">%s</strong>/
        <strong style="margin-right: 7px; color: green;">%s</strong>
        </span></a>''' % (
            len(self.forwarded),
            len(self.reading),
            len(self.read)
        )


    def __repr__(self):
        return '''<Paper('%s', '%s', '%s', '%s', '%s')>''' % (self.author,
                                                              self.title,
                                                              self.filename,
                                                              self.upload_date,
                                                              self.uploader_id)


