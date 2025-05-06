# Import necessary libraries
import discord
import responses
import time
import nltk
nltk.download('vader_lexicon')
from discord.ext import commands
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import defaultdict
import json 
import os
from datetime import timedelta, datetime
from difflib import SequenceMatcher

# Link files
import settings
import responses
import confidential

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Abreviations
bot = commands.Bot(command_prefix="!", intents=intents)
now = time.time()

# Load existing points or initialize new folder
def load_user_points():
    if os.path.exists("user_points.json") and os.path.getsize("user_points.json") > 0:
        try:
            with open("user_points.json", "r") as f:
                data = json.load(f)
                return defaultdict(lambda: 80, {int(k): int(v) for k, v in data.items()})
        except json.JSONDecodeError:
            print("⚠️ Corrupted JSON file. Starting fresh.")
    return defaultdict(lambda: 80)
user_points = load_user_points()

# Function to save points to file
def save_points():
    with open("user_points.json", "w") as f:
        json.dump(user_points, f)

# Dictionary to track the last time a user sent a message
last_message_time = {}
last_message_content = {}

# Helper function to detect similar messages
async def handle_spam(message, uid):
    if uid not in last_message_content:
        last_message_content[uid] = []

    last_message_content[uid] = [
        t for t in last_message_content[uid] 
        if now - t[0] < settings.SPAM_SIMILARITY_THRESHOLD
    ]
    last_message_content[uid].append((now, message.content))
    msgs = last_message_content[uid]

    if len(msgs) >= settings.SPAM_MESSAGE_THRESHOLD:
        # Check if messages are similar
        recent_msgs = [msg for _, msg in msgs[-1*settings.SPAM_MESSAGE_THRESHOLD:]]
        similarities = [
            SequenceMatcher(None, recent_msgs[i], recent_msgs[i+1]).ratio() > settings.SPAM_SIMILARITY_THRESHOLD
            for i in range(len(recent_msgs) - 1)
        ]
        if similarities.count(True) >= len(similarities) // 2:
            last_message_content[uid].clear()
            return -10  # Deduct points for spamming      
    return 0

# Punishment logic
async def punish(member: discord.Member, score: int):
    for i in range(len(settings.PUNISH_THRESHOLDS)):
        if score <= settings.PUNISH_THRESHOLDS[i]:
            try:
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=settings.PUNISHMENT_TIMES[i]), reason="Toxic behavior")
                print(f"{member} has been punished (Social Credit = {score}).")
            except discord.Forbidden:
                print(f"⚠️ Cannot timeout {member}. Missing permissions.")
            return

# Function to handle user points and save them
async def handle_user_points(message, uid):
    change = await handle_spam(message, uid)
    compound = SentimentIntensityAnalyzer().polarity_scores(message.content)['compound']
    if (compound > .5):
        change += 1
    elif (compound < -.5):
        change -= 5
    current_score = user_points.get(uid, 80) + change

    user_points[uid] = max(0, current_score)
    save_points()

    print(f"{message.author.display_name} | Message: {message.content}| Sentiment: {compound:.2f} | Score : {current_score}")

    if change < 0:
        await punish(message.author, current_score)

# Social Credit Board
social_credit_message_id = None
async def update_social_credit_board():
    global social_credit_message_id

    channel = discord.utils.get(bot.get_all_channels(), name="hypathiabot")
    if channel is None:
        print(f"⚠️ #hypathiabot channel not found.")
        return

    # Format leaderboard
    leaderboard = "**📜 Social Credit Scores 📜**\n\n"
    for member_id, score in sorted(user_points.items(), key=lambda x: -x[1]):
        member = channel.guild.get_member(member_id)
        if member:
            leaderboard += f"**{member.display_name}**: {score}/100\n"

    try:
        if social_credit_message_id:
            # Try to edit existing message
            msg = await channel.fetch_message(social_credit_message_id)
            await msg.edit(content=leaderboard)
        else:
            # No saved message, send a new one
            msg = await channel.send(leaderboard)
            social_credit_message_id = msg.id
            with open("social_credit_message_id.txt", "w") as f:
                f.write(str(social_credit_message_id))

    except discord.NotFound:
        # Message was deleted, create a new one
        msg = await channel.send(leaderboard)
        social_credit_message_id = msg.id
        with open("social_credit_message_id.txt", "w") as f:
            f.write(str(social_credit_message_id))
    except discord.HTTPException as e:
        if e.code == 30046:
            print("⚠️ Message edit limit reached. Deleting and resending leaderboard...")
            try:
                # Delete old message and send a new one
                if social_credit_message_id:
                    msg = await channel.fetch_message(social_credit_message_id)
                    await msg.delete()

                new_msg = await channel.send(leaderboard)
                social_credit_message_id = new_msg.id
                with open("social_credit_message_id.txt", "w") as f:
                    f.write(str(social_credit_message_id))
            except Exception as inner_e:
                print(f"❌ Failed to replace leaderboard message: {inner_e}")
        else:
            print(f"⚠️ Failed to update leaderboard: {e}")

# Upon turning bot on
@bot.event
async def on_ready():
    global social_credit_message_id
    # Load social credit message ID if saved
    if os.path.exists("social_credit_message_id.txt"):
        with open("social_credit_message_id.txt", "r") as f:
            try:
                social_credit_message_id = int(f.read().strip())
            except ValueError:
                social_credit_message_id = None
    print(f"✅ Bot is ready! Logged in as {bot.user}")

# Main message logic
@bot.event
async def on_message(message):
    # Make sure bot doesn't get stuck in an infinite loop
    if message.author == bot.user:
        return
    
    # Abbreviation
    uid = message.author.id

    # Update last message time and content
    last_message_time[uid] = now
    
    # Get sentiment and change user scores
    await handle_user_points(message, uid)
    
    # Respond to commands
    await responses.handle_response(message, uid)
    
    # Update social credit board
    await update_social_credit_board()

bot.run(confidential.TOKEN)