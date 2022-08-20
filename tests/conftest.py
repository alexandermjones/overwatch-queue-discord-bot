import pytest

from bot_code.game_queue import Player, Overwatch_Queue


# Create a fixture of five players
@pytest.fixture
def five_players():
    five_players_list = [Player(str(i)) for i in range(1,6)]
    return five_players_list


# Create a fixture of a queue of five players
@pytest.fixture
def five_player_queue(five_players):
    five_player_queue_obj = Overwatch_Queue(five_players)
    return five_player_queue_obj


# Create a fixture of seven players
@pytest.fixture
def seven_players():
    seven_players_list = [Player(str(i)) for i in range(1,8)]
    return seven_players_list


# Create a fixture of a queue of seven players
@pytest.fixture
def seven_player_queue(seven_players):
    seven_player_queue_obj = Overwatch_Queue(seven_players)
    return seven_player_queue_obj


# Create a fixture of ten players
@pytest.fixture
def ten_players():
    ten_players_list = [Player(str(i)) for i in range(1,11)]
    return ten_players_list


# Create a fixture of a queue of ten players
@pytest.fixture
def ten_player_queue(ten_players):
    ten_player_queue_obj = Overwatch_Queue(ten_players)
    return ten_player_queue_obj
