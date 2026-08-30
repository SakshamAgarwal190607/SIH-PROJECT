from flask import Flask

from routes.login import login_bp
from routes.profile import profile_bp
from routes.assesment import assessment_bp
from routes.dashboard import dashboard_bp
from routes.igot_traning import igot_bp
from routes.quiz import quiz_bp
# from routes.reassessment import reassessment_bp
from routes.copilot import copilot_bp


app = Flask(__name__)

# Session ke liye secret key
app.secret_key = "sih-mvp-secret-key-change-later"


# Register Blueprints
app.register_blueprint(login_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(assessment_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(igot_bp)
app.register_blueprint(quiz_bp)
# app.register_blueprint(reassessment_bp)
app.register_blueprint(copilot_bp)


if __name__ == "__main__":
    app.run(debug=True)