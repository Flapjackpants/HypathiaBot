# handlers/leaderboard.py
import discord
from handlers.data import user_points

hypathiabot_channel = None

async def update_social_credit_board(bot, guild: discord.Guild):
    hypathiabot_channel = discord.utils.get(guild.text_channels, name="hypathiabot")

    # Check if HypathiaBot channel exists
    if hypathiabot_channel is None:
        print("🛠️ #hypathiabot channel not found. Creating it at the top...")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False)
        }
        # Create the channel
        hypathiabot_channel = await guild.create_text_channel(
            "hypathiabot",
            overwrites=overwrites,
            position=0  # Place it at the top of the channel list
        )
    
    # Build the leaderboard content
    leaderboard = "# **📜 Social Credit Scores 📜**\n\n"
    for member_id, score in sorted(user_points.items(), key=lambda x: -x[1]):
        member = hypathiabot_channel.guild.get_member(member_id)
        if member:
            leaderboard += f"**{member.display_name}**: {score}/100\n"

    # Find and edit the leaderboard message, or send a new one if it doesn't exist or is rate limited
    save_msg = None
    async for msg in hypathiabot_channel.history(limit=10):
        if (msg.author == bot.user and msg.content.startswith("# **📜 Social Credit Scores 📜**\n\n")):
                try:
                    await msg.edit(content=leaderboard)
                    save_msg = msg.id
                    break
                except discord.HTTPException as e:
                    print(f"⚠️ Failed to edit leaderboard, sending new one: {e}")
                    break  # Will fall through to sending new one
    
    # If not found or failed → send a new message
    if save_msg is None:
        try:
            new_msg = await hypathiabot_channel.send(leaderboard)
            save_msg = new_msg.id
        except discord.HTTPException as e:
            print(f"⚠️ Failed to send leaderboard: {e}")

    # Clear the hypathiabot channel 
    async for msg in hypathiabot_channel.history(limit=None):
        if msg.id != save_msg:
            try:
                await msg.delete()
            except discord.HTTPException as e:
                print(f"⚠️ Failed to delete message {msg.id}: {e}")