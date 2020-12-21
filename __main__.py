from dotenv import load_dotenv

# Load in Discord token.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

# Run the bot.
while not input():
    bot.run(TOKEN)