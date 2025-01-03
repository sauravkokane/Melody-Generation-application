import pickle
import numpy as np

SEQUENCE_LENGTH = 64

def load_generated_sequences():
    with open("songs_inputs.pkl", "rb") as f:
        inputs = pickle.load(f)
        
    with open("songs_targets.pkl", "rb") as f:
        targets = pickle.load(f)
    return inputs, targets

def train_model():

    # get generated sequences
    inputs, targets = load_generated_sequences()

    # create model

    # train model

    # save model