import discord
from channels import expected_channels
prefix = "!"
ALLOWED_USERS = [442675649749057540, 535159866717896726]    # [CryptoDayTrade, Hazzu]


async def process_message(message: discord.Message, client: discord.Client):
    if message.author.id not in ALLOWED_USERS:
        return

    if message.content.startswith(f"{prefix}channels"):
        channels = []
        for channel_id in expected_channels.expected:
            channel = client.get_channel(channel_id)
            if channel:
                channels.append(f"#{channel.name} ({channel.id})")
            else:
                channels.append(f"Not Found ({channel_id})")
        text = "\n".join(c for c in channels)
        await message.reply(f"Expected channels:```fix\n{text}```")

    elif message.content.startswith(f"{prefix}addchannel"):
        channel_id = message.content.split(" ")[1]
        channel = client.get_channel(int(channel_id))
        if not channel:
            return await message.reply(f"Channel not found.")
        if expected_channels.is_expected(channel):
            return await message.reply(f"This channel is already on the list.")
        expected_channels.add_channel(channel.id)
        return await message.reply(f"Channel `#{channel}` added to the list.")

    elif message.content.startswith(f"{prefix}removechannel"):
        channel_id = int(message.content.split(" ")[1])
        if channel_id not in expected_channels.expected:
            return await message.reply(f"This channel  is not in the list.")
        expected_channels.remove_channel(channel_id)
        return await message.reply(f"Channel id `{channel_id}` removed from list.")