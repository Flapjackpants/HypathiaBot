# handlers/accountAge.py
import discord
from datetime import timedelta
import settings


def _account_age(member: discord.Member | discord.User) -> timedelta:
    return discord.utils.utcnow() - member.created_at


def is_account_too_young(member: discord.Member | discord.User) -> bool:
    if not settings.NEW_ACCOUNT_BAN_ENABLED or member.bot:
        return False
    return _account_age(member) < timedelta(days=settings.NEW_ACCOUNT_MIN_AGE_DAYS)


async def handle_new_account_join(member: discord.Member) -> bool:
    """Ban the member if their Discord account is too new. Returns True if banned."""
    if not is_account_too_young(member):
        return False

    age = _account_age(member)
    reason = (
        f"Account too new (created {age.days} days ago, "
        f"minimum {settings.NEW_ACCOUNT_MIN_AGE_DAYS} days)"
    )
    try:
        await member.ban(reason=reason, delete_message_days=0)
        print(f"Banned {member} ({member.id}): {reason}")
        return True
    except discord.Forbidden:
        print(f"⚠️ Cannot ban {member}. Missing Ban Members permission.")
        return False
