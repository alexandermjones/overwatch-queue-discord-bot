"""
Discord bot to implement the Overwatch Queue from overwatch_order.py.
"""

# Standard library imports.
import json
import os
from pathlib import Path

# Local import
from queue import Player, Game_Queue
from battlenet_interface import Battlenet_Account
from patch_scraper import Overwatch_Patch_Scraper
from storage_layer import Storage

# Third party imports.
from discord.ext import commands, tasks

# Create global variables
db = Storage()

class Queue_Bot(commands.Bot):
    """
    Class for a Queue Discord Bot.
    
    Inherits from a Discord bot with commands for starting and interacting with queues.

    Non-inherited attributes:
        queues (dict): The dictionary of queue names and corresponding Game_Queue objects.
        no_queue_response (str): The default response for there not being a queue.
        queue_not_specified (str): The default response when the queue name cannot be inferred.
    """

    def __init__(self, command_prefix: str):
        """
        Initialises the Queue_Bot.

        Args:
            command_prefix (str): The character that identifies a message as a command to the bot.
        """
        super().__init__(command_prefix=command_prefix, 
                         help_command=commands.DefaultHelpCommand(no_category='Commands'))
        self.queues = dict()
        self.NO_GAME_PARAM_RESPONSE = "Game to interact with cannot be identified. Please enter it after the command."
        self.NO_PLAYERCUTOFF_PARAM_RESPONSE = "No player count data exists for that game. Please enter it after the game name in the command."
        self.NO_QUEUE_RESPONSE = "There is no queue. Type \'!queue [game] [player_number]\' to create one."
        self.game_dict_fpath = Path("db") / "game_dict.json"
        # Create a game dictionary if one isn't present already
        if not self.game_dict_fpath.exists():
            with open(self.game_dict_fpath, 'w') as f:
                json.dump({}, f)
        with open(self.game_dict_fpath) as f:
            self.game_dict = json.load(f)
        
        # TODO separate these out into a new bot
        self.scraper = Overwatch_Patch_Scraper()
        self.patch_channel_fpath = os.path.join("db", "patchchannels")
        if not os.path.exists(self.patch_channel_fpath):
            Path(self.patch_channel_fpath).touch()

    """
    Private class methods.
    """
    def get_patch_channels(self):
        """
        Gets the current patch channels

        Returns:
            list
        """
        with open(self.patch_channel_fpath, "r") as f:
            current_patch_channels = f.readlines()
        return current_patch_channels


    def __update_player_cutoff(self, game_name: str, player_cutoff: int) -> None:
        """
        DOCSTRING
        """
        self.game_dict[game_name] = player_cutoff
        with open(self.game_dict_fpath, 'w') as f:
            json.dump(self.game_dict, f)
        return

    
    def __check_and_lower_game_name_param(self, game_name: str):
        """
        DOCSTRING
        """
        if game_name:
            return game_name.lower()
        elif len(self.queues) == 1:
            return list(self.queues.keys())[0].lower()
        else:
            return ""

    
    def __check_player_cutoff_param(self, game_name: str, player_cutoff: int):
        """
        DOCSTRING
        """
        try:
            assert game_name in self.queues.keys()
        except:
            raise ValueError(f"Game named: \'{game_name}\' is not in the queue.")
        if game_name in self.game_dict:
            db_player_cutoff = self.game_dict[game_name]
            if not player_cutoff:
                player_cutoff = db_player_cutoff
            if player_cutoff != db_player_cutoff:
                self.__update_player_cutoff(game_name, player_cutoff)
        return player_cutoff


    # Start queue when requested.
    @commands.hybrid_command(name='queue', 
                             aliases=['join'],
                             help='Join a Game Queue for the given game_name, start queue if none exists.')
    async def start_queue(self, ctx: commands.Context, game_name: str="", player_cutoff: int=0):
        """
        DOCSTRING HERE
        """
        lower_game_name = self.__check_and_lower_game_name_param(self, game_name)
        if not lower_game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        elif lower_game_name in self.queues.keys():
            response = self.queues[lower_game_name].add_player(Player(ctx.message.author.name))
        else:
            player_cutoff = self.__check_player_cutoff_param(lower_game_name, player_cutoff)
            if not player_cutoff:
                response = self.NO_PLAYERCUTOFF_PARAM_RESPONSE
            else:
                self.queues[game_name] = Game_Queue(game_name, player_cutoff)
                roles = ctx.guild.roles
                for role in roles:
                    if lower_game_name in role.name.lower and role.mentionable:
                        game_name = role.mention
                response = f"Queue has been created for {game_name}.\n"
                response += self.queues[lower_game_name].add_player(Player(ctx.message.author.name))
        await ctx.send(response)


    # Leave queue when requested.
    @commands.command(name='leave', help='Leave the Overwatch queue.')
    async def leave_queue(ctx: commands.Context, game_name: str=""):
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
    @commands.command(name='next', help='Update the queue for the next game.')
    async def next_game_for_queue(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            response = bot.queue.update_queue()
        await ctx.send(response)


    # See the status of the queue.
    @commands.command(name='status', help='See the status of the queue.')
    async def status_queue(ctx):
        if not bot.queue.players:
            response = bot.no_queue_response
        else:
            response = bot.queue.print_players()
        await ctx.send(response)


    # See the wait of a player.
    @commands.command(name='wait', help='See how long until your next game.')
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
    @commands.command(name='add', help='Add a player to the queue.')
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
    @commands.command(name='kick', help='Remove a player from the queue.')
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
    @commands.command(name='delay', help='Temporarily no longer join current players until rejoined.')
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
    @commands.command(name='rejoin', help='Stop delaying games and be able to join current players again.')
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
    @commands.command(name='undo', help='Reset the queue to the previous state.')
    async def undo_queue(ctx):
        message = bot.queue.undo_command()
        response = "Previous command has been undone. The status of the queue now is:\n\n"
        response = response + message
        await ctx.send(response)


    # Change between Overwatch 1 and 2
    @commands.command(name='game', help='Switch the queue between Overwatch 1 and Overwatch 2.')
    async def switch_queue(ctx, arg=""):
        if arg == "1":
            bot.queue.player_cutoff = 6
            response = "Switching to a queue of 6 players for Overwatch 1."
        elif arg == "2":
            bot.queue.player_cutoff = 5
            response = "Switching to a queue of 5 players for Overwatch 2."
        else:
            response = "Type \'!game \' followed by \'1\' or \'2\' to swtich between Overwatch 1 or 2."
        await ctx.send(response)    
        

    # End the queue.
    @commands.command(name='end', help='End (empty) the current queue.')
    async def end_queue(ctx):
        if not bot.queue.players:
            response = "There is no queue to end (the queue has already been ended)."
        else:
            bot.queue.empty_queue()
            response = "The queue has been ended. Type \'!queue\' to start a new queue."
        await ctx.send(response)

    
    # Ask for patches to be posted into this channel
    @commands.command(name='patchnotes', help='The bot will post Overwatch patch notes to this channel.')
    async def add_patch_channel(ctx: commands.Context):
        current_patch_channels = bot.get_patch_channels()
        current_channel = str(ctx.channel.id)
        if current_channel in current_patch_channels:
            response = "This channel already has patches posted here."
        else:
            current_patch_channels.append(current_channel)
            with open(bot.patch_channel_fpath, "w") as f:
                f.writelines(current_patch_channels)
            response = "This channel will now have patches posted here."
        await ctx.send(response)


    # Ask for patches to stop being posted into this channel
    @commands.command(name='stoppatchnotes', help='The bot will stop posting Overwatch patch notes to this channel.')
    async def remove_patch_channel(ctx: commands.Context):
        current_patch_channels = bot.get_patch_channels()
        current_channel = str(ctx.channel.id)
        current_patch_channels.remove(current_channel)
        with open(bot.patch_channel_fpath, "w") as f:
            f.writelines(current_patch_channels)
        response = "This channel will no longer have patches posted here."
        await ctx.send(response)

    
    # Error handling for commands
    @commands.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements.**')
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("**There was aconnection error somewhere, why don't you try again in a few seconds?**")


    # Check for any new patch each hour
    @tasks.loop(hours=1)
    async def check_patch(self):
        if self.scraper.check_for_new_live_patch():
            messages = bot.scraper.prepare_new_live_patch_notes()
            for message in messages:
                for patch_channel in bot.get_patch_channels():
                    await bot.get_channel(int(patch_channel)).send(message)


    @commands.event
    async def on_ready(self):
        print(f"Bot created as: {self.user.name}")
        self.check_patch.start()


def create_bot() -> Queue_Bot:
    """
    Create a Queue_Bot with an '!' command prefix.

    Returns:
        bot (Queue_Bot): A bot initialised with a command prefix of '!'.
    """
    bot = Queue_Bot(command_prefix='!')
    return bot
