from . import db


class Subject(db.Model):
    __tablename__ = 'subjects'
    participant_id = db.Column(db.String(64), unique=True, primary_key=True, index=True)
    prolific_pid = db.Column(db.String(64), unique=True)
    recaptcha_complete = db.Column(db.Boolean)
    consent = db.Column(db.Boolean)
    ip_addy = db.Column(db.VARCHAR(200))
    in_progress = db.Column(db.Boolean)
    complete = db.Column(db.Boolean)
    start_time = db.Column(db.DateTime)
    complete_time = db.Column(db.DateTime)
    study_version = db.Column(db.VARCHAR(200))
    attn_chck = db.Column(db.Boolean)
    attn_chck2 = db.Column(db.VARCHAR(400))
    conjunctives = db.relationship('Conjunctive', backref='subject', lazy='dynamic', cascade="all, delete-orphan" )
    disjunctives = db.relationship('Disjunctive', backref='subject', lazy='dynamic', cascade="all, delete-orphan" )


class Conjunctive(db.Model):
    __tablename__ = 'conjunctives'
    id = db.Column(db.Integer, primary_key=True)
    p_c1 = db.Column(db.Float)
    p_c2 = db.Column(db.Float)
    p_c3 = db.Column(db.Float)
    c1_cause_rating = db.Column(db.VARCHAR(200))
    c2_cause_rating = db.Column(db.VARCHAR(200))
    c3_cause_rating = db.Column(db.VARCHAR(200))
    trl_num = db.Column(db.Integer)
    jar_checked = db.Column(db.VARCHAR(5))
    check_correct = db.Column(db.Boolean)
    participant_id = db.Column(db.String, db.ForeignKey('subjects.participant_id'))


class Disjunctive(db.Model):
    __tablename__ = 'disjunctives'
    id = db.Column(db.Integer, primary_key=True)
    p_c1 = db.Column(db.Float)
    p_c2 = db.Column(db.Float)
    p_c3 = db.Column(db.Float)
    c1_cause_rating = db.Column(db.VARCHAR(200))
    c2_cause_rating = db.Column(db.VARCHAR(200))
    c3_cause_rating = db.Column(db.VARCHAR(200))
    participant_id = db.Column(db.String, db.ForeignKey('subjects.participant_id'))


