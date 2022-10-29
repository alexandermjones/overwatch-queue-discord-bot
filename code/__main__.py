# Standard imports
from os import getenv

# Third party imports
from dotenv import load_dotenv

# Local imports
from discord_bot import Queue_Bot

# Load in Discord token.
load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')

# Create bot and run.
bot = Queue_Bot(command_prefix='!')
bot.run(TOKEN)