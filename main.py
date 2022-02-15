"""
Project: InviteCatcher
Author: iHazzu
Function: Catch discord invites and post it on Wordpress
Date: 17/12/2021
"""

import discord
from keys import DISCORD_BOT_TOKEN
import commands, catch_discord_guilds, catch_tweets
from channels import expected_channels


client = discord.Client(
    guild_subscription_options=discord.GuildSubscriptionOptions(max_online=1, auto_subscribe=False)
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
        await catch_discord_guilds.go(message, client)
        await catch_tweets.go(message)


# connecting to discord
client.run(DISCORD_BOT_TOKEN)