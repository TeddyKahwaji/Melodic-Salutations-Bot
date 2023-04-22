import os
from enum import Enum


class Collections(Enum):
    WELCOME_COLLECTION = "welcomeIntros"
    OUTROS_COLLECTION = "byeOutros"
    BLACKLIST_COLLECTION = "blacklist"


class Gifs(Enum):
    BROKEN_ROBOT = "https://media.giphy.com/media/l3vR7SWnEv6mmhS0g/giphy.gif"
    INVALID_USAGE = "https://media.giphy.com/media/11e5gZ6NJ8AB1K/giphy.gif"
    COOLDOWN = "https://media.giphy.com/media/xFmuT64Jto3mRO4w3G/giphy.gif"
    ROBOT_SEARCHING = "https://media.giphy.com/media/S5tkhUBHTTWh865paS/giphy.gif"


YDL_OPTIONS = {
    'format': 'mp3/bestaudio/best',
    'noplaylist': 'True',
    'dump_single_json': 'True',
    'extract_flat': 'True',
    'default_search': 'auto',
    "max_downloads": 1
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


BUCKET_NAME = "twitterbot-e7ab0.appspot.com"
CREDENTIALS_DICT = {
    "type": "service_account",
    "project_id": "twitterbot-e7ab0",
    "private_key_id": os.environ["MELODIC_GOOGLE_PRIVATE_KEY_ID"],
    "private_key": "\n".join(os.environ["MELODIC_PRIVATE_KEY"].split("\\n")),
    "client_email": os.environ["MELODIC_CLIENT_EMAIL"],
    "client_id": os.environ["MELODIC_GOOGLE_CLIENT_ID"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ["MELODIC_CERT_URL"]
}
