"""
Discord bot to implement the Overwatch Queue from overwatch_order.py.
"""

# Standard library imports.
import os

# Local import
from overwatch_queue import create_queue, find_player, Player, Overwatch_Queue
from battlenet_interface import Battlenet_Account
from storage_layer import Storage

# Third party imports.
import discord
from discord.ext import commands
from dotenv import load_dotenv
import emoji


# Load in Discord token.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Load in Guild name - use emojize in case of emoji in the name.
GUILD = os.getenv(emoji.emojize('DISCORD_GUILD'))

# Create bot
bot = commands.Bot(command_prefix='!')

# Create global variables
queue = False
queue_created = False

db = Storage()

# Associate a discord username with a battlenet tag
@bot.command(name='link', help='Link a discord name to a battle net account')
async def store_link(ctx, name: str):
    """Stores the battle net name against the discord user name.
    Checks for uniqueness and profile state offers a warning if not unique and profile not public
    name -- the battlenet name with format DisplayName#0000    
    """
    acc = Battlenet_Account(name)
    pub_chk = await acc.public_check
    response = ''
    if(acc.valid_battletag and pub_chk ):
        await db.upsert_player(ctx.message.author.name, name)
        response += f"{ctx.message.author.name} is now linked to {name}"
    else:
        response += f"Something went wrong with error/s:\n {acc.error}"

    await ctx.send(response)
    

"""
The commands that can be given to the bot.
"""


# Start queue when requested.
@bot.command(name='queue', help='Starts an Overwatch queue.')
async def start_queue(ctx):
    global queue
    if not queue:
        queue, response = create_queue(ctx.message.author.name)
    else:
        response = "A queue already exists. Type \'!join\' to join the queue."
    await ctx.send(response)


# Join queue when requested.
@bot.command(name='join', help='Join the Overwatch queue.')
async def join_queue(ctx):
    global queue
    if not queue:
        queue, response = create_queue(ctx.message.author.name)
    elif find_player(queue, ctx.message.author.name):
        response = f"{ctx.message.author.name} is already in the queue."
    else:
        response = queue.add_player(Player(ctx.message.author.name))
    await ctx.send(response)
    

# Leave queue when requested.
@bot.command(name='leave', help='Leave the Overwatch queue.')
async def leave_queue(ctx):
    global queue
    if not queue:
        response = "There is no queue. Type \'!queue\' to create one."
    else:
        queue.delete_player(find_player(queue, ctx.message.author.name))
        response = f"{ctx.message.author.name} have been removed from the queue."
    await ctx.send(response)


# Switch to the next game.
@bot.command(name='next', help='Update the queue for the next game.')
async def next_game_for_queue(ctx):
    global queue
    if not queue:
        response = "There is no queue. Type \'!queue\' to create one."
    else:
        response = queue.update_queue()
    await ctx.send(response)


# See the status of the queue.
@bot.command(name='status', help='See the status of the queue.')
async def status_queue(ctx):
    global queue
    if not queue:
        response = "There is no queue. Type \'!queue\' to create one."
    else:
        response = queue.print_players()
    await ctx.send(response)


# See the wait of a player.
@bot.command(name='wait', help='See how long until your next game.')
async def wait_queue(ctx):
    global queue
    player = find_player(queue, ctx.message.author.name)
    if not queue:
        response = "There is no queue. Type \'!queue\' to create one."
    elif player:
        response = queue.print_player_wait(player)
    else:
        response = f"{ctx.message.author.name} is not a member of the queue. Type \'!join\' to join the queue."
    await ctx.send(response)


# End the queue.
@bot.command(name='end', help='End (remove) the current queue.')
async def end_queue(ctx):
    global queue
    if not queue:
        response = "There is no queue to end."
    else:
        queue = False
        response = "The queue has been ended. Type \'!queue\' to start a new queue."
    await ctx.send(response)

# Run the bot.
while not input():
    bot.run(TOKEN)

