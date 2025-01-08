
## generate_melody

It takes a `seed` (a sequence of musical notes), and generates a new melody by iteratively predicting the next note based on the previous notes. The prediction is done using a neural network model (`self.model`).

Here's a step-by-step breakdown:

1. The `seed` is split into individual notes and prepended with a fixed sequence of start symbols (`self._start_symbols`).
2. The notes in the seed are mapped to numerical values using a dictionary (`self._mapping`).
3. The algorithm then enters a loop, where it:
	* Limits the seed to a maximum length (`max_sequence_length`).
	* One-hot encodes the seed notes.
	* Adds a batch dimension to the one-hot encoded seed (since the model expects a batch of inputs).
	* Makes a prediction using the model, which outputs a probability distribution over possible next notes.
	* Samples from this probability distribution to select the next note, using a temperature parameter to control the randomness of the selection.

The loop repeats for a specified number of steps (`num_steps`), generating a new melody note by note.


## _sample_with_temperature:

1. **Log scaling**: `predictions = np.log(probabilities) / temperature`
	* This line applies a log scaling to the probabilities, which has the effect of "stretching" or "compressing" the probability distribution.
	* When `temperature` is high, the log scaling reduces the differences between probabilities, making them more similar.
	* When `temperature` is low, the log scaling amplifies the differences between probabilities, making the most probable symbol even more likely.
2. **Softmax normalization**: `probabilities = np.exp(predictions) / np.sum(np.exp(predictions))`
	* This line applies the softmax function to the log-scaled predictions, which normalizes the values to ensure they add up to 1.
	* The softmax function maps the log-scaled predictions to a probability distribution, where each value is between 0 and 1.
3. **Random sampling**: `index = np.random.choice(choices, p=probabilities)`
	* This line uses NumPy's `random.choice` function to select a random index from the `choices` array (which contains integers from 0 to `len(probabilities)-1`).
	* The `p` parameter specifies the probability distribution to use for the sampling, which is the softmax-normalized probabilities calculated in step 2.

By adjusting the `temperature` parameter, the code can control the level of randomness in the sampling process. When `temperature` is high, the sampling is more random and uniform, while when `temperature` is low, the sampling is more deterministic and favors the most probable symbol.:

1. **Log scaling**: `predictions = np.log(probabilities) / temperature`
	* This line applies a log scaling to the probabilities, which has the effect of "stretching" or "compressing" the probability distribution.
	* When `temperature` is high, the log scaling reduces the differences between probabilities, making them more similar.
	* When `temperature` is low, the log scaling amplifies the differences between probabilities, making the most probable symbol even more likely.
2. **Softmax normalization**: `probabilities = np.exp(predictions) / np.sum(np.exp(predictions))`
	* This line applies the softmax function to the log-scaled predictions, which normalizes the values to ensure they add up to 1.
	* The softmax function maps the log-scaled predictions to a probability distribution, where each value is between 0 and 1.
3. **Random sampling**: `index = np.random.choice(choices, p=probabilities)`
	* This line uses NumPy's `random.choice` function to select a random index from the `choices` array (which contains integers from 0 to `len(probabilities)-1`).
	* The `p` parameter specifies the probability distribution to use for the sampling, which is the softmax-normalized probabilities calculated in step 2.

By adjusting the `temperature` parameter, the code can control the level of randomness in the sampling process. When `temperature` is high, the sampling is more random and uniform, while when `temperature` is low, the sampling is more deterministic and favors the most probable symbol.