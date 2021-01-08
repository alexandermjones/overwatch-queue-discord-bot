import sqlite3
from sqlite3 import Error
from typing import Set, Tuple
import logging
from overwatch_queue import Overwatch_Queue

"""
SUPER FUCKING IMPORTANTANTO - It is in Spanish so you know how seroius I am 

use tuple substitution api layer, instead of f strings or % substitution for injecting params 
Otherwise bobby drop tables USER; will strike again
"""

class Storage():
    """
    Class for handling sqlite storage of data
    """

    def __init__(self):
        """
        Initialise an Battlenet Account.
        """
        self.conn = self.create_connection()


    def create_connection(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            logging.info("Connecting to db")
            conn = sqlite3.connect(r"./db/overwatch_stats.db")
            logging.info(f"db connection successful sqlite version: {sqlite3.version}")
        except Error as e:
            print(e)
        finally:
            if conn:
                #TODO: needs refactoring out as single sql script with migration strategy for after 1.0 release
                sql_create_players_table = """ CREATE TABLE IF NOT EXISTS players (
                                id integer PRIMARY KEY,
                                discord_name text NOT NULL,
                                battle_tag text UNIQUE NOT NULL
                                ); """
                sql_create_session_table = """ CREATE TABLE IF NOT EXISTS session (
                                id integer PRIMARY KEY,
                                win int DEFAULT 0,
                                loss int DEFAULT 0,
                                draw int DEFAULT 0
                                ); """
                sql_create_sessionPlayers_table = """ CREATE TABLE IF NOT EXISTS sessionPlayers (
                                id integer PRIMARY KEY,
                                playerId integer,
                                sessionId integer,
                                FOREIGN KEY(playerId) REFERENCES players(id),
                                FOREIGN KEY(sessionId) REFERENCES session(id),
                                UNIQUE(playerId, sessionId)
                                );"""
                conn.cursor().execute(sql_create_players_table)
                conn.cursor().execute(sql_create_session_table)
                conn.cursor().execute(sql_create_sessionPlayers_table)
                conn.commit()
        return conn


    async def upsert_player(self, discord_name: str, battle_tag: str) -> None:
        """
        Inserts or updates a player based on the idea the battle tag will not change but the discord name might
        """
        t = [(discord_name), (battle_tag)]
        try:
            self.conn.cursor().execute('INSERT INTO players(discord_name ,battle_tag) VALUES(?,?) ON CONFLICT(battle_tag) DO UPDATE SET discord_name=excluded.battle_tag;', t)
            self.conn.commit()
            logging.info(f"Link successful: {discord_name} linked to {battle_tag}")
        except:
            logging.error(f"Error linking the account details {discord_name}, {battle_tag}")

    
    async def get_battltag(self, discord_name: str) -> Tuple[str, str]:
        """
        Gets the battletag assigned ot the discord user
        """
        c= self.conn.cursor()
        t = ( discord_name, )
        c.execute('SELECT id, battle_tag FROM players WHERE discord_name=?', t)

        return c.fetchone()
    
    async def create_session(self , queue: Overwatch_Queue) -> int:
        """
        Creates a default session inserts the players into the sessionPlayers table returns the session id
        """
        #for each member of the queue playing get their player id if they have one
        c = self.conn.cursor()
        sessionId = -1
        try:
            c.execute('INSERT INTO session(win, loss, draw) VALUES(0,0,0);')
            self.conn.commit()
            sessionId = c.lastrowid
            logging.info(f"Empty session created with id : {sessionId}")
        except:
            logging.error(f"Error creating session")
        try:
            await self.associate_players_with_session(queue= queue, sessionId = sessionId)
        except:
            logging.error(f"Error associating the players with session: {queue}")
        return sessionId

    async def update_session_stats(self, sessionId: int, wins: int, losses: int, draws: int) -> None:
        """
        Inserts the session stats into the db
        """
        try:
            c= self.conn.cursor()
            t = [(sessionId), (wins), (losses), (draws)]
            c.execute('UPDATE session SET win = ? ,loss = ?, draw = ? WHERE id = ?;', t) 
            self.conn.commit()
        except:
            logging.error(f"Something went wrong updating the session with values: {t}")
    
    async def associate_players_with_session(self, queue: Overwatch_Queue, sessionId: int) -> None:
        """
        Takes the queue and inserts the active player into the sessionPlayers table.
        """
        c = self.conn.cursor()
        try:
            records = [(el, sessionId) for el in queue.get_current_players()]
            c.executemany('INSERT INTO sessionPlayers VALUES((SELECT id FROM players WHERE discord_name=?),?);',records)
            self.conn.commit()
        except:
            logging.info(f"Something went wrong inserting {records}")
            raise Exception("Storage error")
        