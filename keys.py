from os import environ as env
import base64


DISCORD_BOT_TOKEN = env["DISCORD_BOT_TOKEN"]
WP_CREDENCIALS = env["WORDPRESS_USER"] + ':' + env["WORDPRESS_PASSWORD"]
WP_TOKEN = base64.b64encode(WP_CREDENCIALS.encode())
WP_AUTH_HEADER = {'Authorization': 'Basic ' + WP_TOKEN.decode('utf-8')}