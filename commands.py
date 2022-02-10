import discord
from channels import expected_channels
prefix = "!"


async def process_message(message: discord.Message, client: discord.Client):

    if message.content.starts_with(f"{prefix}channels"):
        channels = [client.get_channel(c_id) for c_id in expected_channels.expected]
        text = "\n".join(str(c) for c in channels)
        await message.reply(f"Expected channels:```fix\n{text}```")

    elif message.content.starts_with(f"{prefix}addchannel"):
        channel_id = message.content.split(" ")[1]
        channel = client.get_channel(int(channel_id))
        if not channel:
            return await message.reply(f"Channel not found.")
        if expected_channels.is_expected(channel):
            return await message.reply(f"This channel is already on the list.")
        expected_channels.add_channel(channel.id)
        return await message.reply(f"Channel `{channel}` added to the list.")

    elif message.content.starts_with(f"{prefix}removechannel"):
        channel_id = message.content.split(" ")[1]
        if channel_id not in expected_channels.expected:
            return await message.reply(f"This channel  is not in the list.")
        expected_channels.remove_channel(channel_id)
        return await message.reply(f"Channel id `{channel_id}` removed from list.")