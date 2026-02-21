import random
import discord
import os
from dotenv import load_dotenv
from openai import OpenAI
import settings

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# Fetch a list of the last limit number of messages from the current channel
async def fetch_recent_messages(channel: discord.TextChannel, limit=settings.CHAT_BOT_FETCH_LIMIT) -> list[str]:
    messages = []
    async for msg in channel.history(limit=limit):
        if msg.author.bot:
            continue
        # Convert each message into a readable string
        messages.append(f"{msg.author.display_name}: {msg.content}")
    # Reverse to chronological order
    messages.reverse()
    return messages

# Generate a response based on the conversation history
async def generate_response(history: list[str]) -> str:

    prompt = "The following is a conversation history:\n\n"
    prompt += "\n".join(history)
    prompt += "\n\nRespond to the last message in a relevant sarcastic and snarky manner, using the message history to imitate the style of a member of the server. Keep track of which messages were sent by which server members directed at whom. Never repeat the contents of the message or including unessesary content like 'Oh' or 'Ah' at the start of the message. Process requests in a timely manner and avoid long responses. Keep the response concise and to the point. Refer to the internet for any queries regarding information outside the server.\n\n"

    try:
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a Discord Bot named HypathiaBot designed to monitor and police Discord servers. You are fiercely patriotic for the server Susland, and you have a disdain for people named Ethan."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ generate_response failed: {e}")
        return "generate_response failed"

# Handle incoming messages and respond conditionally
async def handle_chat_bot(bot, message: discord.Message):
    
    if message.author.bot:
        return

    mentioned = bot.user in message.mentions
    random_chance = (random.randint(1, 100) <= settings.CHAT_BOT_RESPONSE_CHANCE)

    if settings.CHAT_BOT_ENABLED and (mentioned or random_chance):
        # Fetch recent messages and respond
        history = await fetch_recent_messages(message.channel, limit=settings.CHAT_BOT_FETCH_LIMIT)
        response = await generate_response(history)
        await message.channel.send(response)
    