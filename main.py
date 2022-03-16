"""
Project: InviteCatcher
Author: iHazzu
Function: Catch discord invites and post it on Wordpress
Date: 17/12/2021
"""

import discord
import keys
import commands, catch_invites, catch_tweets
from wp_api import WpApi
from channels import expected_channels


client = discord.Client(
    guild_subscription_options=discord.GuildSubscriptionOptions(max_online=1, auto_subscribe=False)
)
wp = WpApi(
    domain=keys.WORDPRESS_DOMAIN,
    user=keys.WORDPRESS_USER,
    password=keys.WORDPRESS_PASSWORD
)


# events
@client.event
async def on_ready():
    print("---| BOT ONLINE |---")
    print(f"User: {client.user}")
    print(f"Guilds: {len(client.guilds)}")
    await client.change_presence(status=discord.Status.invisible)


@client.event
async def on_message(message: discord.Message):
    await commands.process_message(message, client)
    if expected_channels.is_expected(message.channel):
        await catch_invites.go(message, client, wp)
        await catch_tweets.go(message, wp)


# connecting to discord
client.run(keys.DISCORD_BOT_TOKEN)