# handlers/punish.py
import discord
from datetime import timedelta
import settings

async def punish(member: discord.Member, score: int):
    for i, threshold in enumerate(settings.PUNISH_THRESHOLDS):
        if score <= threshold:
            try:
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=settings.PUNISHMENT_TIMES[i]), reason="Toxic behavior")
                print(f"{member} has been punished (Social Credit = {score}).")
            except discord.Forbidden:
                print(f"⚠️ Cannot timeout {member}. Missing permissions.")
            return
