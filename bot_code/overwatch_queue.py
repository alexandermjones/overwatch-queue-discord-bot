"""
Class of Overwatch players and a class for a Queue of players.

Below these classes are common funtions for interacting with these classes.
"""

# Standard library imports
import datetime
from collections import deque
from math import floor



class Player():
    """
    An Overwatch player.

    Attributes:
        name (str): The name of the Player.
        playing (bool): Whether a Player is currently playing a game.
    """

    def __init__(self, name: str):
        """
        Initialise an Overwatch player.

        Args:
            name (str): The name of the Player.
        """
        self.name = name
        self.playing = False
        self.delaying = False



class Overwatch_Queue():
    """
    A queue of Overwatch players (Player objects)

    Attributes:
        players (list): The list of all players (Player objects).
        current_players (collections.deque): A deque of players (Player objects) currently playing
        waiting_players (collections.deque): A deque of players (Player objects) waiting to play
    """

    def __init__(self, players=[]):
        """
        Initialise an Overwatch Queue with a list of players.

        The first six players are added into the current_players deque and any other players are
        added to the waiting_players queue.

        Args:
            players (list): The list of players (Player objects) to start the queue.
        """
        self.players = players
        self.delayed_players = []
        self.start_time = datetime.datetime.now()
        # Create a deque of the first six players.
        self.current_players = deque(players[:6])
        # Create a deque of all other players.
        if len(players) > 6:
            self.waiting_players = deque(players[6:])
        else:
            self.waiting_players = deque()
        # Set whether the Player objects are playing or not.
        for player in self.current_players:
            player.playing = True
        for player in self.waiting_players:
            player.playing = False
    

    def add_player(self, player: Player) -> str:
        """
        Adds a player to the queue.

        If there are fewer than six plyers, they are added to the current_players deque,
        else they are added to the waiting_players deque.
        If they are the twelth player, then it is recommended that a 6 v. 6 is played.

        Args:
            player (Player): A Player object to add to the queue.

        Returns:
            message (str): A message saying whether the player has been added.
        """
        # Check that player is not already a player.
        if player in self.players:
            message = (f"{player.name} is already a player in the queue.")
            return message
        # Add player to queue and current or waiting players.
        self.players.append(player)
        if len(self.current_players) < 6:
            self.current_players.append(player)
            player.playing = True
        else:
            self.waiting_players.append(player)
            player.playing = False

        message = f"{player.name} has been added to the queue."
        
        # If twelve players, recommend you have a six v. six.
        if len(self.players) == 12:
            message += (f"\nOh damn! {player.name} is the twelth player - is it time for a 6 vs. 6?")
        return message


    def delete_player(self, player: Player):
        """
        Removes a player from the queue.

        The player is removed from the list of players.
        If they are in the current_players deque, then they are removed from here and the next
        waiting player is added to current_players.
        If the player is in the waiting_players deque, they are removed from here.

        Args:
            player (Player): A Player object to add to the queue.
        """
        self.players.remove(player)
        if player in self.current_players:
            self.current_players.remove(player)
            # If we have a player waiting who is not delaying, then add them to the current_players list.
            if len(list(filter(lambda x: not x.delaying, self.waiting_players))):
                self.__rotate_queue_once()
        elif player in self.waiting_players:
            self.waiting_players.remove(player)

    
    def delay_player(self, player: Player):
        """
        Moves a player from the current or waiting players to delayed_players.

        The player is removed from the current_players or waiting_players deque.
        The player is then added to the delayed_players list.
        Finally, if a player is in the waiting_players deque, then they are added to current_players.

        Args:
            player (Player): A Player object in self.players
        """
        player.playing = False
        player.delaying = True
        self.delayed_players.append(player)
        if player in self.current_players:
            self.current_players.remove(player)
            # If we have a player waiting who is not delaying, then add them to the current_players list.
            if len(list(filter(lambda x: not x.delaying, self.waiting_players))):
                self.__rotate_queue_once()
            self.waiting_players.appendleft(player)
        message = self.print_players()
        return message

    
    def rejoin_player(self, player: Player):
        """
        Sets the player to no longer be delaying and adds them to current_players if space.

        Args:
            player (Player): A Player object in self.players
        """
        player.delaying = False
        self.delayed_players.remove(player)
        if len(self.current_players) <= 5:
            self.current_players.append(player)
            self.waiting_players.remove(player)
            player.playing = True
        message = self.print_players()
        return message
    

    def print_players(self) -> str:
        """
        Returns a message showing the currently playing players and the waiting players.

        Returns:
            message (str): The message of current and waiting players' status.
        """
        # Print players in the next/current game.
        message = "The players in the next game are: "
        for player in self.current_players:
            message += ("\n\t" + player.name)
        # Print players waiting for a game.
        if self.waiting_players:
            message += "\n\nThe players in the waiting queue are: "
            for player in self.waiting_players:
                message += ("\n\t" + player.name)
                if player.delaying:
                    message += " (Currently delaying)"
        return message


    def update_queue(self) -> str:
        """
        Changes the current players in the queue for the next game.

        If there are fewer than six players, nothing changes.
        If there are seven players, then the oldest player is moved to waiting_players and the
        longest waiting player is moved to current_players.
        If there are more than seven players, then the two oldest players are moved to waiting_players
        and the two longest waiting players are moved to current_players.

        Returns:
            message (str): The message from self.print_players()
        """
        if (len(self.players) - len(self.delayed_players)) <= 6:
            # No players to swap out
            pass
        elif (len(self.players) - len(self.delayed_players)) == 7:
            # Only a single player to swap
            self.__rotate_queue_once()
        elif (len(self.players) - len(self.delayed_players)) <= 10: 
            # Two players to swap
            self.__rotate_queue_once()
            self.__rotate_queue_once()
        else:
            # Three players to swap
            self.__rotate_queue_once()
            self.__rotate_queue_once()
            self.__rotate_queue_once()

        # Get a message of who the current/waiting players now.
        message = self.print_players()
        return message

    
    def print_player_wait(self, player: Player) -> str:
        """
        Returns a message of the queue status of the Player and how many games they have left/to wait.

        Args:
            player (Player): A Player object to return its status.

        Returns:
            message (str): The message telling the player how long they have to go.
        """
        # If player in a game, return how many games they have left to play.
        if player in self.current_players:
            games_left = int(floor(self.current_players.index(player)/2))
            message = f"{player.name} is currently playing/queuing for a game. They have {games_left} games left after this one."
        # If player waiting for a game, return how many games they have to wait for.
        elif player in self.waiting_players:
            games_left = int(floor(self.waiting_players.index(player)/2))
            message = f"{player.name} has to wait for {games_left} games after this one."
        else:
            message = f"{player.name} is not currently in the queue."
        return message

    
    def empty_queue(self):
        """
        Empties the queue of all players.
        """
        for player in self.players:
            del(player)
        self.players = []
        self.current_players = deque()
        self.waiting_players = deque()

    
    def __rotate_queue_once(self):
        """
        Private function. Rotates one current player into the waiting queue.
        Called in update_queue.
        """
        players_delaying = []

        # Remove any delayed players into holding position
        for player in self.delayed_players:
            if player == self.waiting_players[0]:
                players_delaying.append(self.waiting_players.popleft())

        # Swap out player
        old_player = self.current_players.popleft()
        new_player = self.waiting_players.popleft()
        self.current_players.append(new_player)
        self.waiting_players.append(old_player)
        old_player.playing = False
        new_player.playing = True        

        # Replace any players holding position
        for player in players_delaying:
            self.waiting_players.appendleft(player)



"""
Function for interacting with the classes above.
"""


def find_player(queue: Overwatch_Queue, player_name: str):
    """
    Returns a Player object from the queue, given a player name as a string.

    Args:
        queue (Overwatch_Queue): An Overwatch_Queue of Players.
        player_name (str): The name of a player in the Overwatch_Queue.
    
    Returns:
        player (Player): A Player object with the same name as player_name in the queue, empty string if none.
    """
    for player in queue.players:
        if player.name == player_name:
            return player
    return ""