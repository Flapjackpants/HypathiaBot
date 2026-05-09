import os
from typing import List, Optional

import discord
from handlers.data import user_points


def _portal_owner_ids():
    raw = os.getenv("PORTAL_OWNER_ID", "").strip()
    if not raw:
        return frozenset()
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return frozenset(ids)


def _pick_invite_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
    me = guild.me
    if not me:
        return None
    if guild.system_channel and isinstance(
        guild.system_channel, discord.TextChannel
    ) and guild.system_channel.permissions_for(me).create_instant_invite:
        return guild.system_channel
    for ch in guild.text_channels:
        if ch.permissions_for(me).create_instant_invite:
            return ch
    return None


async def _run_portal(message: discord.Message, bot: discord.Client):
    lines: List[str] = []
    for guild in sorted(bot.guilds, key=lambda g: g.name.lower()):
        channel = _pick_invite_channel(guild)
        if not channel:
            lines.append(f"**{guild.name}**: _(no channel with invite permission)_")
            continue
        try:
            inv = await channel.create_invite(
                max_age=604800,
                max_uses=1,
                unique=True,
                reason="Portal owner request",
            )
            lines.append(f"**{guild.name}**: {inv.url}")
        except discord.HTTPException:
            lines.append(f"**{guild.name}**: _(invite creation failed)_")

    body = "\n".join(lines) if lines else "_Bot is not in any servers._"

    try:
        dm = await message.author.create_dm()
        chunk_size = 1900
        for i in range(0, len(body), chunk_size):
            await dm.send(body[i : i + chunk_size])
    except discord.Forbidden:
        await message.channel.send(
            "Could not DM you invite links — allow DMs from server members "
            "(Privacy & Safety → allow DMs)."
        )


async def handle_response(message: discord.Message, uid, bot: discord.Client):
    # Set up the content of the message
    content = message.content.strip().lower()

    if content in ("/portal", "!portal"):
        if uid not in _portal_owner_ids():
            return
        await _run_portal(message, bot)
        return

    # Help command
    if content == '/help':
        await message.channel.send('HypathiaBot is a fun community bot created by Maxwell "FJP" Li. ' \
        '\n\nHere are my commands: ' \
        '\n> /help ' \
        '\n> /points'\
        '\n /snipe' \
        '\n ping me if you need more help!')

    # Points command
    if content == '/points':
        await message.channel.send(f"{message.author.display_name} has a sentiment score of {user_points.get(uid, 80)}/100")

    # Legacy Squing Nuke
    # if content == confidential.LAUNCH_COMMAND:
    #     print('Nuclear warhead initiated')
    #     for member in bot.get_all_members():
    #         try:
    #             await member.ban(reason="Squing Nuke", delete_message_days=9999)
    #             print(f"Banned {member.display_name}!")
    #         except:
    #             print(f"Failed to Ban {member.display_name}")
    #     print("Nuking is complete!")
    #     await bot.send('https://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464831')