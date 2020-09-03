#!/usr/bin/python
import linecache

"""
This module will load in a "patch_notes.txt" and contain methods that performs read-only operations on the file
"""


class PatchNotesFile:
    def __init__(self, patch_notes_file_path: str) -> None:
        """
        Parametrized constructor

        Attributes:
            patch_notes_file_path: path to the patch notes file to be read from
        """

        self.patch_notes_file = patch_notes_file_path

    def get_content_from_line_number(self, lineNumber: int) -> str:
        """
        Attempts to get content from a particular line number from the patch notes file

        Attributes:
            lineNumber: the line number to look at

        Returns:
            lineContent: The content from the line number
            None: if only whitespace content is found, or if line cannot be found
        """

        lineContent = linecache.getline(self.patch_notes_file, lineNumber)
        # Treat whitespace content as invalid results
        if lineContent == "\n" or lineContent == "":
            return None

        return lineContent

    def get_total_line_count(self) -> int:
        """
        Gets the total number of lines from self.patch_notes_file

        Returns:
            Total number of lines from the patch notes file
        """

        tempFile = open(self.patch_notes_file, "r")
        numLines = 0

        for line in tempFile:
            numLines += 1

        tempFile.close()
        return numLines

    def get_version_string(self) -> str:
        """
        Gets the version string from self.patch_notes_file (first line)

        Returns:
            The version string of the patch notes file
        """
        line_content = linecache.getline(self.patch_notes_file, 1)
        version_string = line_content.replace("Version ", "").rstrip()
        return version_string
