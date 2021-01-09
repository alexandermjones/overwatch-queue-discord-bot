import os
import sqlite3
from sqlite3 import Error

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
        if not os.path.exists("./db"):
            os.mkdir("./db")
        try:
            conn = sqlite3.connect(r"./db/overwatch_stats.db")
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            if conn:
                sql_create_players_table = """ CREATE TABLE IF NOT EXISTS players (
                                id integer PRIMARY KEY,
                                discord_name text NOT NULL,
                                battle_tag text UNIQUE NOT NULL
                                ); """
                conn.cursor().execute(sql_create_players_table)
                conn.commit()
        return conn


    async def upsert_player(self, discord_name: str, battle_tag:str):
        """
        Inserts or updates a player based on the idea the battle tag will not change but the discord name might
        """
        t = (discord_name, battle_tag)
        self.conn.cursor().execute('INSERT INTO players(discord_name ,battle_tag) VALUES(?,?) ON CONFLICT(battle_tag) DO UPDATE SET discord_name=excluded.battle_tag;', t)
        self.conn.commit()
    
    async def get_battltag(self, discord_name: str):
        """
        Gets the battletag assigned to the discord user
        """
        c= self.conn.cursor()
        t = ( discord_name, )
        c.execute('SELECT battle_tag FROM players WEHRE battle_tag=?', t)

        return c.fetchone()
        
