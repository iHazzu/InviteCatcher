from os import environ as env
import base64


DISCORD_BOT_TOKEN = env["DISCORD_BOT_TOKEN"]
WP_AUTH_HEADER = {'Authorization': 'Bearer ' + env["WORDPRESS_TOKEN"]}
TWITTER_BEARER_TOKEN = env["TWITTER_BEARER_TOKEN"]