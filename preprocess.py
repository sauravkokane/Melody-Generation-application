import os
import json
import pickle

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import music21 as m21
import numpy as np
import tensorflow as tf
import keras

from configurations import SEQUENCE_LENGTH, \
    DELIMETER, \
    ACCEPTABLE_DURATIONS, \
    KERN_DATASET_PATH, \
    DATASET_PATH, \
    FILE_DATASET_PATH, \
    MAPPING_PATH


def load_songs_in_kern(dataset_path):
    """
    Walks through the directory tree rooted at dataset_path and loads all files
    with extension "krn" or "musicxml" using music21. Each song is added to a
    list which is returned at the end of the function.

    Parameters
    ----------
    dataset_path : str
        The path to the root directory of the dataset.

    Returns
    -------
    songs : list of music21.stream.Score
        A list of music21.stream.Score objects, each representing a song in the
        dataset.
    """

    # go through all files in dataset and load them using music21
    songs = []
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "krn" or file[-8:] == "musicxml":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs


def has_acceptable_duration(song, acceptable_durations):
    """
    Checks if all notes and rests in a song have durations that are in the
    acceptable_durations list.

    Parameters
    ----------
    song : music21.stream.Score
        The song to check.
    acceptable_durations : list of float
        A list of acceptable durations.

    Returns
    -------
    bool
        True if all notes and rests have acceptable durations, False otherwise.
    """

    for note in song.flatten().notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True


def transpose(song):
    """
    Transposes a given song to C major or A minor scale.

    This function analyzes the key of the input song and calculates the interval
    necessary to transpose the song to C major if it's in a major key, or A minor
    if it's in a minor key. The transposed song is then returned.

    Parameters
    ----------
    song : music21.stream.Score
        The song to be transposed.

    Returns
    -------
    music21.stream.Score
        The transposed song in C major or A minor scale.
    """

    # get key from the score
    parts = song.getElementsByClass(m21.stream.Part)
    measure0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measure0[0][4]

    # Predict key using music21
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")

    # get interval for transposition. E.g., Bmaj -> Cmaj, Dmin -> Amin
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    # Transpose song by interval between scales
    transposed_song = song.transpose(interval)
    return transposed_song


def encode(song, time_step=0.25):
    """
    Encodes a song into a time series representation.

    This function takes a music21.stream.Score object and encodes it into a
    string representation of a time series. The time series is divided into
    steps of a specified time_step (default is 0.25, or a quarter of a beat).
    Each step is represented by either a MIDI pitch (for notes) or an
    underscore (for rests). The duration of each note/rest is encoded by
    repeating the symbol for the appropriate number of steps.

    Parameters
    ----------
    song : music21.stream.Score
        The song to be encoded.
    time_step : float, optional
        The time step for the time series representation. Defaults to 0.25.

    Returns
    -------
    str
        The time series representation of the input song.
    """
    # p = 60, d= 1.0 => [60, "_", "_", "_"]
    encoded_song = []
    for event in song.flatten().notesAndRests:
        # handle notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi  # 60

        # handle rests
        elif isinstance(event, m21.note.Rest):
            symbol = "r"

        # convert the note/rest into time series notation
        steps = int(event.duration.quarterLength // time_step)

        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
    # change encoded song from list to string
    encoded_song = " ".join(map(str, encoded_song))
    return encoded_song


def preprocess(dataset_path):
    """
    Preprocesses a dataset of songs from the specified path.

    This function loads songs using the `load_songs_in_kern` function, filters
    out songs with unacceptable durations, transposes remaining songs to C major
    or A minor, encodes them into a time series representation, and saves each
    encoded song to a text file in the dataset directory.

    Parameters
    ----------
    dataset_path : str
        The path to the root directory of the dataset containing songs to be processed.
    """
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


def load_encoded_song(file_path):
    with open(file_path, "r") as file:
        song = file.read()
    return song


def create_single_file_dataset(dataset_path, full_dataset_file_path, delimiter, sequence_length):
    """
    Loads all the songs in the dataset_path, adds a song delimiter (delimiter * sequence_length) after each song, and saves the songs in a single file located at full_dataset_file_path.

    Parameters
    ----------
    dataset_path : str
        The path to the root directory of the dataset containing songs to be processed.
    full_dataset_file_path : str
        The path to the file that will contain the whole dataset.
    delimiter : str
        The delimiter that will be used to separate the songs in the single file.
    sequence_length : int
        The length of the sequence that will be used to separate the songs in the single file.

    Returns
    -------
    str
        The string containing the songs and the delimiters.
    """
    song_delimiter = delimiter * sequence_length
    songs = []
    number_of_songs = 0
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load_encoded_song(file_path)
            songs.append(song)
            number_of_songs += 1
            if number_of_songs > 1000:
                break
        if number_of_songs > 1000:
            break
    print(f"Loaded {number_of_songs} songs.")

    songs_str = ' '.join(songs + [song_delimiter])

    with open(full_dataset_file_path, 'w') as f:
        f.write(songs_str)

    return songs_str


def create_mapping(songs, mapping_file_path):
    """
    Creates a mapping from unique symbols in the songs to numeric indices and saves it to a file.

    This function identifies the unique vocabulary of symbols (e.g., notes, rests) in the provided
    songs, assigns each symbol a unique integer index, and saves this mapping to a specified JSON file.

    Parameters
    ----------
    songs : str
        A string representing a sequence of encoded songs, with symbols separated by spaces.
    mapping_file_path : str
        The file path where the mapping of symbols to indices will be saved in JSON format.

    Returns
    -------
    dict
        A dictionary where keys are symbols from the songs and values are their corresponding indices.
    """

    mappings = {}

    # identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))

    for i, note in enumerate(vocabulary):
        mappings[note] = i

    # save the mapping in a text file
    with open(mapping_file_path, "w") as f:
        json.dump(mappings, f, indent=4)

    return mappings


def convert_songs_to_numeric(encoded_songs, mapping_file_path):
    """
    Converts a string of encoded songs to a list of numeric values by mapping
    each symbol to its corresponding index in the provided mapping file.

    Parameters
    ----------
    encoded_songs : str
        A string representing a sequence of encoded songs, with symbols
        separated by spaces.
    mapping_file_path : str
        The file path where the mapping of symbols to indices is saved in JSON
        format.

    Returns
    -------
    list of int
        A list of numeric values corresponding to the input songs.
    """
    # Load mappings
    with open(mapping_file_path, "r") as file:
        mappings = json.load(file)

    # Split the songs into list of events
    encoded_songs = encoded_songs.split()

    # Map songs to numeric values
    numeric_songs = [mappings[symbol] for symbol in encoded_songs]

    return numeric_songs


def generate_training_sequences(full_dataset_file_path, mapping_file_path, sequence_length):
    """
    Generates training sequences from a file containing a sequence of songs.

    This function first loads the encoded songs from the specified file path,
    then converts them to numeric values using the provided mapping file path.
    The function then generates the input sequences and targets for training a
    sequence prediction model. The number of sequences is equal to the length
    of the input sequence minus the sequence length.

    Parameters
    ----------
    full_dataset_file_path : str
        The path to the file containing the sequence of encoded songs.
    mapping_file_path : str
        The file path where the mapping of symbols to indices is saved in JSON
        format.
    sequence_length : int
        The length of the sequences to be generated.

    Returns
    -------
    inputs : numpy.ndarray
        A 3-dimensional array of shape (number of sequences, sequence length,
        vocabulary size) containing the input sequences after one-hot encoding.
    targets : numpy.ndarray
        A 1-dimensional array of shape (number of sequences,) containing the
        targets for the input sequences.
    """
    encoded_songs = load_encoded_song(full_dataset_file_path)

    # Convert songs to numeric values
    numeric_songs = convert_songs_to_numeric(encoded_songs, mapping_file_path)

    # Generate the training sequences
    input_sequences = []
    target_values = []

    num_sequences = len(numeric_songs) - sequence_length
    for i in range(num_sequences):
        # Input sequence
        input_sequences.append(numeric_songs[i:i + sequence_length])

        # Target value
        target_values.append(numeric_songs[i + sequence_length])

    # One-hot encode the sequences
    # input dimension = (number of sequences, sequence length) =-> (number of sequences, sequence length, vocabulary size)
    # [[0, 1, 2], [1, 0, 1], [2, 1, 0]] =-> [[[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 1, 0], [1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0], [1, 0, 0]]]
    vocabulary_size = len(set(numeric_songs))
    input_sequences = np.array(input_sequences, dtype=np.int8)
    inputs = keras.utils.to_categorical(input_sequences, num_classes=vocabulary_size).astype(np.int8)
    targets = np.array(target_values, dtype=np.int8)

    return inputs, targets


def main():
    preprocess(KERN_DATASET_PATH)
    songs = create_single_file_dataset(DATASET_PATH, FILE_DATASET_PATH, DELIMETER, SEQUENCE_LENGTH)
    print(len(songs))
    create_mapping(songs, MAPPING_PATH)
    inputs, targets = generate_training_sequences(FILE_DATASET_PATH, MAPPING_PATH, SEQUENCE_LENGTH)
    print(type(inputs), type(targets))
    print(inputs.shape, targets.shape)
    # print memory size of inputs and targets
    print(inputs.nbytes, targets.nbytes)
    # We have shortage of memory, so we will save the inputs and targets to the disk
    with open("songs_inputs.pkl", "wb") as f:
        pickle.dump(inputs, f)

    with open("songs_targets.pkl", "wb") as f:
        pickle.dump(targets, f)


if __name__ == "__main__":
    main()
