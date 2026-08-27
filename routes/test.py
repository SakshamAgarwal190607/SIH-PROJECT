from flask import render_template,request,redirect,Flask

app = Flask(__name__)

@app.route("/profile")
def profile_page():
    return 