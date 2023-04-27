import os
from enum import Enum


class Collections(Enum):
    WELCOME_COLLECTION = "welcomeIntros"
    OUTROS_COLLECTION = "byeOutros"
    BLACKLIST_COLLECTION = "blacklist"


class Images(Enum):
    WAITING_ROBOT = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/e2e475ef-615e-4f8b-a488-697c7bab6d01/dfqzj2e-d4d87bcf-8dc4-4881-9d3a-85ef32e16ae5.png/v1/fill/w_1280,h_640,q_80,strp/robot_waiting_for_its_human_by_wonderlandartworks_dfqzj2e-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NjQwIiwicGF0aCI6IlwvZlwvZTJlNDc1ZWYtNjE1ZS00ZjhiLWE0ODgtNjk3YzdiYWI2ZDAxXC9kZnF6ajJlLWQ0ZDg3YmNmLThkYzQtNDg4MS05ZDNhLTg1ZWYzMmUxNmFlNS5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.4dk0gtdfntmMuxUX5BtjLnan4AA4sgf9pBezGqUONc8"


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

COMMANDS_TO_DESCRIPTION = {
    "📽️ Upload": "Upload an outro/intro voiceline (.zip, .mp3, .m4a) for a given user",
    "🗏 voicelines": "View the intro/outro voicelines for a given user",
    "🚫 blacklist": "Prevent me from using your voicelines",
    "🟩 whitelist": "Undo a previous blacklist command which allows me to use your voicelines",
    "💀 delete": "Remove voicelines for a given user"
}
