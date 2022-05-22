import discord


class Channels:
    def __init__(self):
        self.expected = []
        self.load_expected_channels()

    def load_expected_channels(self):
        with open("catch/channel_ids.txt", "r") as file:
            channel_ids = file.read().split("\n")
            self.expected = [int(c_id) for c_id in channel_ids]

    def save_expected_channel(self):
        with open("catch/channel_ids.txt", "w") as file:
            file.write("\n".join([str(c_id) for c_id in self.expected]))

    def is_expected(self, channel: discord.TextChannel):
        return channel.id in self.expected

    def add_channel(self, channel_id: int):
        self.expected.append(channel_id)
        self.save_expected_channel()

    def remove_channel(self, channel_id: int):
        self.expected.remove(channel_id)
        self.save_expected_channel()


expected_channels = Channels()
