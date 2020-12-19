"""
Discord bot to implement the Overwatch Queue from overwatch_order.py.
"""

# Standard library imports
import os
import emoji

# Local import
from overwatch_order import create_queue, find_player, Player, Overwatch_Queue

# Third party imports
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load in Discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv(emoji.emojize('DISCORD_GUILD'))

# Create bot
bot = commands.Bot(command_prefix='!')

# Create global variables
queue = False
queue_created = False

# Start queue when requested
@bot.command(name='queue', help='Starts an Overwatch queue.')
async def start_queue(ctx):
    global queue
    if not queue:
        queue, response = create_queue(ctx.message.author.name)
    else:
        response = "A queue already exists. Type \'!join\' to join the queue."
    await ctx.send(response)


# Join queue when requested
@bot.command(name='join', help='Join the Overwatch queue.')
async def join_queue(ctx):
    global queue
    if not queue:
        queue, response = create_queue(ctx.message.author.name)
    elif find_player(queue, ctx.message.author.name) in queue.players:
        response = f"{ctx.message.author.name} is already a member of the queue."
    else:
        queue.add_player(Player(ctx.message.author.name))
        response = f"{ctx.message.author.name} has been added to the queue."
    await ctx.send(response)


# Leave queue when requested
@bot.command(name='leave', help='Leave the Overwatch queue.')
async def leave_queue(ctx):
    global queue
    queue.delete_player(find_player(queue, ctx.message.author.name))
    response = f"{ctx.message.author.name} have been removed from the queue."
    await ctx.send(response)


# Switch to the next game
@bot.command(name='next', help='Update the queue for the next game.')
async def next_game_for_queue(ctx):
    global queue
    response = queue.update_queue()
    await ctx.send(response)


# See the status of the queue
@bot.command(name='status', help='See the status of the queue.')
async def status_queue(ctx):
    global queue
    if not queue:
        response = "There is no queue. Type \'!queue\' to create one."
    else:
        response = queue.print_players()
    await ctx.send(response)


# See the wait of a player
@bot.command(name='wait', help='See how long until your next game.')
async def status_queue(ctx):
    global queue
    player = find_player(queue, ctx.message.author.name)
    if not queue:
        response = "There is no queue. Type \'!queue\' to create one."
    elif player:
        response = queue.print_player_wait(player)
    else:
        response = f"{ctx.message.author.name} is not a member of the queue. Type \'!join\' to join the queue."
    await ctx.send(response)


bot.run(TOKEN)

