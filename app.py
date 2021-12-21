import os
import secrets
from pathlib import Path
from importlib import import_module
from datetime import datetime, timedelta

from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy

# -------------------------------------------------------- Configuration

app = Flask(__name__)
secret_key = os.environ.get("CHATBOT_SECRET_KEY", secrets.token_bytes(32))
db_path = Path(__file__).parent / "chatbot.db"
app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY=secret_key,
    SESSION_COOKIE_SAMESITE="Lax",
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    REPLY_DELAY_MS=int(os.environ.get("CHATBOT_REPLY_DELAY_MS", 2500)),
)
db = SQLAlchemy(app)

# ------------------------------------------------------------- Database


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=None)
    abort = db.Column(db.Boolean, default=None)
    rating = db.Column(db.Integer, default=None)
    comment = db.Column(db.Text, default=None)


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # chatbot replies have a NULL reaction_ms
    reaction_ms = db.Column(db.Integer)


if not db_path.is_file():
    db.create_all()

# ---------------------------------------------------- Handling requests


# There's technically only one route, so as to prevent the user from
# easily navigating the interaction with the chatbot. The state of the
# app is instead held in session["page"], based on which the request is
# dispatched to an appropriate handler.
#
# The scenario can be set via query parameters in the URL
# (?scenario=...). Once set, it's stored in session["scenario"]. Setting
# the scenario clears the session, as it's taken as a signal of a new
# conversation starting. Trying to use the app without setting a
# scenario shows an error.
@app.route("/", methods=("GET", "POST"))
def dispatcher():
    url_scenario = request.args.get("scenario")
    if url_scenario is not None:
        # a scenario was set via the URL's query string -> start a new
        # conversation
        session.clear()
        session["scenario"] = url_scenario
        try:
            import_module(url_scenario)
        except ImportError:
            session["page"] = "not_found"
        return redirect(url_for("dispatcher"))
    elif session.get("scenario") is None:
        # starting a conversation without setting a scenario is
        # forbidden -> 403 error
        return render_template("forbidden.html"), 403

    try:
        scenario = import_module(session["scenario"])
        for attr in ("bg_color", "heading_color", "reply_outline", "reply_bg"):
            setattr(g, attr, getattr(scenario, attr, None))
    except ImportError:
        pass

    if request.args.get("abort"):
        session["page"] = "outro"
        session["abort"] = True
        return redirect(url_for("dispatcher"))

    page = session.setdefault("page", "intro")
    handler = globals().get(page)
    if handler is None:
        abort(404)
    return handler()


def not_found():
    return render_template("not_found.html", scenario=session["scenario"]), 404


def intro():
    if request.method == "GET":
        scenario = import_module(session["scenario"])
        return render_template(
            "intro.html", scenario=scenario.__name__, scenario_desc=scenario.description
        )
    elif request.method == "POST":
        user = User(nick=request.form.get("nick"), scenario=session["scenario"])
        db.session.add(user)
        db.session.commit()
        # the user only has a valid ID after they've been committed to
        # the database
        session["user_id"] = user.id
        session["page"] = "chat"
        return redirect(url_for("dispatcher"))


def chat():
    user = User.query.filter_by(id=session["user_id"]).first()
    user_reply = request.form.get("answer")
    if request.method == "POST":
        db.session.add(
            Reply(
                user_id=user.id,
                content=user_reply,
                reaction_ms=request.form.get("reaction-ms"),
            )
        )

    conversation_state = session.setdefault("conversation_state", {})
    scenario = import_module(session["scenario"])
    bot_reply = scenario.reply(user_reply, user.nick, conversation_state)
    session.modified = True
    if bot_reply is None:
        session["page"] = "outro"
        response = redirect(url_for("dispatcher"))
    else:
        db.session.add(Reply(user_id=user.id, content=bot_reply))
        response = render_template(
            "chat.html", bot_reply=bot_reply, scenario=scenario.__name__
        )

    db.session.commit()
    return response


def outro():
    if request.method == "GET":
        return render_template("outro.html", errors=())
    elif request.method == "POST":
        errors = []
        rating = request.form.get("rating")
        if rating is None:
            errors.append("Bodové hodnocení je povinné, vyplňte je prosím.")
        if errors:
            return render_template("outro.html", errors=errors)

        user = User.query.filter_by(id=session["user_id"]).first()
        user.end_date = datetime.utcnow()
        user.abort = session.get("abort", False)
        user.rating = int(rating)
        user.comment = request.form.get("comment")

        db.session.add(user)
        db.session.commit()
        session.clear()
        return render_template("thanks.html")


if __name__ == "__main__":
    app.run(debug=True)
