import discord
from discord.ext import commands
from datetime import datetime
import time
import os

import responses
import handlers.helpers as helpers
from dotenv import load_dotenv
from handlers.data import last_message_time
from handlers.messageAnalysis import handle_user_points
from handlers.leaderboard import update_social_credit_board
from handlers.chatBot import handle_chat_bot

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
now = time.time()

@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Run handler functions
    if message.author == bot.user:
        return

    uid = message.author.id
    last_message_time[uid] = now

    await handle_user_points(message, uid, now)
    await responses.handle_response(message, uid)
    await update_social_credit_board(bot, message.guild)
    await handle_chat_bot(bot ,message)

    # Logger for messages:
    log_channel = await helpers.get_or_create_channel(message.guild, "message-logs")
    embed = discord.Embed(
        title=f"💬 New Message from {message.author}",
        description=f"**Channel:** {message.channel.mention}\n**Message:** {message.content or '*No text content*'}",
        color=discord.Color.blue(),
        timestamp=message.created_at
    )
    embed.set_footer(text="Message Log")
    embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)

    if message.attachments:
        attach_list = "\n".join(a.url for a in message.attachments)
        embed.add_field(name="Attachments", value=attach_list, inline=False)

    await log_channel.send(embed=embed)
    await bot.process_commands(message)







# Rest of the logger event handlers------------------------------------------------------------------------------------------------------------------
@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    log_channel = await helpers.get_or_create_channel(before.guild, "message-logs")
    embed = discord.Embed(
        title=f"✏️ Message Edited by {before.author}",
        description=f"**Channel:** {before.channel.mention}\n**Before:** {before.content or '*empty*'}\n**After:** {after.content or '*empty*'}",
        color=discord.Color.gold()
    )
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="Message Log")
    embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
    await log_channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    log_channel = await helpers.get_or_create_channel(message.guild, "message-logs")
    embed = discord.Embed(
        title=f"🗑️ Message Deleted by {message.author}",
        description=f"**Channel:** {message.channel.mention}\n**Content:** {message.content or '*empty*'}",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Message Log")
    embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
    await log_channel.send(embed=embed)

@bot.event
async def on_member_join(member: discord.Member):
    log_channel = await helpers.get_or_create_channel(member.guild, "server-logs")
    embed = discord.Embed(
        title="✅ Member Joined",
        description=f"{member.mention} (`{member}`)\nID: `{member.id}`",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    embed.set_thumbnail(url=member.display_avatar.url)
    await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member: discord.Member):
    log_channel = await helpers.get_or_create_channel(member.guild, "server-logs")
    embed = discord.Embed(
        title="🚪 Member Left",
        description=f"{member.mention} (`{member}`)\nID: `{member.id}`",
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    embed.set_thumbnail(url=member.display_avatar.url)
    await log_channel.send(embed=embed)

# ✅ Bans & Unbans
@bot.event
async def on_member_ban(guild, user):
    log_channel = await helpers.get_or_create_channel(guild, "server-logs")
    embed = discord.Embed(
        title="🚫 Member Banned",
        description=f"**{user}** (`{user.id}`)",
        color=discord.Color.dark_red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    log_channel = await helpers.get_or_create_channel(guild, "server-logs")
    embed = discord.Embed(
        title="✅ Member Unbanned",
        description=f"**{user}** (`{user.id}`)",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

# ✅ Role Logs
@bot.event
async def on_guild_role_create(role):
    log_channel = await helpers.get_or_create_channel(role.guild, "server-logs")
    embed = discord.Embed(
        title="➕ Role Created",
        description=f"Role: {role.mention}\nID: `{role.id}`",
        color=discord.Color.purple(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    log_channel = await helpers.get_or_create_channel(role.guild, "server-logs")
    embed = discord.Embed(
        title="❌ Role Deleted",
        description=f"Role: **{role.name}** (`{role.id}`)",
        color=discord.Color.dark_purple(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_update(before, after):
    log_channel = await helpers.get_or_create_channel(after.guild, "server-logs")
    changes = []
    if before.name != after.name:
        changes.append(f"**Name:** {before.name} → {after.name}")
    if before.color != after.color:
        changes.append(f"**Color:** {before.color} → {after.color}")
    if before.permissions != after.permissions:
        changes.append("**Permissions changed**")

    embed = discord.Embed(
        title="🔄 Role Updated",
        description=f"{after.mention}\n" + ("\n".join(changes) if changes else "No visible changes"),
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

# ✅ Channel Logs
@bot.event
async def on_guild_channel_create(channel):
    log_channel = await helpers.get_or_create_channel(channel.guild, "server-logs")
    embed = discord.Embed(
        title="📂 Channel Created",
        description=f"**Name:** {channel.name}\nID: `{channel.id}`",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    log_channel = await helpers.get_or_create_channel(channel.guild, "server-logs")
    embed = discord.Embed(
        title="❌ Channel Deleted",
        description=f"**Name:** {channel.name}\nID: `{channel.id}`",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_update(before, after):
    log_channel = await helpers.get_or_create_channel(after.guild, "server-logs")
    changes = []
    if before.name != after.name:
        changes.append(f"**Name:** {before.name} → {after.name}")
    if before.category != after.category:
        changes.append(f"**Category:** {before.category} → {after.category}")
    if hasattr(before, "topic") and hasattr(after, "topic") and before.topic != after.topic:
        changes.append(f"**Topic:** {before.topic} → {after.topic}")

    embed = discord.Embed(
        title="🔄 Channel Updated",
        description=f"**{after.name}**\n" + ("\n".join(changes) if changes else "No visible changes"),
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

# ✅ Emoji Logs
@bot.event
async def on_guild_emojis_update(guild, before, after):
    log_channel = await helpers.get_or_create_channel(guild, "server-logs")
    before_names = {e.name for e in before}
    after_names = {e.name for e in after}
    added = after_names - before_names
    removed = before_names - after_names

    desc = ""
    if added:
        desc += f"➕ Added: {', '.join(added)}\n"
    if removed:
        desc += f"❌ Removed: {', '.join(removed)}\n"

    embed = discord.Embed(
        title="😀 Emoji Updated",
        description=desc or "No visible changes",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

# ✅ Server (Guild) Updates
@bot.event
async def on_guild_update(before, after):
    log_channel = await helpers.get_or_create_channel(after, "server-logs")
    changes = []
    if before.name != after.name:
        changes.append(f"**Name:** {before.name} → {after.name}")
    if before.icon != after.icon:
        changes.append("**Icon updated**")

    embed = discord.Embed(
        title="🏰 Server Updated",
        description="\n".join(changes) if changes else "No visible changes",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="Server Log")
    await log_channel.send(embed=embed)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Nickname update logger
    if before.nick != after.nick:
        log_channel = await helpers.get_or_create_channel(after.guild, "server-logs")
        embed = discord.Embed(
            title="📝 Nickname Changed",
            description=(
                f"**Member:** {after.mention} (`{after}`)\n"
                f"**Before:** {before.nick or before.name}\n"
                f"**After:** {after.nick or after.name}"
            ),
            color=discord.Color.teal(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Server Log")
        embed.set_thumbnail(url=after.display_avatar.url)
        await log_channel.send(embed=embed)
    
    # Role update logger
    if before.roles != after.roles:
        log_channel = await helpers.get_or_create_channel(after.guild, "server-logs")
        before_roles = {r.id for r in before.roles}
        after_roles = {r.id for r in after.roles}

        added_roles = [r.mention for r in after.roles if r.id not in before_roles and r.name != "@everyone"]
        removed_roles = [r.mention for r in before.roles if r.id not in after_roles and r.name != "@everyone"]

        desc = f"**Member:** {after.mention} (`{after}`)\n"
        if added_roles:
            desc += f"➕ **Added Roles:** {', '.join(added_roles)}\n"
        if removed_roles:
            desc += f"❌ **Removed Roles:** {', '.join(removed_roles)}\n"

        embed = discord.Embed(
            title="🎭 Roles Updated",
            description=desc.strip(),
            color=discord.Color.magenta(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Server Log")
        embed.set_thumbnail(url=after.display_avatar.url)
        await log_channel.send(embed=embed)




bot.run(TOKEN)
