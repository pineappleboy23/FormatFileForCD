import os

from pathlib import Path

# to rea and edit file metadata
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class Song:
    def __init__(self, artist, album, title, file_path, number):
        """
        Initialize a Song object with artist, album, title, and file path.

        :param artist: Name of the contributing artist(s)
        :param album: Name of the album
        :param title: Title of the song
        :param file_path: File path to the audio file
        """
        self.artist = artist
        self.album = album
        self.title = title
        self.number = number
        self.file_path = Path(file_path)

        if len(self.number) == 1:
            self.number = "0" + self.number

        #if first char is a digit
        if self.title[0].isdigit():
            self.title = "_" + self.title



    def __str__(self):
        """
        Returns a string representation of the song.
        """
        return f"'{self.title}' by {self.artist} from album '{self.album}' ({self.file_path})"





def get_metadata(file_path):
    """
    Reads metadata from an MP3 file and returns a Song object.
    """
    try:
        audio = MP3(file_path, ID3=EasyID3)
        # Retrieve metadata, providing defaults if tags are missing
        title = audio.get('Title', ['Unknown'])[0]
        artist = audio.get('Artist', ['Unknown'])[0]
        album = audio.get('Album', ['Unknown'])[0]
        number = audio.get('tracknumber', ['Unknown'])[0]

        # Create and return a Song object
        return Song(artist=artist, album=album, title=title, file_path=file_path, number=number)
    except Exception as e:
        print(f"Could not read metadata for {file_path}: {e}")
        return None  # Return None if metadata cannot be read



replacements = {
    ":": ";",
    "/": "~~",
    "?": "(question)",
    "<": "(less than)",
    ">": "(greater than)",
    "\\": "(backslash)", # escaped backslash
    "|": "(pipe)",
    "*": "(asterisk)",
    "\"": "_"
}

def replace_with_dict(text, replacements):
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


# also sets file name to {number}{title}
# Function to set metadata and rename the file
def set_metadata(song, rename=True):
    """
    Updates the metadata of the song and renames the file to {number}{title}.mp3.

    :param song: song object
    :param rename: should we change the file name too?
    """
    try:
        audio = MP3(song.file_path, ID3=EasyID3)

        # Update metadata if new values are provided
        if song.title:
            audio["Title"] = song.title
        if song.artist:
            audio["Artist"] = song.artist
        if song.album:
            audio["Album"] = song.album

        # Save updated metadata
        audio.save()

        # Rename file to {number}{title}.mp3
        if song.number is not None and rename:
            # Generate new file name with the track number and title
            new_file_name = f"{song.number.strip()}{replace_with_dict(song.title.strip(), replacements)}.mp3"
            new_file_path = song.file_path.parent / new_file_name

            # Rename the file
            os.rename(song.file_path, new_file_path)
            print(f"Renamed {song.file_path} to {new_file_path}")
            song.file_path = new_file_path  # Update the song's file path


    except Exception as e:
        print(f"Could not edit metadata for {song.file_path}: {e}")


def print_titles_and_names(album_path):
    print()
    print()
    print()
    # loop through all songs
    song_file_names = sorted(os.listdir(album_path))
    for file_name in song_file_names:
        full_song_path = os.path.join(album_path, file_name)

        # get song object
        song = get_metadata(full_song_path)

        spaces = ""
        for i in range(50 - len(song.title)):
            spaces = spaces + " "

        print(f"Title: '{song.title}'           {spaces} {song.number} File name: '{file_name}'")
    print()


def check_titles(album_path):
    use_name = False
    print_titles_and_names(album_path)
    if input("Are the titles good? (y/n):") == "y":
        return

    #when title is empty and name is mostly good
    if input("Set titles to name before trim? (y/n):") == "y":
        use_name = True

    while(input("Do you want to trim a string off of the titles? (y/n):") != "n"):
        string_to_trim = input("string to trim:").strip()

        # loop through all songs
        song_file_names = sorted(os.listdir(album_path))
        for file_name in song_file_names:
            full_song_path = os.path.join(album_path, file_name)

            # get song object
            song = get_metadata(full_song_path)

            song.title = song.title.strip()
            if use_name:
                song.title = file_name.replace(".mp3", "")

            song.title = song.title.replace(string_to_trim, "").strip()

            set_metadata(song, rename=False)

        print_titles_and_names(album_path)

    print_titles_and_names(album_path)

    while input("All good? (y/n):") != "y":
        # loop through all songs
        song_file_names = sorted(os.listdir(album_path))
        for file_name in song_file_names:
            full_song_path = os.path.join(album_path, file_name)

            # get song object
            song = get_metadata(full_song_path)
            print()
            print(song)
            print()

            if input("song title ok? (y/n):") != "y":

                title = input("input title (y/n):")

                song.title = title.strip()

                set_metadata(song, rename=False)

        print_titles_and_names(album_path)


def get_album_and_artist(album_path):
    album = None
    artist = None

    artist_freq = {}
    album_freq = {}

    # loop through all songs
    song_file_names = sorted(os.listdir(album_path))
    for file_name in song_file_names:
        full_song_path = os.path.join(album_path, file_name)

        # get song object
        song = get_metadata(full_song_path)

        # Update artist frequency
        artist_freq[song.artist] = artist_freq.get(song.artist, 0) + 1

        # Update album frequency
        album_freq[song.album] = album_freq.get(song.album, 0) + 1

    most_common_artist = max(artist_freq, key=artist_freq.get)
    most_common_album = max(album_freq, key=album_freq.get)

    # get artist
    result = input(f"is artist '{most_common_artist}'?: y/n")
    if result == "y":
        artist = most_common_artist
    else:
        print(artist_freq)
        print()
        for file_name in song_file_names:
            print(file_name)
        print()
        print(album_path)

        artist = input("what is the artist?").strip()

    result = input(f"is album '{most_common_album}'?: y/n")
    if result == "y":
        album = most_common_album
    else:
        print(album_freq)
        print()
        for file_name in song_file_names:
            print(file_name)
        print()
        print(album_path)

        album = input("what is the album?").strip()

    return album, artist


# return example song to rename folder with?
def process_album(album_path):
    """
    Processes all the files in an album folder.
    """
    files = sorted(os.listdir(album_path))
    song_numbers = []

    check_titles(album_path)

    # get album and artist
    album, artist = get_album_and_artist(album_path)


    # loop through each song
    song_file_names = sorted(os.listdir(album_path))
    for file_name in song_file_names:
        full_song_path = os.path.join(album_path, file_name)

        # get song object
        song = get_metadata(full_song_path)
        song.album = album
        song.artist = artist

        # set metadata and rename file
        set_metadata(song)

        # save song number for later checking
        song_numbers.append(int(song.number))

    # check for dupes and missing
    if set(song_numbers) != set(range(1, len(song_numbers) + 1)):
        for i in range(7):
            print(f"missing song in {album} by {artist} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


def main():

    base_folder = input("Enter the base folder path containing albums: ").strip()
    for folder in sorted(os.listdir(base_folder)):
        album_path = os.path.join(base_folder, folder)

        print()
        print()
        print()
        print()
        print()
        print()
        print(f"album path: {album_path}")
        print()

        if not os.path.isdir(album_path):
            print("err")
            continue

        if not folder.endswith("_done"):
            process_album(album_path)

            # Rename folder to indicate completion
            finished_folder_name = folder + "_done"
            os.rename(album_path, os.path.join(base_folder, finished_folder_name))
            print(f"Renamed folder '{folder}' to '{finished_folder_name}'")




if __name__ == "__main__":
    main()
