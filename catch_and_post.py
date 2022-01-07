import re
import discord
from keys import WORDPRESS_AUTH
import markdown
import requests


WORDPRESS_API_URL = "https://alphaleaks.com/wp-json/wp/v2/"
POST_TYPE = "discord-guilds"
POSTS_URL = WORDPRESS_API_URL + POST_TYPE
INVITE_PATTERN = r'discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})'
URL_REGEX = re.compile(r'(https?://[^\s]+)')
with open("channel_ids.txt", "r") as file:
    channel_ids = file.read().split("\n")
    EXPECTED_CHANNELS = [int(c_id) for c_id in channel_ids]


class GuildIcon:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.format = "gif" if guild.is_icon_animated() else "png"
        self.filename = guild.name
        self.file = None

    async def load(self):
        self.file = await self.guild.icon_url.read()


async def go(message: discord.Message, client: discord.Client):
    if message.channel.id in EXPECTED_CHANNELS:
        invites = re.findall(INVITE_PATTERN, message.content)
        for invite_url in invites:
            if invite_url.startswith("discord"):
                default = "https://" + invite_url   # correcting link
                message.content.replace(invite_url, default)
                invite_url = default
            try:
                invite = await client.fetch_invite(url=invite_url)
            except discord.NotFound:    # invalid invite
                continue
            else:
                icon = GuildIcon(invite.guild)
                await icon.load()
                publish_invite(invite, message, icon)


def publish_invite(invite: discord.Invite, message: discord.Message, icon: GuildIcon):
    desc = URL_REGEX.sub(r'<a href="\1">\1</a>', str(message.clean_content))    # making clickable links
    desc = markdown.markdown(str(desc))     # converting discord markdown to html
    desc += GUILD_DATA_TABLE.format(message.guild.name, str(message.author), invite.approximate_member_count)
    post = get_post(invite.guild)
    if not post:
        create_post(invite, desc, icon)
    else:
        if invite.url not in post['content']['rendered']:
            edit_post(post, desc)


def get_post(guild: discord.Guild):
    payload = {
        'post_type': 'discord-guilds',
        'search': guild.id
    }
    resp = requests.get(url=POSTS_URL, params=payload, auth=WORDPRESS_AUTH)
    posts = resp.json()
    if posts:
        return posts[0]
    else:
        return None


def create_post(invite: discord.Invite, desc: str, icon: GuildIcon):
    guild = invite.guild
    image = upload_image(icon)
    desc += f'\n<!-- Invite Guild ID: {guild.id} -->'   # needed to search by guild id
    payload = {
        'title': invite.guild.name,
        'content': desc,
        'status': 'publish',
        'featured_media': image["id"]
    }
    requests.post(url=POSTS_URL, data=payload)


def upload_image(icon: GuildIcon) -> dict:
    headers = {
        'Content-Type': f'image/{icon.format}',
        'Content-Disposition': f'attachment; filename="{icon.filename}.{icon.format}"'
    }
    url = WORDPRESS_API_URL + "media"
    resp = requests.post(url=url, data=icon.file, headers=headers, auth=WORDPRESS_AUTH)
    return resp.json()


def edit_post(post_data: dict, desc: str):
    desc = post_data['content']['rendered'] + "<hr/>" + desc
    payload = {
        'id': post_data['id'],
        'content': desc
    }
    url = POSTS_URL + f"/{post_data['id']}"
    requests.post(url=url, data=payload, auth=WORDPRESS_AUTH)


GUILD_DATA_TABLE = '''\n
    <table border=1>
    <tr>
        <th>Posted In</th>
        <th>Inviter</th>
        <th>Members</th>
    </tr>
    <tr>
        <td style='text-align:center'>{}</td>
        <td style='text-align:center'>{}</td>
        <td style='text-align:center'>{}</td>
    </tr>
    </table>
'''