import re
import over_stats

from overwatch import Overwatch

class Battlenet_Account():
    """
    A Batllenet Account.
    """

    def __init__(self, name: str):
        """
        Initialise an Battlenet Account.
        """
        self.name = name
        self.valid_battletag = validate_battletag( name )
        self.public_check = public_check()
    
    def validate_battletag() -> bool:
        """
        Validates that the battletag is in the correct format
        """
        # nasty looking regex that matches unicode characters from 2 - 11 in length followed by a hash and a 4 or 5 digit number
        p= re.compile('/^[\p{L}\p{Mn}][\p{L}\p{Mn}0-9]{2,11}#[0-9]{4,5}+$/u')
        
        return p.match(self.name)

    def public_check() -> bool:
        """
        Checks the account is publicly availible so that stats can be scraped
        """
        player_data = over_stats.PlayerProfile(self.name)
        # hacky way of determining if profile is public ofr not checks for prescence of game mode stats should have qp and comp if private will be empty list
        return not (len(player_data.modes()) == 0)

