"""
Project: InviteCatcher
Author: iHazzu
Function: Catch discord invites and post it on Wordpress
Date: 17/12/2021
"""

import discord
import catch_and_post
from keys import DISCORD_BOT_TOKEN


client = discord.Client(
    guild_subscription_options=discord.GuildSubscriptionOptions(max_online=1, auto_subscribe=False)
)


# events
@client.event
async def on_ready():
    print("---| BOT ONLINE |---")
    print(f"User: {client.user}")
    print(f"Guilds: {len(client.guilds)}")


@client.event
async def on_message(message: discord.Message):
    await catch_and_post.go(message, client)


# connecting to discord
client.run(DISCORD_BOT_TOKEN)