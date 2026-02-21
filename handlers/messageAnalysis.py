# handlers/sentiment.py
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from handlers.data import user_points, save_points
from handlers.punish import punish
import re
from difflib import SequenceMatcher
import settings
from handlers.data import last_message_content
import time

# Message sentiment analysis
# analyzer = SentimentIntensityAnalyzer()
# async def sentiment_score(message):
#     compound = analyzer.polarity_scores(message.content)['compound']
#     print(f"Sentiment: {compound:.2f}")
#     if compound > settings.SENTIMENT_POSITIVE_THRESHOLD:
#         return 1
#     elif compound < settings.SENTIMENT_NEGATIVE_THRESHOLD:
#         return -3
#     return 0

# Message spam analysis
async def handle_spam(message, uid, now):
    # Ignore any users with the role "bot"
    if message.author.bot or any(role.name.lower() == "bot" for role in message.author.roles):
        return 0

    # Skip if it's a specific whitelisted command OR starts with a common prefix
    content = message.content.lower().strip()
    if content.startswith(settings.WHITELISTED_COMMANDS) or content.startswith(settings.COMMAND_PREFIXES):
        return 0

    if uid not in last_message_content:
        last_message_content[uid] = []

    last_message_content[uid] = [
        t for t in last_message_content[uid] 
        if now - t[0] < settings.SPAM_SIMILARITY_THRESHOLD
    ]
    last_message_content[uid].append((now, message.content))
    msgs = last_message_content[uid]

    # Check for mass ping or link spam
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
    if len(message.mentions) > settings.MAX_MENTIONS or len(links) > settings.MAX_LINKS:
        return -15

    if len(msgs) >= settings.SPAM_MESSAGE_THRESHOLD:
        recent_msgs = [msg for _, msg in msgs[-settings.SPAM_MESSAGE_THRESHOLD:]]

        # Between recent messages, check similarity between them
        similarities = [
            SequenceMatcher(None, recent_msgs[i], recent_msgs[i+1]).ratio() > settings.SPAM_SIMILARITY_THRESHOLD
            for i in range(len(recent_msgs) - 1)
        ]
        print(f"Spam similarities: {similarities}")
        # If more than half of the recent messages are similar, treat as spam
        if similarities.count(True) >= len(similarities) // 2:
            last_message_content[uid].clear()
            return -10      
    return 0

# Handle all the user points logic
async def handle_user_points(message, uid, now):
    print(f"{message.author.display_name} | Message: {message.content}|")
    
    # Sum points from all analyses
    # change = await sentiment_score(message) + await handle_spam(message, uid, now) deprecated code for SCS trollage
    change = await handle_spam(message, uid, now)
    current_score = user_points.get(uid, 80) + change
    print(f"New Score: {current_score}")

    # Save score into JSON
    user_points[uid] = max(0, current_score)
    save_points()

    if change < 0:
        await punish(message.author, current_score)