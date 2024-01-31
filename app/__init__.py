from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = "beterrabavermelha"
    from app.routes import init_app
    init_app(app)

    return app
