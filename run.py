import os
from app import create_app, db
from app.models import User, PlayerProfile, Match, MatchStat


environment = os.environ.get('FLASK_ENV', 'development')

app = create_app(environment)

@app.shell_context_processor
def make_shell_context():
    """
    The Shell Context Flex:
    Running 'flask shell' opens a Python terminal directly bound to your app.
    This function pre-imports the database and models automatically so you can
    test queries instantly without typing 'from app import db' every single time.
    """
    return {
        'db': db,
        'User': User,
        'PlayerProfile': PlayerProfile,
        'Match': Match,
        'MatchStat': MatchStat
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
