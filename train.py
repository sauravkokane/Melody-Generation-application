import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import pickle
import keras
from configurations import SEQUENCE_LENGTH, \
        OUTPUT_UNITS, \
        NUM_UNITS, LOSS, \
        LEARNING_RATE, \
        NUM_EPOCHS, \
        BATCH_SIZE, \
        SAVE_MODEL_PATH

def load_generated_sequences():
    with open("songs_inputs.pkl", "rb") as f:
        inputs = pickle.load(f)
        
    with open("songs_targets.pkl", "rb") as f:
        targets = pickle.load(f)
    return inputs, targets

def build_model(output_units, num_units, loss_function, learning_rate):
    """
    Builds a model with the specified architecture and compiles it with the
    specified loss function and optimizer.

    Parameters
    ----------
    output_units : int
        The number of output units of the model.
    num_units : list of int
        The number of units in each layer of the model.
    loss_function : str
        The name of the loss function to use.
    learning_rate : float
        The learning rate of the optimizer.

    Returns
    -------
    model : keras.Model
        The compiled model.
    """

    # create model architecture
    input_layer = keras.layers.Input(shape=(None, output_units))

    x = keras.layers.LSTM(num_units[0])(input_layer)
    x = keras.layers.Dropout(0.2)(x)

    output_layer = keras.layers.Dense(output_units, activation="softmax")(x)


    model = keras.Model(input_layer, output_layer)

    # compile model
    model.compile(loss=loss_function, optimizer=keras.optimizers.Adam(learning_rate=learning_rate), metrics=["accuracy"])

    model.summary()

    return model

def train_model(
        output_units=OUTPUT_UNITS, num_units=NUM_UNITS, 
        loss_function=LOSS, learning_rate=LEARNING_RATE):

    # get generated sequences
    inputs, targets = load_generated_sequences()

    # create model
    model = build_model(output_units, num_units, loss_function, learning_rate)

    # train model
    model.fit(inputs, targets, epochs=NUM_EPOCHS, batch_size=BATCH_SIZE)

    # save model
    model.save(SAVE_MODEL_PATH)


if __name__ == "__main__":
    train_model()