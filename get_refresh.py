import os 
from subprocess import Popen
from dotenv import dotenv_values
import spotipy
from spotipy.oauth2 import SpotifyOAuth

configuration = {**dotenv_values("amostra.env", **dotenv_values(".env"), **os.environ)}

scopes = ["playlist-read-private", "playlist-modify-private"]
spotify_auth = SpotifyOAuth(scope=scopes, client_id = configuration('CLIENT_ID'), 
                            client_secret = configuration('CLIENT_SECRET'),
                            redirect_uri=configuration('REDIRECT_URI'))
                            
url = spotify_auth.get_authorize_url()
redirect_server = None

if "localhost" in configuration['REDIRECT_URI']:
    hostport = configuration['REDIRECT_URI'].rstrip("/").split(":")[-1]
    redirect_server = Popen(["python", "-m", "http.server", hostport])

print(f"Abra o seguinte link: \n\n {url}\n")
print("Aceite a autorização do Spotify")

url_redirect = input("Coloque a URL que você foi redirecionado'''no terminal após aceitar a autorização")

response_code = spotify_auth.parse_response_code(url_redirect)
access_token = spotify_auth.get_access_token(response_code)

print(f"O refresh token é \n\n{access_token['refresh_token']}\n")
print(f"Guardar isso como REFRESH_TOKEN nos arquivos .env")

if redirect_server is not None:
    redirect_server.terminate