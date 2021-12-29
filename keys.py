from os import environ as env
from aiohttp import BasicAuth


DISCORD_BOT_TOKEN = env["DISCORD_BOT_TOKEN"]
WORDPRESS_AUTH = BasicAuth(login=env["WORDPRESS_USER"], password=env["WORDPRESS_PASSWORD"])