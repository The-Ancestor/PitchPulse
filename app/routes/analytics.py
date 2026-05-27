from flask import render_template, request, flash, redirect, url_for
from . import analytics_bp 
from app.models import PlayerProfile, MatchStat, Match, User
from app import db
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash



@analytics_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If a user is already logged in, don't make them log in again
    if current_user.is_authenticated:
        if current_user.role == 'Scout':
            return redirect(url_for('analytics.scout_dashboard'))
        return redirect(url_for('analytics.player_profile', user_id=current_user.id))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Tell Flask-Login to spin up the encrypted cookie session
            login_user(user)
            flash('Access granted. Welcome back to the system matrix.', 'success')

            # Role-Based Routing
            if user.role == 'Scout':
                return redirect(url_for('analytics.scout_dashboard'))
            else:
                return redirect(url_for('analytics.player_profile', user_id=user.id))
        
        # Generic error message to prevent database username harvesting
        flash('Invalid email or password configuration.', 'error')
        return redirect(url_for('analytics.login'))

    return render_template('login.html')

@analytics_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Session terminated successfully.', 'info')
    return redirect(url_for('analytics.login'))



@analytics_bp.route('/dashboard/scout', methods=['GET'])
@login_required
def scout_dashboard():

    position_filter = request.args.get('position', None)
    
    query = PlayerProfile.query.filter_by(is_active=True)
    

    if position_filter:
        query = query.filter_by(primary_position=position_filter)
        
    players = query.all()
    
    # Calculates global averages across all recorded statistics in one database operation
    team_insights = db.session.query(
        func.avg(MatchStat.match_rating).label('avg_team_rating'),
        func.sum(MatchStat.goals).label('total_team_goals')
    ).first()


    return render_template(
        'scout_dashboard.html', 
        players=players, 
        insights=team_insights,
        selected_position=position_filter
    )
    
    
    

@analytics_bp.route('/player/register', methods=['GET', 'POST'])
@login_required
def register_player():
    if request.method == 'POST':
        # 1. Capture the raw input strings from the UI form submission
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        position = request.form.get('position')
        foot = request.form.get('preferred_foot', 'Right')
        weight = request.form.get('weight', type=float)

        # 2. Defensive check: Ensure critical fields are not empty
        if not first_name or not last_name or not position:
            flash('Error: First name, last name, and position are mandatory.', 'error')
            return redirect(url_for('analytics.register_player'))

        # 3. Create a placeholder User identity for auth decoupling requirements
        # In prod, this would link to an actual registration invitation email pipeline
        placeholder_email = f"{first_name.lower()}.{last_name.lower()}@pitchpulse.local"
        
        # Check if email variant collision occurs
        existing_user = User.query.filter_by(email=placeholder_email).first()
        if existing_user:
            placeholder_email = f"{first_name.lower()}.{last_name.lower()}{db.session.query(User).count()}@pitchpulse.local"

        new_user = User(email=placeholder_email, password_hash="pbkdf2:sha256:placeholder_hash", role="Player")
        db.session.add(new_user)
        db.session.commit() # Commit identity to generate user.id

        # 4. Instantiate the physical profile card linked directly to that new user identity
        new_profile = PlayerProfile(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.strptime('2005-01-01', '%Y-%m-%d').date(), # Default baseline placeholder age
            primary_position=position,
            preferred_foot=foot,
            current_weight_kg=weight if weight else 70.0,
            is_active=True
        )

        db.session.add(new_profile)
        db.session.commit()

        flash(f"Athlete {first_name} {last_name} successfully registered to system matrix!", "success")
        return redirect(url_for('analytics.scout_dashboard'))

    return render_template('register_player.html')    
    
    

@analytics_bp.route('/player/<int:player_id>', methods=['GET'])
def player_profile(player_id):
    # Fetch the player or throw a clean 404 error if they don't exist
    player = PlayerProfile.query.get_or_404(player_id)
    
    # Career Performance Aggregations (Single-trip DB optimization)
    career_stats = db.session.query(
        func.count(MatchStat.id).label('matches_played'),
        func.sum(MatchStat.goals).label('total_goals'),
        func.sum(MatchStat.assists).label('total_assists'),
        func.sum(MatchStat.tackles_won).label('total_tackles'),
        func.avg(MatchStat.match_rating).label('lifetime_rating')
    ).filter(MatchStat.player_id == player_id).first()

    # Fetch all available matches in the system so the logging form dropdown can display them
    all_matches = Match.query.order_by(Match.match_date.desc()).all()

    return render_template(
        'player_profile.html',
        player=player,
        stats=career_stats,
        matches=all_matches
    )




@analytics_bp.route('/match/log-stat', methods=['POST'])
def log_match_stat():
    # Extract the form payload sent from the UI
    player_id = request.form.get('player_id', type=int)
    match_id = request.form.get('match_id', type=int)
    
    # Instantiate the data metric row
    stat_entry = MatchStat(
        match_id=match_id,
        player_id=player_id,
        minutes_played=request.form.get('minutes_played', default=0, type=int),
        goals=request.form.get('goals', default=0, type=int),
        assists=request.form.get('assists', default=0, type=int),
        tackles_won=request.form.get('tackles_won', default=0, type=int),
        match_rating=request.form.get('match_rating', default=6.0, type=float)
    )

    try:
        db.session.add(stat_entry)
        db.session.commit()
        # Flash messages let us send quick session alerts to the frontend
        flash('Match statistics successfully logged!', 'success')
    except IntegrityError:
        db.session.rollback()
        # This catches our composite unique constraint (_player_match_uc) if a duplicate entry is made
        flash('Error: Statistics have already been logged for this player in this specific match.', 'error')

    return redirect(url_for('analytics.player_profile', player_id=player_id))
