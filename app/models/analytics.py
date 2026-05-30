from datetime import datetime
from app import db



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

