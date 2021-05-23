"""
Discord bot to implement the Overwatch Queue from overwatch_order.py.
"""

# Standard library imports.
import os

# Local import
from overwatch_queue import Player, Overwatch_Queue
from battlenet_interface import Battlenet_Account
from storage_layer import Storage

# Third party imports.
from discord.ext import commands

# Create global variables
db = Storage()

class Overwatch_Bot(commands.Bot):
    """
    Class for Overwatch Discord Bot, inherits from a Discord bot with
    an added Overwatch_Queue object attached.

    :param commands.Bot Discord class for an Overwatch bot
    """

    def __init__(self, command_prefix: str):
        """
        Initialises the Overwatch_Bot

        :param command_preix (str) The character that identifies a message as a command to the bot.
        """
        super().__init__(command_prefix=command_prefix)
        self.queue = Overwatch_Queue()
        self.no_queue_response = "There is no queue. Type \'!queue\' to create one."


def create_bot() -> Overwatch_Bot:
    """
    Create the Overwatch queue bot and give it all the commands.

    Returns:
        bot (Overwatch_Bot): A bot initialised with all the commands we need.
    """
    bot = Overwatch_Bot(command_prefix='!')

    # The commands that can be given to the bot.

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


    # Start queue when requested.
    @bot.command(name='queue', help='Starts an Overwatch queue.')
    async def start_queue(ctx):
        message = "A queue already exists.\n" if bot.queue.players else ""
        if bot.queue.find_player(ctx.message.author.name):
            response = message + f"{ctx.message.author.name} is already in the queue."
        else:
            message = bot.queue.add_player(Player(ctx.message.author.name))
            response = "Overwatch queue has been created. Type \'!join\' to be added to the queue.\n" + message
        await ctx.send(response)


    # Join queue when requested.
    @bot.command(name='join', help='Join the Overwatch queue.')
    async def join_queue(ctx):
        message = "Overwatch queue has been created. Type \'!join\' to be added to the queue.\n" if not bot.queue.players else ""
        if bot.queue.find_player(ctx.message.author.name):
            response = f"{ctx.message.author.name} is already in the queue."
        else:
            response = message + bot.queue.add_player(Player(ctx.message.author.name))
        await ctx.send(response)


    # Leave queue when requested.
    @bot.command(name='leave', help='Leave the Overwatch queue.')
    async def leave_queue(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            player = bot.queue.find_player(ctx.message.author.name)
            if player:
                bot.queue.delete_player(player)
                response = f"{ctx.message.author.name} has been removed from the queue."
            else:
                response = f"{ctx.message.author.name} was not in the queue."
        await ctx.send(response)


    # Switch to the next game.
    @bot.command(name='next', help='Update the queue for the next game.')
    async def next_game_for_queue(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            response = bot.queue.update_queue()
        await ctx.send(response)


    # See the status of the queue.
    @bot.command(name='status', help='See the status of the queue.')
    async def status_queue(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            response = bot.queue.print_players()
        await ctx.send(response)


    # See the wait of a player.
    @bot.command(name='wait', help='See how long until your next game.')
    async def wait_queue(ctx):
        player = bot.queue.find_player(ctx.message.author.name)
        if not bot.queue.players:
            response = bot.no_queue_response
        elif player:
            response = bot.queue.print_player_wait(player)
        else:
            response = f"{ctx.message.author.name} is not a member of the queue. Type \'!join\' to join the queue."
        await ctx.send(response)

    
    # Add a player to the queue.
    @bot.command(name='add', help='Add a player to the queue.')
    async def kick_player(ctx, arg=""):
        message = "Overwatch queue has been created. Type \'!join\' to be added to the queue.\n" if not bot.queue.players else ""
        if bot.queue.find_player(arg):
            response = f"{arg} is already in the queue."
        else:
            response = message + bot.queue.add_player(Player(arg))
        if not arg:
            response = "Type \'!add \' followed by the Discord name of the player to add them."
        await ctx.send(response)


    # Kick a player from the queue.
    @bot.command(name='kick', help='Remove a player from the queue.')
    async def kick_player(ctx, arg=""):
        if not bot.queue.players:
            response = bot.no_queue_response
        elif not arg:
            response = "Type \'!kick \' followed by the Discord name of the player to remove them."
        else:
            player = bot.queue.find_player(arg)
            if player:
                bot.queue.delete_player(player)
                response = f"{arg} has been removed from the queue."
            else:
                response = f"{arg} is not a player in the queue."
        await ctx.send(response)

    
    # Delay your position in the queue when requested.
    @bot.command(name='delay', help='Temporarily no longer join current players until rejoined.')
    async def delay_player(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            player = bot.queue.find_player(ctx.message.author.name)
            if player:
                message = bot.queue.delay_player(player)
                response = f"{ctx.message.author.name} is now delaying their games. Type \'!rejoin\' to stop."
                response += ("\n\n" + message)
            else:
                response = f"{ctx.message.author.name} is not a player in the queue."
        await ctx.send(response)

    
    # Rejoin your position in the queue after delaying.
    @bot.command(name='rejoin', help='Stop delaying games and be able to join current players again.')
    async def rejoin_player(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            player = bot.queue.find_player(ctx.message.author.name)
            if player and player.delaying:
                message = bot.queue.rejoin_player(player)
                response = f"{ctx.message.author.name} is no longer delaying their games."
                response += ("\n\n" + message)
            elif player and not player.delaying:
                response = f"{ctx.message.author.name} was not delaying games."
            else:
                response = f"{ctx.message.author.name} is not a player in the queue."
        await ctx.send(response)


    # Undo the previous command
    @bot.command(name='undo', help='Undo the previous command issued.')
    async def undo_queue(ctx):
        message = bot.queue.undo_command()
        response = "Previous command has been undone. The status of the queue now is:\n\n"
        response = response + message
        await ctx.send(response)
        

    # End the queue.
    @bot.command(name='end', help='End (empty) the current queue.')
    async def end_queue(ctx):
        if not bot.queue.players:
            response = "There is no queue to end (the queue has already been ended)."
        else:
            bot.queue.empty_queue()
            response = "The queue has been ended. Type \'!queue\' to start a new queue."
        await ctx.send(response)

    
    # Error handling
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements.**')
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("**There was aconnection error somewhere, why don't you try again in a few seconds?**")
            
        
    print("Bot created")
    return bot
