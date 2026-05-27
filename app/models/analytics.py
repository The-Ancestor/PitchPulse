from datetime import datetime
from app import db

class TrialSession(db.Model):
    __tablename__ = 'trial_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)  
    session_date = db.Column(db.DateTime, nullable=False, index=True)
    session_type = db.Column(db.String(30), nullable=False)  
    notes = db.Column(db.Text)

    attendees = db.relationship('TrialAttendance', backref='session', cascade="all, delete-orphan")


class TrialAttendance(db.Model):
    __tablename__ = 'trial_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    trial_session_id = db.Column(db.Integer, db.ForeignKey('trial_sessions.id', ondelete='CASCADE'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profiles.id', ondelete='CASCADE'), nullable=False)
    
    status = db.Column(db.String(20), default='Present', nullable=False)  # Present, Absent, Injured
    performance_rating = db.Column(db.Integer, nullable=True)  # Scout rating out of 10
    scout_feedback = db.Column(db.Text, nullable=True)


class ScoutingReport(db.Model):
    __tablename__ = 'scouting_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profiles.id', ondelete='CASCADE'), nullable=False)
    scout_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    potential_rating = db.Column(db.String(10), nullable=False)  # e.g., 'Elite', 'Club Level'
    tactical_awareness = db.Column(db.Text)
    physical_assessment = db.Column(db.Text)
    conclusion = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    venue = db.Column(db.String(100), default='Home')
    
    our_score = db.Column(db.Integer, default=0, nullable=False)
    their_score = db.Column(db.Integer, default=0, nullable=False)

    stats = db.relationship('MatchStat', backref='match', cascade="all, delete-orphan")


class MatchStat(db.Model):
    __tablename__ = 'match_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profiles.id', ondelete='CASCADE'), nullable=False)
    
    minutes_played = db.Column(db.Integer, default=0, nullable=False)
    goals = db.Column(db.Integer, default=0, nullable=False)
    assists = db.Column(db.Integer, default=0, nullable=False)
    tackles_won = db.Column(db.Integer, default=0, nullable=False)
    passes_completed = db.Column(db.Integer, default=0, nullable=False)
    passes_attempted = db.Column(db.Integer, default=0, nullable=False)
    match_rating = db.Column(db.Float, nullable=False)  # Out of 10.0

    __table_args__ = (
        db.UniqueConstraint('match_id', 'player_id', name='_player_match_uc'),
    )


class InjuryLog(db.Model):
    __tablename__ = 'injury_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profiles.id', ondelete='CASCADE'), nullable=False)
    
    injury_type = db.Column(db.String(100), nullable=False)  
    status = db.Column(db.String(20), default='Recovering', nullable=False)  
    
    injured_on = db.Column(db.Date, nullable=False)
    cleared_on = db.Column(db.Date, nullable=True)
