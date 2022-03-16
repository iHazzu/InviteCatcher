import re
import discord
import markdown
from wp_api import WpApi


POST_TYPE = "discord-guilds"
INVITE_PATTERN = r'discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})'
URL_REGEX = re.compile(r'(https?://[^\s]+)')


class GuildIcon:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        ext = "gif" if guild.is_icon_animated() else "png"
        self.filename = f"{guild.name}.{ext}"
        self.file = None

    async def load(self):
        self.file = await self.guild.icon_url.read()


async def go(message: discord.Message, client: discord.Client, wp: WpApi):
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
            publish_invite(invite, message, icon, wp)


def publish_invite(invite: discord.Invite, message: discord.Message, icon: GuildIcon, wp: WpApi):
    guild = invite.guild
    desc = URL_REGEX.sub(r'<a href="\1">\1</a>', str(message.clean_content))    # making clickable links
    desc = markdown.markdown(str(desc))     # converting dirscord markdown to html
    desc += GUILD_DATA_TABLE.format(message.guild.name, str(message.author), invite.approximate_member_count)
    post = wp.get_post(POST_TYPE, str(guild.id))
    if not post:
        desc += f'\n<!-- Invite Guild ID: {guild.id} -->'  # needed to search by guild id
        media_id = wp.upload_image(icon.filename, icon.file)["id"]
        wp.create_post(POST_TYPE, guild.name, desc, media_id)
    else:
        if invite.url not in post['content']['rendered']:
            desc = post['content']['rendered'] + "<hr/>" + desc
            wp.edit_post(POST_TYPE, post["id"], desc)


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