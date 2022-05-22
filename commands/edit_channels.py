import discord
from catch.channels import expected_channels


async def list_channels(message: discord.Message, client: discord.Client):
    channels = []
    for channel_id in expected_channels.expected:
        channel = client.get_channel(channel_id)
        if channel:
            channels.append(f"#{channel.name} ({channel.id})")
        else:
            channels.append(f"Not Found ({channel_id})")
    text = "\n".join(c for c in channels)
    await message.reply(f"Expected channels:```fix\n{text}```")


async def add_channel(message: discord.Message, client: discord.Client, args: tuple):
    channel = client.get_channel(int(args[0]))
    if not channel:
        return await message.reply(f"Channel not found.")
    if expected_channels.is_expected(channel):
        return await message.reply(f"This channel is already on the list.")
    expected_channels.add_channel(channel.id)
    return await message.reply(f"Channel `#{channel}` added to the list.")


async def remove_channel(message: discord.Message, args: tuple):
    channel_id = int(args[0])
    if channel_id not in expected_channels.expected:
        return await message.reply(f"This channel  is not in the list.")
    expected_channels.remove_channel(channel_id)
    return await message.reply(f"Channel id `{channel_id}` removed from list.")