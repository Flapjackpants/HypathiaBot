# handlers/messageAnalysis.py
from handlers.data import user_points, save_points, track_user_message
from handlers.punish import punish
import re
import settings


def _is_blank_message(message):
    """Messages with only attachments, stickers, embeds, etc. (no text)."""
    return not (message.content or "").strip()


def _contains_banned_word(content):
    lower = content.lower()
    for word in settings.BANNED_WORDS:
        if word and word.lower() in lower:
            return True
    return False


async def handle_moderation(message, uid, now):
    if message.author.bot or any(role.name.lower() == "bot" for role in message.author.roles):
        return 0

    content = message.content.lower().strip()
    if content.startswith(settings.WHITELISTED_COMMANDS) or content.startswith(settings.COMMAND_PREFIXES):
        return 0

    # Rate limit: count every message kind (including blank/image-only)
    message_count = track_user_message(uid, message, now)
    if message_count >= settings.RATE_LIMIT_MESSAGE_THRESHOLD:
        return settings.RATE_LIMIT_PENALTY

    # Blank messages do not trigger content-based punishment
    if _is_blank_message(message):
        return 0

    if _contains_banned_word(message.content):
        return settings.BANNED_WORD_PENALTY

    links = re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        message.content,
    )
    if len(message.mentions) > settings.MAX_MENTIONS or len(links) > settings.MAX_LINKS:
        return settings.MENTION_LINK_PENALTY

    return 0


async def handle_user_points(message, uid, now):
    print(f"{message.author.display_name} | Message: {message.content}|")

    change = await handle_moderation(message, uid, now)
    current_score = user_points.get(uid, 80) + change
    print(f"New Score: {current_score}")

    user_points[uid] = max(0, current_score)
    save_points()

    if change < 0:
        await punish(message.author, current_score)
