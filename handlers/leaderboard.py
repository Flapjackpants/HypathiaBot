# handlers/leaderboard.py
import discord
from handlers.data import user_points
import os

social_credit_message_id = None

async def clear_channel_messages(channel: discord.TextChannel):
    """Delete ALL messages in the channel, even older than 14 days."""
    async for msg in channel.history(limit=None):
        try:
            await msg.delete()
        except discord.HTTPException as e:
            print(f"⚠️ Failed to delete message {msg.id}: {e}")

async def update_social_credit_board(bot, guild: discord.Guild):
    global social_credit_message_id

    channel = discord.utils.get(guild.text_channels, name="hypathiabot")
    if channel is None or not isinstance(channel, discord.TextChannel):
        print(f"⚠️ #hypathiabot channel not found or is not a text channel.")
        return
    
    print("🧹 Clearing all messages in #hypathiabot...")
    await clear_channel_messages(channel)

    leaderboard = "**📜 Social Credit Scores 📜**\n\n"
    for member_id, score in sorted(user_points.items(), key=lambda x: -x[1]):
        member = channel.guild.get_member(member_id)
        if member:
            leaderboard += f"**{member.display_name}**: {score}/100\n"

    try:
        if social_credit_message_id:
            msg = await channel.fetch_message(social_credit_message_id)
            await msg.edit(content=leaderboard)
        else:
            msg = await channel.send(leaderboard)
            social_credit_message_id = msg.id
            with open("social_credit_message_id.txt", "w") as f:
                f.write(str(social_credit_message_id))
    except discord.NotFound:
        msg = await channel.send(leaderboard)
        social_credit_message_id = msg.id
        with open("social_credit_message_id.txt", "w") as f:
            f.write(str(social_credit_message_id))
    except discord.HTTPException as e:
        print(f"⚠️ Failed to update leaderboard: {e}")
