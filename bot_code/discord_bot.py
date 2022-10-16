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
        NO_QUEUE_RESPONSE (str): The default response for there not being a queue.
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
        self.command_prefix = command_prefix
        self.queues = dict()
        self.NO_GAME_PARAM_RESPONSE = "Game to interact with cannot be identified. Please enter it after the command."
        self.NO_PLAYERCUTOFF_PARAM_RESPONSE = "No player count data exists for that game. Please enter it after the game name in the command."
        self.NO_QUEUE_RESPONSE = "There is no queue. Type \'!queue [game_name] [player_number]\' to create one."
        self.__game_dict_fpath = Path("db") / "game_dict.json"
        # Create a game dictionary if one isn't present already
        if not self.__game_dict_fpath.exists():
            with open(self.__game_dict_fpath, 'w') as f:
                json.dump({}, f)
        with open(self.__game_dict_fpath) as f:
            self.game_dict = json.load(f)
        
        # TODO separate these out into a new bot
        self.scraper = Overwatch_Patch_Scraper()
        self.patch_channel_fpath = os.path.join("db", "patchchannels")
        if not os.path.exists(self.patch_channel_fpath):
            Path(self.patch_channel_fpath).touch()

    """
    Private class methods to support commands.
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

    
    def __check_and_lower_game_name_param(self, game_name: str, player_name: str=""):
        """
        DOCSTRING
        """
        if game_name:
            return game_name.lower()
        player_queues = [name for name in self.queues.keys() if self.queues[name].find_player(player_name)]
        if len(player_queues) == 1:
            return player_queues[0]
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


    """
    Commands for the bot - methods decorated by discord.ext.commands.
    """
    @commands.hybrid_command(name='queue', 
                             aliases=['join'],
                             help='Join a Game Queue for the given game_name, start queue if none exists.')
    async def start_queue(self, ctx: commands.Context, game_name: str="", player_cutoff: int=0) -> str:
        """
        Command for the player to start or join  a queue for the given game_name.

        Args:
            ctx (commands.Context): The context of the command.
            game_name (str, default=""): The name of the game to queue for.
            player_cutoff (int, default=0): The player count for the given game_name.

        Returns:
            str: The response message to post in the Discord channel the command was sent in.
        """
        lower_game_name = self.__check_and_lower_game_name_param(self, game_name)
        # If no game_name and can't be inferred, then return this needs to be a parameter
        if not lower_game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        # Add player to queue if game already has a queue
        elif lower_game_name in self.queues.keys():
            response = self.queues[lower_game_name].add_player(Player(ctx.message.author.name))
        # Create a new queue if game does not have a queue
        else:
            player_cutoff = self.__check_player_cutoff_param(lower_game_name, player_cutoff)
            # If player_cutoff can't be inferred, return this needs to be a parameter
            if not player_cutoff:
                response = self.NO_PLAYERCUTOFF_PARAM_RESPONSE
            # Create a new queue for the game, and @mention game if possible.
            else:
                self.queues[game_name] = Game_Queue(game_name, player_cutoff)
                roles = ctx.guild.roles
                for role in roles:
                    if lower_game_name in role.name.lower and role.mentionable:
                        game_name = role.mention
                response = f"Queue has been created for {game_name}.\n"
                response += self.queues[lower_game_name].add_player(Player(ctx.message.author.name))
        await ctx.send(response)


    @commands.hybrid_command(name='leave',
                             aliases=['quit'],
                             help='Leave the queue for the given game_name.')
    async def leave_queue(self, ctx: commands.Context, game_name: str="") -> str:
        """
        Command for the player to leave the queue for the given game_name.

        Args:
            ctx (commands.Context): The context of the command.
            game_name (str, default=""): The name of the game to queue for.

        Returns:
            str: The response message to post in the Discord channel the command was sent in.
        """
        player_name = ctx.message.author.name
        lower_game_name = self.__check_and_lower_game_name_param(game_name, player_name)
        # If no game_name and can't be inferred, then return this needs to be a parameter
        if not game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        # If player in the game_name, them remove from queue
        elif self.queues[game_name].find_player[player_name]:
            player = self.queues[game_name].find_player[player_name]
            response = self.queues[game_name].delete_player(player)
        else:
            response = f"{player_name} is not a member of the queue for {game_name}. Please check and try again."
        await ctx.send(response)


    @commands.hybrid_command(name='next',
                             aliases=['rotate', 'update'],
                             help='Rotate the queue to get the players for the next game.')
    async def next_game_for_queue(self, ctx: commands.Context, game_name: str="") -> str:
        """
        Command to rotate the queue for game_name to view the players for the next game.

        Args:
            ctx (commands.Context): The context of the command.
            game_name (str, default=""): The name of the game to rotate the queue for.

        Returns:
            str: The response message to post in the Discord channel the command was sent in.
        """
        player_name = ctx.message.author.name
        lower_game_name = self.__check_and_lower_game_name_param(game_name, player_name)
        # If no game_name and can't be inferred, then return this needs to be a parameter
        if not game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        # Else rotate the queue once and print the new ordering of the queue
        else:
            response = self.queues[lower_game_name].update_queue()
        await ctx.send(response)


    @commands.command(name='status', help='See the status of the queue for the given game_name.')
    async def status_queue(self, ctx: commands.Context, game_name: str="") -> str:
        """
        Command to print the status of the queue, i.e. the current ordering of players.

        Args:
            ctx (commands.Context): The context of the command.
            game_name (str, default=""): The name of the game to print the status of the queue for.

        Returns:
            str: The response message to post in the Discord channel the command was sent in.
        """
        player_name = ctx.message.author.name
        lower_game_name = self.__check_and_lower_game_name_param(game_name, player_name=player_name)
        # If no game_name and can't be inferred, then return this needs to be a parameter
        if not game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        elif lower_game_name not in self.queues.keys():
            response = self.NO_QUEUE_RESPONSE
        else:
            response = self.queues[lower_game_name].print_players()
        await ctx.send(response)


    @commands.command(name='wait', help='See how long until your next game.')
    async def wait_queue(self, ctx: commands.Context, game_name: str='') -> str:
        """
        Command to print the wait time of the messager.

        Args:
            ctx (commands.Context): The context of the command.
            game_name (str, default=""): The name of the game to print the wait for.

        Returns:
            str: The response message to post in the Discord channel the command was sent in.
        """
        player_name = ctx.message.author.name
        lower_game_name = self.__check_and_lower_game_name_param(game_name, player_name=player_name)
        if not lower_game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        elif lower_game_name not in self.queues.keys():
            response = self.NO_QUEUE_RESPONSE
        else:
            player = self.queues[lower_game_name].find_player(player_name)
            response = self.queues[lower_game_name].print_player_wait(player)
        await ctx.send(response)

    
    @commands.command(name='add', help='Add a player to the queue.')
    async def add_player(self, ctx: commands.Context, player_to_add: str='', game_name: str=''):
        """
        Command to add a player to the queue.
        
        Args:
            ctx (commands.Context): The context of the command.
            player_to_add (str, default=""): The name of the player to add to the queue.
            game_name (str, default=""): The name of the game to add the player to.

        Returns:
            str: The response message to post in the Discord channel the command was sent in.
        """
        if not player_to_add:
            await ctx.send(f'Please enter {self.command_prefix}add [PLAYERNAME] [GAMENAME].')
        lower_game_name = self.__check_and_lower_game_name_param(game_name, player_name=ctx.message.author.name)
        if not lower_game_name:
            response = self.NO_GAME_PARAM_RESPONSE
        elif lower_game_name not in self.queues.keys():
            response = self.NO_QUEUE_RESPONSE
        elif self.queues[lower_game_name].find_player(player_to_add):
            response = f'{player_to_add} is already a member of the queue for {lower_game_name}.'
        else:
            response = self.queues[lower_game_name].add_player(Player(player_to_add))
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
