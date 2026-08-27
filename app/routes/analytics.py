from flask import render_template, request, flash, redirect, url_for
from . import analytics_bp 
from app.models import PlayerProfile, MatchStat, Match, User
from app import db
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash



@analytics_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'Scout':
            return redirect(url_for('analytics.scout_dashboard'))
        return redirect(url_for('analytics.player_profile', user_id=current_user.id))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'Player') # Defaults to Player if not specified

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This system email matrix is already registered.', 'error')
            return redirect(url_for('analytics.register'))

        hashed_password = generate_password_hash(password)

        new_user = User(email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration complete. Security profile compiled successfully.', 'success')
        return redirect(url_for('analytics.login'))

    return render_template('register.html')


@analytics_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        if current_user.role == 'Scout':
            return redirect(url_for('analytics.scout_dashboard'))
        return redirect(url_for('analytics.player_profile', user_id=current_user.id))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Access granted. Welcome back to the system matrix.', 'success')

            if user.role == 'Scout':
                return redirect(url_for('analytics.scout_dashboard'))
            else:
                return redirect(url_for('analytics.player_profile', user_id=user.id))
        
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
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        position = request.form.get('position')
        foot = request.form.get('preferred_foot', 'Right')
        weight = request.form.get('weight', type=float)

        if not first_name or not last_name or not position:
            flash('Error: First name, last name, and position are mandatory.', 'error')
            return redirect(url_for('analytics.register_player'))

        placeholder_email = f"{first_name.lower()}.{last_name.lower()}@pitchpulse.local"
        
        existing_user = User.query.filter_by(email=placeholder_email).first()
        if existing_user:
            placeholder_email = f"{first_name.lower()}.{last_name.lower()}{db.session.query(User).count()}@pitchpulse.local"

        new_user = User(email=placeholder_email, password_hash="pbkdf2:sha256:placeholder_hash", role="Player")
        db.session.add(new_user)
        db.session.commit() 

        new_profile = PlayerProfile(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.strptime('2005-01-01', '%Y-%m-%d').date(), 
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

    player = PlayerProfile.query.get_or_404(player_id)
    
    career_stats = db.session.query(
        func.count(MatchStat.id).label('matches_played'),
        func.sum(MatchStat.goals).label('total_goals'),
        func.sum(MatchStat.assists).label('total_assists'),
        func.sum(MatchStat.tackles_won).label('total_tackles'),
        func.avg(MatchStat.match_rating).label('lifetime_rating')
    ).filter(MatchStat.player_id == player_id).first()

    all_matches = Match.query.order_by(Match.match_date.desc()).all()

    return render_template(
        'player_profile.html',
        player=player,
        stats=career_stats,
        matches=all_matches
    )




@analytics_bp.route('/match/log-stat', methods=['POST'])
def log_match_stat():
    player_id = request.form.get('player_id', type=int)
    match_id = request.form.get('match_id', type=int)
    
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
        flash('Match statistics successfully logged!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Error: Statistics have already been logged for this player in this specific match.', 'error')

    return redirect(url_for('analytics.player_profile', player_id=player_id))
