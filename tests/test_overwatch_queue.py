"""
Unit tests for overwatch_queue.py
"""
from collections import deque
import pytest

from bot_code.overwatch_queue import *


def test_add_player_five_person_queue(five_player_queue):
    new_player = Player("new")
    message = five_player_queue.add_player(new_player)
    assert new_player in five_player_queue.current_players
    assert new_player.playing
    assert message == "new has been added to the queue."


def test_add_player_seven_person_queue(seven_player_queue):
    new_player = Player("new")
    message = seven_player_queue.add_player(new_player)
    assert new_player in seven_player_queue.waiting_players
    assert not new_player.playing
    assert message == "new has been added to the queue."


def test_add_existing_player(five_players, five_player_queue):
    previous_length = len(five_player_queue.players)
    new_player = five_players[0]
    message = five_player_queue.add_player(new_player)
    assert len(five_player_queue.current_players) == previous_length
    assert message == "1 is already a player in the queue."


def test_delete_player_seven_person_queue(seven_players, seven_player_queue):
    old_player = seven_players[0]
    old_waiting_player = seven_players[6]
    seven_player_queue.delete_player(old_player)
    assert old_player not in seven_player_queue.players
    assert len(seven_player_queue.players) == 6
    assert old_waiting_player.playing
    assert old_waiting_player in seven_player_queue.current_players


def test_update_queue_five_person_queue(five_players, five_player_queue):
    old_message = five_player_queue.print_players()
    message = five_player_queue.print_players()
    expected_current_players = deque(five_players)
    assert message == old_message
    assert five_player_queue.current_players == expected_current_players
    assert five_player_queue.waiting_players == deque()


def test_update_queue_seven_person_queue(seven_players, seven_player_queue):
    message = seven_player_queue.update_queue()
    expected_message = ''.join(("The players in the next game are: ",
                                "\n\t2\n\t3\n\t4\n\t5\n\t6\n\t7",
                                "\n\nThe players in the waiting queue are: ",
                                "\n\t1"))
    assert seven_players[0] in seven_player_queue.waiting_players
    assert seven_players[6] in seven_player_queue.current_players
    assert message == expected_message


def test_update_queue_ten_person_queue(ten_players, ten_player_queue):
    message = ten_player_queue.update_queue()
    expected_message = ''.join(("The players in the next game are: ",
                                "\n\t3\n\t4\n\t5\n\t6\n\t7\n\t8",
                                "\n\nThe players in the waiting queue are: ",
                                "\n\t9\n\t10\n\t1\n\t2"))
    assert ten_players[0] in ten_player_queue.waiting_players                         
    assert ten_players[1] in ten_player_queue.waiting_players
    assert ten_players[6] in ten_player_queue.current_players
    assert ten_players[7] in ten_player_queue.current_players
    assert message == expected_message


def test_print_player_wait_current_player(seven_players, seven_player_queue):
    current_player = seven_players[4]
    message = seven_player_queue.print_player_wait(current_player)
    expected_message = ''.join(("5 is currently playing/queuing for a game. ",
                                "They have 2 games left after this one."))
    assert message == expected_message


def test_print_player_wait_waiting_player(seven_players, seven_player_queue):
    current_player = seven_players[6]
    message = seven_player_queue.print_player_wait(current_player)
    expected_message = "7 has to wait for 0 games after this one."
    assert message == expected_message

"""
def test_create_queue():
    queue, message = create_queue("1")
    expected_message = ''.join(("Overwatch queue has been created. ",
                                "Type \'!join\' to be added to the queue.",
                                "\n1 has been added to the queue."))
    assert type(queue) == Overwatch_Queue
    assert queue.current_players[0].name == "1"
    assert message == expected_message
"""

def test_find_player(five_players, five_player_queue):
    player = find_player(five_player_queue, "5")
    assert player == five_players[4]