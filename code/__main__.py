from dotenv import load_dotenv
from discord_bot import Queue_Bot
from os import getenv

# Load in Discord token.
load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')

# Create bot and run.
bot = Queue_Bot(command_prefix='!')
bot.run(TOKEN)