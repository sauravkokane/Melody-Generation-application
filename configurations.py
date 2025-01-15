# constants

SEQUENCE_LENGTH = 64
OUTPUT_UNITS = 45
NUM_UNITS = [256]
LOSS = "sparse_categorical_crossentropy"
LEARNING_RATE = 0.001
NUM_EPOCHS = 50
BATCH_SIZE = 64
DELIMETER = "/ "

ACCEPTABLE_DURATIONS = [
    0.25,  # 16th Note
    0.5,  # 8th note
    0.75,  # dotted note
    1.0,  # quarter note
    1.5,  # dotted quarter note
    2,  # half note
    3,  # three quarter-notes
    4  # full note
]

# paths
TEST_DATASET_PATH = "Melodies/deutschl/test"
KERN_DATASET_PATH = "Melodies"
DATASET_PATH = "Dataset"
FILE_DATASET_PATH = "file_dataset.txt"
MAPPING_PATH = "mapping.json"
SAVE_MODEL_PATH = "Models/melody_generation_model.keras"
MODEL_PATH = "./Models/melody_generation_model.h5"