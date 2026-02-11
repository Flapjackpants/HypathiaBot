# Settings

# Spam settings
SPAM_TIME_THRESHOLD = 5  # seconds
SPAM_MESSAGE_THRESHOLD = 3  # number of similar messages
SPAM_SIMILARITY_THRESHOLD = 0.8  # similarity ratio for spam detection

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