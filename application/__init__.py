from flask import Flask


def create_app():
    app = Flask(__name__)

    app.secret_key = '2389457uuign134oifjrgj34905gj'

    from application.routes import main
    from authentication import authentication

    app.register_blueprint(main)
    app.register_blueprint(authentication)

    return app
