from flask import Flask, session, redirect, request, render_template
from requests_oauthlib import OAuth2Session
from os import environ
from dotenv import load_dotenv
from discord.ext import ipc

ipc_client = ipc.Client(secret_key="RafaelSetton")

load_dotenv()

OAUTH2_CLIENT_ID = environ['CLIENT_ID']
OAUTH2_CLIENT_SECRET = environ['CLIENT_SECRET']
OAUTH2_REDIRECT_URI = "http://127.0.0.1:5000/userpage" #TODO: Adjust to deploy

API_BASE_URL = environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater,
    )


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login')
async def login():
    discord = make_session(scope=['guilds', 'email', 'identify'])
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/userpage')
async def userpage():
    if request.values.get('error'):
        return request.values['error']

    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token

    user = discord.get(API_BASE_URL + '/users/@me').json()
    user_guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    guild_ids = await ipc_client.request("get_guild_ids")

    same_guilds = [guild for guild in user_guilds if int(guild['id']) in guild_ids]
    return render_template("userpage.html", user=user, matching=same_guilds)


@app.route("/dashboard/<_id>")
async def dashboard(_id):
    guild = await ipc_client.request("get_guild_info", guild_id=int(_id))
    return render_template("dashboard.html", info=guild)


if __name__ == '__main__':
    app.run(host="localhost", debug=True)
