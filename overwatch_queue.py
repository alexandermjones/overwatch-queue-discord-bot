"""
Class of Overwatch players and a class for a Queue of players.
"""

# Standard library imports
from collections import deque
from math import ceil
import datetime


class Player():
    """
    An Overwatch player.
    """

    def __init__(self, name: str):
        """
        Initialise an Overwatch player.
        """
        self.name = name
        self.playing = False



class Overwatch_Queue():
    """
    A queue of Overwatch players (Player objects)
    """

    def __init__(self, players=[]):
        self.players = players
        self.start_time = datetime.datetime.now()
        self.current_players = deque(players[:6])
        if len(players) > 6:
            self.waiting_players = deque(players[6:])
        else:
            self.waiting_players = deque()
        for player in self.current_players:
            player.playing = True
        for player in self.waiting_players:
            player.playing = False
    

    def add_player(self, player: Player):
        """
        Add a player to the queue.
        """
        # Check that player is not already a player
        if player in self.players:
            message = (f"{player.name} is already a player in the queue.")
            return message
        # Add player to current queue
        self.players.append(player)
        if len(self.current_players) < 6:
            self.current_players.append(player)
            player.playing = True
        else:
            self.waiting_players.append(player)
            player.playing = False
        message = f"{player.name} has been added to the queue."
        
        # If twelve players, recommend you have a six v. six
        if len(self.players) == 12:
            message += (f"\nOh damn! {player.name} is the twelth player - is it time for a 6 vs. 6?")
        return message


    def delete_player(self, player: Player):
        """
        Remove a player from the queue.
        """
        self.players.remove(player)
        if player in self.current_players:
            self.current_players.remove(player)
            # If we have a player waiting, then add them to the current_players list
            if self.waiting_players:
                new_player = self.waiting_players.popleft()
                self.current_players.append(new_player)
                new_player.playing = True
        elif player in self.waiting_players:
            self.waiting_players.remove(player)
    

    def print_players(self):
        """
        Return a message of the currently playing players and the waiting players.
        """
        message = "The players in the next game are: "
        for player in self.current_players:
            message += ("\n\t" + player.name)
        if self.waiting_players:
            message += "\n\nThe players in the waiting queue are: "
            for player in self.waiting_players:
                message += ("\n\t" + player.name)
        return message


    def update_queue(self):
        """
        Change the current players in the queue.
        """
        players_removed = []
        players_waiting = []

        if len(self.players) <= 6:
            pass
        elif len(self.players) == 7:
            # Only a single player to swap out
            players_removed.append(self.current_players.popleft())
            players_waiting.append(self.waiting_players.popleft())
        else:
            # Two players to swap out
            players_removed.append(self.current_players.popleft())
            players_removed.append(self.current_players.popleft())
            players_waiting.append(self.waiting_players.popleft())
            players_waiting.append(self.waiting_players.popleft())

        # Swap the players around
        for player in players_removed:
            self.waiting_players.append(player)
            player.playing = False
        for player in players_waiting:
            self.current_players.append(player)
            player.playing = True

        message = self.print_players()
        return message

    
    def print_player_wait(self, player: Player):
        """
        Return a message of the position of the player and how many games they have to go.
        """
        if player in self.current_players:
            games_left = int(floor(self.current_players.index(player)/2)) -1
            message = f"{player.name} is currently playing/queuing for a game. They have {games_left} games left after this one."
        elif player in self.waiting_players:
            games_left = int(floor(self.waiting_players.index(player)/2)) -1
            message = f"{player.name} has to wait for {games_left} games after this one."
        else:
            message = f"{player.name} is not currently in the queue."
        return message


def create_queue(player_name: str):
    """
    Creates an Overwatch_Queue and adds the creating player to the queue.
    """
    queue = Overwatch_Queue()
    queue.add_player(Player(player_name))
    response = "Overwatch queue has been created. Type \'!join\' to be added to the queue."
    return queue, response


def find_player(queue: Overwatch_Queue, player_name: str):
    """
    Returns a Player object given the player name.
    """
    if not queue:
        return ""
    for player in queue.players:
        if player.name == player_name:
            return player
    return ""