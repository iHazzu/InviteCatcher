import discord
from .edit_channels import list_channels, add_channel, remove_channel
from .retweets import get_retweets
prefix = "!"
ALLOWED_USERS = [442675649749057540, 535159866717896726]    # [CryptoDayTrade, Hazzu]


async def process_message(message: discord.Message, client: discord.Client):
    if not message.content.startswith(prefix):
        return
    if message.author.id not in ALLOWED_USERS:
        return
    args = message.content.lower().split()
    command = args[0].replace(prefix, "")
    args = args[1:]
    if command == "channels":
        await list_channels(message, client)
    elif command == "addchannel":
        await add_channel(message, client, args)
    elif command == "removechannel":
        await remove_channel(message, args)
    elif command == "retweets":
        await get_retweets(message, args)