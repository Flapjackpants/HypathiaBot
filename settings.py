# Settings

# Auto-moderation settings
RATE_LIMIT_TIME_THRESHOLD = 5  # seconds — window for counting messages
RATE_LIMIT_MESSAGE_THRESHOLD = 8  # max messages (any kind) allowed in that window
RATE_LIMIT_PENALTY = -10  # social credit change when rate limit is exceeded
MAX_MENTIONS = 5
MAX_LINKS = 3
MENTION_LINK_PENALTY = -15  # social credit change for mass pings or link spam
BANNED_WORDS = ("** **", "﷽")  # words/phrases that trigger immediate punishment (case-insensitive)
BANNED_WORD_PENALTY = -20  # social credit change when a banned word is used
COMMAND_PREFIXES = ("-", "!", "/")
WHITELISTED_COMMANDS = ("-random", "-caption", "-speed")

# Sentiment analysis settings
SENTIMENT_POSITIVE_THRESHOLD = 0.5  # threshold for positive sentiment
SENTIMENT_NEGATIVE_THRESHOLD = -0.5  # threshold for negative sentiment

# Punishment settings
PUNISH_THRESHOLDS = [0, 30, 40, 50, 60, 70]  # Social Credit thresholds for punishment
PUNISHMENT_TIMES = [345600, 86400, 21600, 3600, 1800, 600]  # Punishment times in seconds for each threshold

# Chat bot settings
CHAT_BOT_ENABLED = True  # Enable or disable the chat bot
CHAT_BOT_RESPONSE_CHANCE = 1  # Percentage chance to respond to a message
CHAT_BOT_FETCH_LIMIT = 10  # Number of recent messages to fetch for chat bot responses