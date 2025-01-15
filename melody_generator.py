import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import json
import numpy as np
import keras
import music21 as m21


from configurations import MAPPING_PATH, SEQUENCE_LENGTH, MODEL_PATH, SAVE_MODEL_PATH, LOSS

class MelodyGenerator:
    def __init__(self, model_path=MODEL_PATH):
        """
        Initializes the MelodyGenerator class.

        Parameters
        ----------
        model_path : str
            The path to the model to be used for generating melodies.
        """
        self.model_path = model_path
        self.model = keras.models.load_model(model_path)
        
        with open(MAPPING_PATH, "r") as mapping_file:
            self._mapping = json.load(mapping_file)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH

    def generate_melody(self, seed, num_steps, max_sequence_length, temperature):
        """
        Generates a melody based on the given seed.

        Parameters
        ----------
        seed : str
            The initial sequence of notes to generate from.
            Example: '55 _ 60 _ 64 _ 67 _ 69 _ 67 _ _ 65'
        num_steps : int
            The number of steps to generate the melody for.
        max_sequence_length : int
            The maximum length of the sequence to generate.
        temperature : float
            The temperature parameter to use for sampling from the output distribution.

        Returns
        -------
        list
            A list of notes representing the generated melody.
        """
        
        # create seed with start symbols
        seed = seed.split()
        melody = seed
        seed = self._start_symbols + seed
        
        # map seed to numbers
        seed = [self._mapping[symbol] for symbol in seed]
        
        for _ in range(num_steps):
            # limit the seed to max_sequence_length
            seed = seed[-max_sequence_length:]

            # one-hot encode the seed
            onehot_seed = keras.utils.to_categorical(seed, num_classes=len(self._mapping))
            # dimension of onehot_seed: (max_sequence_length, len(self._mapping))
            # but the model expects the dimension to be (batch_size, max_sequence_length, len(self._mapping))
            # so we add a batch dimension to the seed
            onehot_seed = onehot_seed[np.newaxis, ...]

            # make a prediction
            # As we can pass multiple samples at once, and we only have one sample, we take the first one
            probabilities = self.model.predict(onehot_seed, verbose=0)[0]
            # probailities will be an array [0.1, 0.2, 0.1, 0.6,.....] of output units dimension whose sum is 1
            # we will sample from this array to get the next symbol
            output_int = self._sample_with_temperature(probabilities, temperature)

            # Update seed
            seed.append(output_int)

            # map the output int to the symbol
            output_symbol = [key for key, val in self._mapping.items() if val == output_int][0]

            # check if we have reached the end of the melody
            if output_symbol == "/":
                break   
            # update the melody
            melody.append(output_symbol)

        return melody
    
    def _sample_with_temperature(self, probabilities, temperature):
        """
        Samples an index from a probability distribution using temperature scaling.

        This method adjusts the provided probability distribution according to the
        specified `temperature`, and samples an index based on the adjusted distribution.
        A higher temperature results in more random samples, while a lower temperature
        favors the most probable indices.

        Parameters
        ----------
        probabilities : numpy.ndarray
            An array representing the probability distribution over possible choices.
        temperature : float
            A parameter that controls the randomness of the sampling process. Higher
            values increase randomness, while lower values make the sampling more
            deterministic.

        Returns
        -------
        int
            The sampled index from the adjusted probability distribution.
        """
        
        # temperature is a parameter that controls the randomness of the sampling
        # higher temperature means more randomness
        # if temperature -> infinity, all probabilities will be the same, its like randomly selecting one of the symbols
        # if temperature -> 0, we will always select the symbol with the highest probability
        # if temperature = 1, we will sample from the given probabilities, which is the most common scenario
        predictions = np.log(probabilities) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))

        choices = range(len(probabilities)) # [0, 1, 2, 3, ...., len(probabilities)]
        index = np.random.choice(choices, p=probabilities)
    
        return index
    

    def save_melody(self, melody, step_duaration=0.25, format='midi', output_path="mel.mid"):
        """
        Saves a melody to a file in the specified format.

        Parameters
        ----------
        melody : list
            A list of symbols representing the melody to be saved.
        step_duaration : float, optional
            The duration of each step in the melody. Defaults to 0.25.
        format : str, optional
            The format to save the melody in. Defaults to 'midi'.
        output_path : str, optional
            The path to save the melody to. Defaults to 'mel.mid'.
        """
        # Create a music21 stream
        stream = m21.stream.Stream()

        # Parse all symbols and convert them into note/rest objects.
        # '60', '_', '_', '_', '62', '_', ....
        current_symbol = None
        step_counter = 1
        for i, symbol in enumerate(melody):
            # handle note or rest
            if symbol != "_" or i+1==len(melody):
                if current_symbol is not None:
                    quarter_length_duration = step_duaration * step_counter
                    # handle a rest
                    if current_symbol == "r":
                        m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                    # handle a note
                    else:
                        m21_event = m21.note.Note(int(current_symbol), quarterLength=quarter_length_duration)

                    stream.append(m21_event)
                    step_counter = 1
                current_symbol = symbol

            # handle prolongations "_"
            else:
                step_counter += 1

        # write a m21 stream to a midi file
        stream.write(format, output_path)

        return stream


if __name__ == "__main__":
   
    melody_generator = MelodyGenerator(model_path=SAVE_MODEL_PATH)
    seed = "60 _ 60 _ 67 _ _ _ 67 _ _ _ 67 _ _ _ 67 _ _ _ 69 _ 65 _ 67 _ _ _ 69 _ 65 _ 69"
    melody = melody_generator.generate_melody(seed, 500, 64, 0.76)
    print(melody)
    song = melody_generator.save_melody(melody, output_path="mel_model_k.mid")
    song.show()

        






