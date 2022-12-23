import os
from flask import Flask

def create_app():
    app  = Flask(__name__,instance_relative_config=True)
    
    # Configuration
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['DATABASE'] = os.path.join(app.instance_path, 'senserver.sqlite')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # blueprint for index page
    from . import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')
    
    # Register API for database
    from . import db
    db.init_app(app)

    # Register Blueprint for API
    from . import api
    app.register_blueprint(api.bp)

    return app