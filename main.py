from flask import Flask, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Credenciais da API e  Scopes
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = 'playlist-read-private playlist-modify-public user-library-modify user-library-read'

# Criação do cliente OAuth
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)

# Route do Flask pra autorizar o usuário
@app.route('/authorize')
def authorize():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Route do Flask pra autorizar o callback
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # Criar um client do Spotify com o access_token
    sp = spotipy.Spotify(auth=access_token)

    # Ler as tracks salvas do usuário
    results = sp.current_user_saved_tracks()

    # Criar a playlist com as descobertas da semana
    playlist_name = 'Descobertas da semana'
    playlist_description = 'Playlist feita em python!'
    playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=True, description=playlist_description)
    track_uris = [track['track']['uri'] for track in results['items']]
    sp.playlist_add_items(playlist['id'], track_uris)

    return 'Playlist criada: <a href="https://open.spotify.com/playlist/{}">{}</a>'.format(playlist['id'], playlist_name)

# Flask route pro botão de criar a playlist
@app.route('/')
def index():
    return '<a href="/authorize"><button>Criar playlist de descobertas da semana</button></a>'

# Dar run no Flask app
if __name__ == '__main__':
    app.run(port=8080, debug=True)
