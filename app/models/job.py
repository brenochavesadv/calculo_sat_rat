from datetime import datetime
from run import db


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(64), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='queued', index=True)


class JobFile(db.Model):
    __tablename__ = 'job_files'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), index=True, nullable=False)
    filename = db.Column(db.String(512), nullable=False)
    filepath = db.Column(db.String(2048), nullable=False)
    status = db.Column(db.String(20), default='queued', index=True)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    job = db.relationship('Job', backref=db.backref('files', lazy='dynamic'))
