from flask import Flask, render_template, redirect, url_for
from flask_discord import DiscordOAuth2Session
from os import environ
from dotenv import load_dotenv
from discord.ext import ipc

app = Flask(__name__)
ipc_client = ipc.Client(secret_key="RafaelSetton")

load_dotenv()
app.config["SECRET_KEY"] = "test123"
app.config["DISCORD_CLIENT_ID"] = 794972976239738920
app.config["DISCORD_CLIENT_SECRET"] = environ['CLIENT_SECRET']
app.config["DISCORD_REDIRECT_URI"] = "https://mybotrafaelsetton-dashboard.herokuapp.com/userpage"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

session = DiscordOAuth2Session(app)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login')
async def login():
    page = session.create_session(scope=['guilds', 'email', 'identify'])
    return page


@app.route('/userpage')
async def userpage():
    try:
        session.callback()
    except:
        return redirect(url_for("login"))

    guild_ids = await ipc_client.request("get_guild_ids")

    try:
        user_guilds = session.fetch_guilds()
        user = session.fetch_user()
    except:
        return redirect(url_for("login"))

    same_guilds = list(filter(lambda g: g.id in guild_ids, user_guilds))

    return render_template("userpage.html", user=user, matching=same_guilds)


@app.route("/dashboard/<_id>")
async def dashboard(_id):
    guild = await ipc_client.request("get_guild_info", guild_id=int(_id))
    return render_template("dashboard.html", info=guild)
