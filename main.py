from flask import Flask, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Spotify API credentials and scopes
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = 'playlist-read-private playlist-modify-public user-library-modify user-library-read'

# Create a Spotify OAuth client
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)

# Flask route to authorize the user
@app.route('/authorize')
def authorize():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Flask route to handle the Spotify OAuth callback
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # Create a Spotify client with the access token
    sp = spotipy.Spotify(auth=access_token)

    # Get the user's saved tracks
    results = sp.current_user_saved_tracks()

    # Create a playlist with the saved tracks
    playlist_name = 'Descobertas da semana'
    playlist_description = 'Playlist feita em python!'
    playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=True, description=playlist_description)
    track_uris = [track['track']['uri'] for track in results['items']]
    sp.playlist_add_items(playlist['id'], track_uris)

    return 'Playlist created: <a href="https://open.spotify.com/playlist/{}">{}</a>'.format(playlist['id'], playlist_name)

# Flask route pro botão de criar a playlist
@app.route('/')
def index():
    return '<a href="/authorize"><button>Create Playlist</button></a>'

if __name__ == '__main__':
    app.run(port=8080, debug=True)
