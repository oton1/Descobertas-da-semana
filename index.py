import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import os
import json
from flask import Flask, request, redirect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

SPOTIPY_CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "playlist-modify-public"

# Creating instance for oAuth
sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI, scope=SCOPE)
token_info = {}

# Load token info from file if it exists
if os.path.exists('token.json'):
    with open('token.json', 'r') as f:
        token_info = json.load(f)

def is_token_expired(token_info):
    if 'expires at' not in token_info:
        return False
    expires_at = token_info['expires_at']
    now = datetime.utcnow()
    return expires_at - timedelta(minutes=10) < now

def refresh_token_if_expired(token_info):
    if is_token_expired(token_info):
        sp = spotipy.Spotify(auth_manager=sp_oauth)
        new_token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        # Update token info file with new token
        with open('token.json', 'w') as f:
            json.dump(new_token_info, f)
        return new_token_info
    return token_info

@app.route('/')
def homepage():
    auth_url = sp_oauth.get_authorize_url()
    return f"<h1>Bem vindo ao criador de playlist de descobertas da semana</h1><form action='/create_playlist_button' method='POST'><button type='submit'>Criar<p>Clique no botão para criar uma nova playlist:</p><a href='{auth_url}'><button>Criar playlist</button></a>"

@app.route('/callback')
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    token_info['refresh_token'] = sp_oauth.refresh_token
    token_info['expires_at'] = datetime.utcnow() + timedelta(seconds=token_info['expires_in'])
    # Save token info to file
    with open('token.json', 'w') as f:
        json.dump(token_info, f)
    return "Autenticação bem sucedida"

@app.route('/create_playlist')
def create_playlist():
    global token_info
    if is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        # Save token info to file
        with open('token.json', 'w') as f:
            json.dump(token_info, f)
    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    user_id = sp.current_user()['id']
    playlist_name = 'Descobertas da semana 2: o inimigo agora é outro'
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    discover_weekly_playlist = sp.user_playlist(user=user_id, playlist_id='37i9dQZEVXcNaMmYylhqug')
    tracks = [track['track']['uri'] for track in discover_weekly_playlist['tracks']['items']]
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=tracks)
    return f"Playlist criada com sucesso: {playlist['external_urls']['spotify']}"

@app.route('/create_playlist_button', methods=['POST'])
def create_playlist_button():
    if request.method == 'POST':
        return redirect('/create_playlist')


if __name__ == "__main__":
    auth_url = sp_oauth.get_authorize_url()
    print (f"Por favor visite essa URL para autorizar o app: {auth_url}")
    app.run(debug=True)
