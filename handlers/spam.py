# handlers/spam.py
from difflib import SequenceMatcher
import settings
from handlers.data import last_message_content
import time

async def handle_spam(message, uid, now):
    if uid not in last_message_content:
        last_message_content[uid] = []

    last_message_content[uid] = [
        t for t in last_message_content[uid] 
        if now - t[0] < settings.SPAM_SIMILARITY_THRESHOLD
    ]
    last_message_content[uid].append((now, message.content))
    msgs = last_message_content[uid]

    if len(msgs) >= settings.SPAM_MESSAGE_THRESHOLD:
        recent_msgs = [msg for _, msg in msgs[-settings.SPAM_MESSAGE_THRESHOLD:]]
        similarities = [
            SequenceMatcher(None, recent_msgs[i], recent_msgs[i+1]).ratio() > settings.SPAM_SIMILARITY_THRESHOLD
            for i in range(len(recent_msgs) - 1)
        ]
        if similarities.count(True) >= len(similarities) // 2:
            last_message_content[uid].clear()
            return -10      
    return 0
