import discord

# Get a channel by name or create it if it doesn't exist
async def get_or_create_channel(guild: discord.Guild, name: str) -> discord.TextChannel:
    channel = discord.utils.get(guild.text_channels, name=name)
    if channel is None:
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False)
            }
            channel = await guild.create_text_channel(name, overwrites=overwrites, position=0)
        except discord.HTTPException as e:
            print(f"⚠️ Failed to create channel '{name}': {e}")
            return None
    return channel