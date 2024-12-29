import os
import music21 as m21
import random

from music21 import converter

TEST_DATASET_PATH = "Melodies/deutschl/test"
KERN_DATASET_PATH = "Melodies"
DATASET_PATH = "Dataset"
ACCEPTABLE_DURATIONS = [
    0.25,    # 16th Note
    0.5,     # 8th note
    0.75,    # dotted note
    1.0,     # quarter note
    1.5,     # dotted quarter note
    2,       # half note
    3,       # three quarter-notes
    4        # full note
]


def load_songs_in_kern(dataset_path):
    # go through all files in dataset and load them using music21
    songs = []
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "krn" or file[-8:]=="musicxml":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs


def has_acceptable_duration(song, acceptable_durations):
    for note in song.flatten().notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True


def transpose(song):
    # get key from the score
    parts = song.getElementsByClass(m21.stream.Part)
    measure0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measure0[0][4]

    # Predict key using music21
    if not isinstance(key, m21.key.Key):
        key =  song.analyze("key")

    # get interval for transposition. E.g., Bmaj -> Cmaj, Dmin -> Amin
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    # Transpose song by interval between scales
    transposed_song = song.transpose(interval)
    return transposed_song

def encode(song, time_step=0.25):
    # p = 60, d= 1.0 => [60, "_", "_", "_"]
    encoded_song = []
    for event in song.flatten().notesAndRests:
        # handle notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi   # 60
        
        # handle rests
        elif isinstance(event, m21.note.Rest):
            symbol = "r"
        
        # convert the note/rest into time series notation
        steps = int(event.duration.quarterLength // time_step)

        for step in range(steps):
            if step==0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
    # change encoded song from list to string
    encoded_song = " ".join(map(str, encoded_song))
    return encoded_song



def preprocess(dataset_path):
    # Load the Folk songs
    print("Song Loading is started")
    loaded_songs = load_songs_in_kern(dataset_path)
    print(f"Loaded {len(loaded_songs)} songs.")
    print("Encoding process may take some time\nPlease wait!!!")

    for i, song in enumerate(loaded_songs):
        # Filter out the songs which have unacceptable duration
        if not has_acceptable_duration(song, ACCEPTABLE_DURATIONS):
            continue

        # Transpose songs to C Major / A Minor scale
        transposed_song = transpose(song)

        # Encode songs with music time series representation
        encoded_song = encode(transposed_song)

        # Save songs in a text file
        save_path = os.path.join(DATASET_PATH, str(i))
        with open(save_path, "w") as f:
            f.write(encoded_song)



if __name__ == "__main__":
    preprocess(KERN_DATASET_PATH)