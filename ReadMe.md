# Melody Generation Project

This project involves preprocessing musical data for melody generation. The `preprocess.py` script contains functions to load, filter, and transpose songs from a dataset.



## Description of `preprocess.py`

### Constants
- `KERN_DATASET_PATH`: Path to the dataset containing musical files.
- `ACCEPTABLE_DURATIONS`: List of acceptable note durations.

### Functions

#### `load_songs_in_kern(dataset_path)`
- Loads songs from the specified dataset path.
- Filters files with extensions `.krn` or `.musicxml`.
- Uses `music21` to parse and load the songs.

#### `has_acceptable_duration(song, acceptable_durations)`
- Checks if all notes and rests in a song have acceptable durations.
- Returns `True` if all durations are acceptable, otherwise `False`.

#### `transpose(song)`
- Determines the key of the song.
- Transposes the song to C Major or A Minor.
- Returns the transposed song.

#### `preprocess(dataset_path)`
- Loads songs from the dataset.
- Filters out songs with unacceptable durations.
- Transposes the remaining songs to C Major or A Minor.
- (Placeholder for encoding and saving songs)

### Main Execution
- Loads songs from the dataset.
- Prints the number of loaded songs.
- Checks if a sample song has acceptable durations.
- Displays the original and transposed versions of the sample song.
