"""
...
"""

# Standard library imports
import os
import requests

# Third party imorts
from bs4 import BeautifulSoup

class Overwatch_Patch_Scraper():
    """
    Class for a scraper that gets patch details from the Overwatch patch-notes and 
    converts this into discord-friendly messages that display nicely.
    """

    def __init__(self):
        """
        Initialises the scraper by setting up the urls and file containing last patch date.
        """
        self.live_patches_url = 'https://playoverwatch.com/en-us/news/patch-notes/live'
        self.experimental_patches_url = 'https://playoverwatch.com/en-us/news/patch-notes/experimental'
        self.live_patch_date_fpath = os.path.join("db", ".livepatchdate")
        latest_live_patch_date = self.__get_patch_date(self.get_latest_patch(self.live_patches_url))
        # Create a patch date file with the date of latest patch
        if not os.path.exists("db"):
            os.mkdir("db")
        with open(self.live_patch_date_fpath, "w") as f:
            f.write(latest_live_patch_date)


    def get_latest_patch(self, url: str):
        """
        Gets the latest (Overwatch) patch from the provided url.

        Args:
            url (str) A url to get the latest patch from - currently only live_patches_url supported.

        Returns:
            latest_patch (bs4.Tag) The latest patch from the provided url.
        """
        latest_patch = self.__get_patch_i(url, 0)
        return latest_patch

    
    def check_for_new_live_patch(self) -> bool:
        """
        Checks the date of the latest patch from the live patches url and compares it with
        the stored date in .livepatchdate. If they differ, return True (new patch) else return False.

        Returns:
            new_patch (bool) True if the latest patch date differs to the stored one.
        """
        latest_patch = self.get_latest_patch(self.live_patches_url)
        patch_date = self.__get_patch_date(latest_patch)
        with open(self.live_patch_date_fpath, "r") as f:
            old_patch_date = f.read()
        
        new_patch = True if old_patch_date != patch_date else False
        if new_patch:
            with open(self.live_patch_date_fpath, "w") as f:
                f.write(patch_date)

        return new_patch


    def prepare_new_live_patch_notes(self) -> list:
        """
        Prepares a list of messages, formatted for Discord, of the latest live patch notes.

        Returns:
            messages (list) A list of patch note messages to return.
        """
        latest_patch = self.get_latest_patch(self.live_patches_url)
        patch_note_string = self.__write_patch_notes(latest_patch)
        messages = self.__create_messages(patch_note_string)
        return messages


    def __get_patch_date(self, patch) -> str:
        """
        Gets the date text from the date class of an Overwatch patch.

        Returns:
            patch_date (str) The date of the patch.
        """
        patch_date = patch.find("div", class_="PatchNotes-date").get_text()
        return patch_date
    

    def __get_patch_i(self, url: str, i: int):
        """
        Gets the ith patch from the provided url.

        Params:
            url (str) The url to get the patch from.
            i (int) Which patch number to get.

        Returns:
            patch (bs4.Tag) A bs4 rendition of the returned url page.
        """
        response = requests.get(url)
        patches_page = BeautifulSoup(response.text, 'html.parser')
        patch = patches_page.find_all("div", class_="PatchNotes-patch")[i]
        return patch

    
    def __write_patch_notes(self, patch) -> str:
        """
        Given a patch from get_latest_patch or __get_patch_i converts the text details of the patch
        into a Discord-friendly string.

        Params:
            patch (bs4.Tag) A patch from get_latest_patch or __get_patch_i
        
        Returns:
            patch_note_string (str) A pretty string formatted with Discord markup of the patch details.
        """
        patch_note_string = f"A new Overwatch patch has been released! Patch notes from: {self.__get_patch_date(patch)}:\n\n"
        patch_sections = patch.find_all("div", class_="PatchNotes-section-generic_update")
        first_section_title = True

        for section in patch_sections:
            # Some patch notes have a section title - add this to the string in bold
            section_title = section.find("h4", class_="PatchNotes-sectionTitle")
            if section_title:
                # Add new lines to subsequent section titles
                if first_section_title:
                    first_section_title = False
                else:
                    patch_note_string += "\n\n"
                patch_note_string += f"__**{section_title.get_text()}**__"
                       
            # Get the title and notes from these sections of patches
            patch_titles = section.find_all("div", class_="PatchNotesGeneralUpdate-title")
            patch_notes = section.find_all("div", class_="PatchNotesGeneralUpdate-description")

            # Loop through patches for the notes section and adds their titles and patches to the patch_note_string
            for i, patch_note in enumerate(patch_notes):
                try:
                    patch_title = patch_titles[i].get_text()
                    patch_note_string += f"\n\n**{patch_title}**"
                except IndexError:
                # No patch_title for events and possibly other patches, so just add new line here
                    patch_note_string += "\n"
                # Prettify nested patch notes by making maps/characters (a single word) italics on a new line
                patch_note_lines = patch_note.get_text().strip().split('\n\n')
                for i, line in enumerate(patch_note_lines):
                    line = line.strip()
                    if not line:
                        continue
                    elif len(line.split(" ")) == 1:
                        patch_note_text = "\n*" + line + "*"
                        patch_note_text = "\n" + patch_note_text if i > 1 else patch_note_text
                    else:
                        patch_note_text = "\n" + line
                    patch_note_string += f"{patch_note_text}"
        
        return patch_note_string


    def __split_message(self, patch_segment: str) -> tuple:
        """
        Given a patch_segment, splits it into two segments, the first with fewer than 2000 characters.
        This is split at the rightmost "__**" index before 2000 characters - i.e. the righmost new
        patch section.

        Params:
            patch_segment (str) A patch segment to split into a chunk <2000 characters.

        Returns:
            patch_segment (str) A section of the patch-notes <2000 characters ending at the end of a section.
            second_patch_segment (str) The rest of the patch-notes, or empty-string if no rest.
        """
        if len(patch_segment) > 2000:
            patch_section_index = patch_segment.rindex("__**", 0, 2000)
            second_patch_segment = patch_segment[patch_section_index:]
            patch_segment = patch_segment[:patch_section_index]
        else:
            second_patch_segment = ""
        return patch_segment, second_patch_segment


    def __create_messages(self, patch_note_string: str) -> list:
        """
        Recursively splits patch_note_string into a series of messages each <2000 characters.

        Params:
            patch_note_string (str) The patch_note_string from __write_patch_notes
        
        Returns:
            messages (list) A list of patch_notes, with each message <2000 characters.
        """
        messages = []
        done = False
        patch_segment = patch_note_string
        while done == False:
            patch_segment, second_patch_segment = self.__split_message(patch_segment)
            messages.append(patch_segment)
            if len(second_patch_segment) < 2000:
                messages.append(second_patch_segment)
                done = True
        # Remove any empty second_patch_segment at the end
        messages = [message.strip() for message in messages if message.strip()]
        return messages


if __name__ == "__main__":
    """
    Run this file directly to test viewing the latest patch notes.
    """
    scraper = Overwatch_Patch_Scraper()
    messages = scraper.prepare_new_live_patch_notes()
    for message in messages:
        print(message)