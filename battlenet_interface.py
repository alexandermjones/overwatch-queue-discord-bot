import regex
import over_stats
import datetime
import json
from contextlib import suppress

class Game_Stats():
    """
    Data holding class for 
    """
    def __init__(self, battletag: str):
        """
        Initialise an Battlenet Account.
        """
        self.battletag = battletag
        self.timestamp = datetime.now
        self.cp_wins = 0
        self.cp_loss = 0
        self.cp_total = 0
        self.cp_draw =0  
        self.qp_wins = 0
        self.qp_loss = 0
        self.qp_total = 0

class Battlenet_Account():
    """
    A Batllenet Account.
    """

    def __init__(self, name: str):
        """
        Initialise an Battlenet Account.
        """
        self.name = name
        self.error = ''
        self.valid_battletag = self.validate_battletag()
        self.public_check = self.public_lookup()
        self.player_data = (over_stats.PlayerProfile(self.name) if self.valid_battletag & self.public_check else None  )

    def validate_battletag(self) -> bool:
        """
        Validates that the battletag is in the correct format
        """
        # nasty looking regex that matches unicode characters from 2 - 11 in length followed by a hash and a 4 or larger digit number
        p= regex.compile(r'(^([A-zÀ-ú][A-zÀ-ú0-9]{2,11})|(^([а-яёА-ЯЁÀ-ú][а-яёА-ЯЁ0-9À-ú]{2,11})))(#[0-9]{4,})$')
        print(f"Checking battle tag {self.name}")
        if p.match(self.name):
            return True
        else:
            self.error += 'Incorrect battle tag format ensure you have include the # and the number following it.\n' 
            return False

    async def public_lookup(self) -> bool:
        """
        Checks the account is publicly availible so that stats can be scraped
        """
        if(self.valid_battletag):
            player_data = over_stats.PlayerProfile(self.name)
            # hacky way of determining if profile is public or not checks for prescence of game mode stats should have qp and comp if private will be empty list
            public = not (len(player_data.modes()) == 0)
            if not public:
                self.error += 'Could not find profile, ensure that it public.\n'
        return public
    
    async def get_game_stats(self) -> Game_Stats:
        """
        Returns the win loss draw values for the instantiated battlenet account
        """
        gs = Game_Stats(self.name)
        #games played can be game played if singular

        qp_total_raw = [(key, value) for key, value in self.player_data.stats('quickplay', "ALL HEROES", "Game").items() if "Played" in key and "Game" in key] 
        cp_total_raw = [(key, value) for key, value in self.player_data.stats('competitive', "ALL HEROES", "Game").items() if "Played" in key and "Game" in key]
        qp_win_raw = [(key, value) for key, value in self.player_data.stats('quickplay', "ALL HEROES", "Game").items() if "Won" in key ] 
        qp_loss_raw = [(key, value) for key, value in self.player_data.stats('quickplay', "ALL HEROES", "Game").items() if "Lost" in key ] 
        cp_win_raw = [(key, value) for key, value in self.player_data.stats('competitive', "ALL HEROES", "Game").items() if "Won" in key ] 
        cp_loss_raw = [(key, value) for key, value in self.player_data.stats('competitive', "ALL HEROES", "Game").items() if "Lost" in key ] 
        cp_draw_raw = [(key, value) for key, value in self.player_data.stats('competitive', "ALL HEROES", "Game").items() if "Drew" in key ]

        gs.cp_total = cp_total_raw[0][1] if len(qp_total_raw) > 0 else 0
        gs.qp_total = qp_total_raw[0][1] if len(qp_total_raw) > 0 else 0
        gs.qp_wins = qp_win_raw[0][1] if len(qp_total_raw) > 0 else 0
        gs.qp_loss = qp_loss_raw[0][1] if len(qp_total_raw) > 0 else 0
        gs.cp_wins = cp_win_raw[0][1] if len(qp_total_raw) > 0 else 0
        gs.cp_loss = cp_loss_raw[0][1] if len(qp_total_raw) > 0 else 0
        gs.cp_draw = cp_draw_raw[0][1] if len(qp_total_raw) > 0 else 0

        return gs