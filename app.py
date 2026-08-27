from flask import Flask

from routes.profile import profile_bp
from routes.login import login_bp
from routes.assesment import assessment_bp


app = Flask(__name__)

app.secret_key = "test-secret-key"

app.register_blueprint(profile_bp)
app.register_blueprint(login_bp)
app.register_blueprint(assessment_bp)

if __name__ == "__main__":
    app.run(debug=True)