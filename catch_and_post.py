import re
import discord
from keys import WORDPRESS_AUTH
from aiohttp import ClientSession
import markdown
from asyncio import sleep
import requests


WORDPRESS_API_URL = "https://alphaleaks.com/wp-json/wp/v2/"
POST_TYPE = "discord-guilds"
POSTS_URL = WORDPRESS_API_URL + POST_TYPE
INVITE_PATTERN = "(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?"
URL_REGEX = re.compile(r'(https?://[^\s]+)')
publishing = set()     # Avoid duplicate posts for simultaneous messages
with open("channel_ids.txt", "r") as file:
    channel_ids = file.read().split("\n")
    EXPECTED_CHANNELS = [int(c_id) for c_id in channel_ids]


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

            while invite.guild.id in publishing:    # preventing concurrency errors when publishing two invitations in the same post
                await sleep(1)
            try:
                publishing.add(invite.guild.id)
                await publish_invite(invite, message)
            finally:
                publishing.remove(invite.guild.id)


async def publish_invite(invite, message):
    desc = URL_REGEX.sub(r'<a href="\1">\1</a>', str(message.clean_content))    # making clickable links
    desc = markdown.markdown(str(desc))     # converting discord markdown to html
    desc += GUILD_DATA_TABLE.format(message.guild.name, str(message.author), invite.approximate_member_count)
    async with ClientSession(auth=WORDPRESS_AUTH) as session:
        post = await fetch_post(invite.guild, session)
        if not post:
            await create_post(invite, desc, session)
        else:
            if invite.url not in post['content']['rendered']:
                await edit_post(post, desc, session)


async def fetch_post(guild: discord.Guild, session: ClientSession):
    payload = {
        'post_type': 'discord-guilds',
        'search': guild.id
    }
    async with session.get(url=POSTS_URL, params=payload) as resp:
        posts = await resp.json()
        if posts:
            return posts[0]
        return None


async def create_post(invite: discord.Invite, desc: str, session: ClientSession):
    guild = invite.guild
    image = await upload_icon(guild)
    desc += f'\n<!-- Invite Guild ID: {guild.id} -->'
    payload = {
        'title': invite.guild.name,
        'content': desc,
        'status': 'publish',
        'featured_media': image["id"]
    }
    await session.post(url=POSTS_URL, data=payload)


async def upload_icon(guild: discord.Guild) -> dict:
    ext = "gif" if guild.is_icon_animated() else "png"
    headers = {
        'Content-Type': f'image/{ext}',
        'Content-Disposition': f'attachment; filename="{guild.name}.{ext}"'
    }
    icon = await guild.icon_url.read()
    url = WORDPRESS_API_URL + "media"

    # i used requests instead aiohttp to avoid the error
    # aiohttp.client_exceptions.ClientPayloadError: Response payload is not completed
    # in dreamhost vps server
    resp = requests.post(url=url, data=icon, headers=headers, auth=(WORDPRESS_AUTH.login, WORDPRESS_AUTH.password))
    return resp.json()


async def edit_post(post_data: dict, desc: str, session: ClientSession):
    desc = post_data['content']['rendered'] + "<hr/>" + desc
    payload = {
        'id': post_data['id'],
        'content': desc
    }
    url = POSTS_URL + f"/{post_data['id']}"
    await session.post(url=url, data=payload)


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