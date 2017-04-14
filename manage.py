import os
from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand
from app.models import User, Role, Comment, Post, Category

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def _make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Comment=Comment, Post=Post, Category=Category)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=_make_shell_context))

if __name__ == '__main__':
    manager.run()













