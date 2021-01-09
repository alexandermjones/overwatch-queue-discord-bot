from dotenv import load_dotenv
from discord_bot import create_bot

# Load in Discord token.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot and run.
bot = create_bot()
bot.run(TOKEN)