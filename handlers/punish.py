# handlers/punish.py
import discord
from datetime import timedelta
import settings
from handlers.data import pop_tracked_messages


async def _delete_messages(messages):
    for msg in messages:
        try:
            await msg.delete()
        except discord.NotFound:
            pass
        except discord.Forbidden:
            print(f"⚠️ Cannot delete message {msg.id} in #{msg.channel}.")


async def punish(member: discord.Member, score: int):
    messages = pop_tracked_messages(member.id)
    if messages:
        await _delete_messages(messages)
        print(f"Deleted {len(messages)} message(s) from {member}.")

    for i, threshold in enumerate(settings.PUNISH_THRESHOLDS):
        if score <= threshold:
            try:
                await member.timeout(
                    discord.utils.utcnow() + timedelta(seconds=settings.PUNISHMENT_TIMES[i]),
                    reason="Toxic behavior",
                )
                print(f"{member} has been punished (Social Credit = {score}).")
            except discord.Forbidden:
                print(f"⚠️ Cannot timeout {member}. Missing permissions.")
            return
