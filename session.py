from overwatch_queue import Overwatch_Queue
from storage_layer import Storage

class Session():
    """
    Class for managing sessions during a queue
    """
    def __init__(self, queue: Overwatch_Queue, store: Storage):
        """
        Initialise the session from the queue.
        """
        self.queue = queue
        self.create_session_store()
        self.insert_players()
        self.storage = store
    
    def create_session_store(self):
        return True
    
    def insert_players(self):
        return True

    def end_session(self):
        return True


