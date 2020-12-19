import regex
import over_stats

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
        self.public_check = self.public_check()

    def validate_battletag(self) -> bool:
        """
        Validates that the battletag is in the correct format
        """
        # nasty looking regex that matches unicode characters from 2 - 11 in length followed by a hash and a 4 or 5 digit number
        p= regex.compile(r'(^([A-zÀ-ú][A-zÀ-ú0-9]{2,11})|(^([а-яёА-ЯЁÀ-ú][а-яёА-ЯЁ0-9À-ú]{2,11})))(#[0-9]{4,})$')
        print(f"Checking battle tag {self.name}")
        if p.match(self.name):
            return True
        else:
            return False

    async def public_check(self) -> bool:
        """
        Checks the account is publicly availible so that stats can be scraped
        """
        if self.valid_battletag:
            player_data = over_stats.PlayerProfile(self.name)
            # hacky way of determining if profile is public or not checks for prescence of game mode stats should have qp and comp if private will be empty list
            public = not (len(player_data.modes()) == 0)
            if not public:
                self.error += 'Error finding profile check the battle tag is correct '
            return public
        else:
            self.error += 'Battle tag invalid '
    


