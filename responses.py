import discord
import bot
import confidential

async def handle_response(message: discord.Message, uid):
    # Set up the content of the message
    content = message.content.strip().lower()

    # Help command
    if content == '/help':
        await message.channel.send('HypathiaBot is a fun community bot created by Maxwell "FJP" Li. ' \
        '\n\nHere are my commands: ' \
        '\n> /help ' \
        '\n> /points')

    # Points command
    if content == '/points':
        await message.channel.send(f"{message.author.display_name} has a sentiment score of {bot.user_points.get(uid, 80)}/100")

    # Legacy Squing Nuke
    # if content == confidential.LAUNCH_COMMAND:
    #     print('Nuclear warhead initiated')
    #     for member in bot.get_all_members():
    #         try:
    #             await member.ban(reason="Squing Nuke", delete_message_days=9999)
    #             print(f"Banned {member.display_name}!")
    #         except:
    #             print(f"Failed to Ban {member.display_name}")
    #     print("Nuking is complete!")
    #     await bot.send('https://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464831')