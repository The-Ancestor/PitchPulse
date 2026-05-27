from datetime import datetime
from app import db
from flask_login import UserMixin
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    email = db.Column(db.String(120), unique=True, nullable=False, index=True) 
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Player', nullable=False) # Admin, Scout, Player
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # uselist=False transforms a 1:Many relationship into a strict 1:1 relationship
    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    reports_written = db.relationship('ScoutingReport', backref='scout', foreign_keys='ScoutingReport.scout_id')


class PlayerProfile(db.Model):
    __tablename__ = 'player_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False, index=True) 
    date_of_birth = db.Column(db.Date, nullable=False)
    preferred_foot = db.Column(db.String(10), default='Right')
    primary_position = db.Column(db.String(20), nullable=False, index=True) 
    current_weight_kg = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    match_stats = db.relationship('MatchStat', backref='player', cascade="all, delete-orphan")
    injuries = db.relationship('InjuryLog', backref='player', cascade="all, delete-orphan")
    trial_appearances = db.relationship('TrialAttendance', backref='player', cascade="all, delete-orphan")
