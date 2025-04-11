import configparser

config = configparser.ConfigParser()
config.read('config.ini')

API_ID = int(config["bot"]["api_id"])
API_HASH = config["bot"]["api_hash"]
BOT_TOKEN = config["bot"]["bot_token"]
ADMIN_IDS = [6856658357, 8143693753]
STORAGE_CHANNEL = int(config["bot"]["storage_channel"])
MOVIE_CHANNEL = config["bot"]["movie_channel"]
STORAGE_CHANNEL_MULTI = int(config["bot"]["storage_channel_multi"])