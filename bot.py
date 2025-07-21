import discord
from discord.ext import commands
from datetime import datetime
import time
import os

import confidential
import responses
from handlers.data import last_message_time
from handlers.sentiment import handle_user_points
from handlers.leaderboard import update_social_credit_board
from handlers.chatBot import handle_chat_bot

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
now = time.time()

@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")
    # Load social credit message ID if saved
    from handlers.leaderboard import social_credit_message_id
    if os.path.exists("social_credit_message_id.txt"):
        with open("social_credit_message_id.txt", "r") as f:
            try:
                social_credit_message_id = int(f.read().strip())
            except ValueError:
                pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    uid = message.author.id
    last_message_time[uid] = now

    await handle_user_points(message, uid, now)
    await responses.handle_response(message, uid)
    await update_social_credit_board(bot)
    await handle_chat_bot(bot ,message)

bot.run(confidential.TOKEN)
