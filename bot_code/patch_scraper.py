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
    ...
    """

    def __init__(self):
        """
        ...
        """
        self.live_patches_url = 'https://playoverwatch.com/en-us/news/patch-notes/live'
        self.experimental_patches_url = 'https://playoverwatch.com/en-us/news/patch-notes/experimental'
        latest_live_patch_date = self.__get_patch_date(self.get_latest_patch(self.live_patches_url))
        # Create a patch date file with the date of latest patch
        with open(".livepatchdate", "w") as f:
            f.write(latest_live_patch_date)


    def get_latest_patch(self, url: str):
        """
        ...
        """
        latest_patch = self.__get_patch_i(url, 0)
        return latest_patch

    
    def check_for_new_live_patch(self):
        """
        ...
        """
        latest_patch = self.get_latest_patch(self.latest_live_patch)
        patch_date = self.__get_patch_date(latest_patch)
        with open(".livepatchdate", "r") as f:
            old_patch_date = f.read()
        
        new_patch = True if old_patch_date != patch_date else False
        if new_patch:
            with open(".livepatchdate", "w") as f:
                f.write(patch_date)

        return new_patch


    def prepare_new_live_patch_notes(self):
        """
        ...
        """
        latest_patch = self.get_latest_patch(self.live_patches_url)
        patch_note_string = self.__write_patch_notes(latest_patch)
        messages = self.__create_messages(patch_note_string)
        return messages


    def __get_patch_date(self, patch):
        """
        ...
        """
        patch_date = patch.find("div", class_="PatchNotes-date").get_text()
        return patch_date
    

    def __get_patch_i(self, url: str, i: int):
        """
        ...
        """
        response = requests.get(url)
        patches_page = BeautifulSoup(response.text, 'html.parser')
        patch = patches_page.find_all("div", class_="PatchNotes-patch")[i]
        return patch

    
    def __write_patch_notes(self, patch):
        """
        ...
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
                       
            # Get the title and notes from the section of patches
            patch_titles = section.find_all("div", class_="PatchNotesGeneralUpdate-title")
            patch_notes = section.find_all("div", class_="PatchNotesGeneralUpdate-description")

            # Loop through patches for the given section and add titles and patches to the patch_note_string
            for i, patch_note in enumerate(patch_notes):
                try:
                    patch_title = patch_titles[i].get_text()
                    patch_note_string += f"\n\n**{patch_title}**\n"
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


    def __split_message(self, patch_segment: str, second_patch_segment: str):
        """
        ...
        """
        if len(patch_segment) > 2000:
            patch_section_index = patch_segment.rindex("__**", 0, 2000)
            second_patch_segment = patch_segment[patch_section_index:]
            patch_segment = patch_segment[:patch_section_index]
        else:
            second_patch_segment = ""
        return patch_segment, second_patch_segment


    def __create_messages(self, patch_note_string: str):
        """
        ...
        """
        messages = []
        done = False
        patch_segment, second_patch_segment = patch_note_string, ""
        while done == False:
            patch_segment, second_patch_segment = self.__split_message(patch_segment, second_patch_segment)
            messages.append(patch_segment)
            if len(second_patch_segment) < 2000:
                messages.append(second_patch_segment)
                done = True
        # Remove any empty second_patch_segment at the end
        [message for message in messages if message]
        return messages


if __name__ == "__main__":
    scraper = Overwatch_Patch_Scraper()
    messages = scraper.prepare_new_live_patch_notes()
    for message in messages:
        print(message)