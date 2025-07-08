# handlers/sentiment.py
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from handlers.data import user_points, save_points
from handlers.spam import handle_spam
from handlers.punish import punish

analyzer = SentimentIntensityAnalyzer()

async def handle_user_points(message, uid, now):
    change = await handle_spam(message, uid, now)
    compound = analyzer.polarity_scores(message.content)['compound']
    
    if compound > 0.5:
        change += 1
    elif compound < -0.5:
        change -= 3

    current_score = user_points.get(uid, 80) + change
    user_points[uid] = max(0, current_score)
    save_points()

    print(f"{message.author.display_name} | Message: {message.content}| Sentiment: {compound:.2f} | Score : {current_score}")

    if change < 0:
        await punish(message.author, current_score)
