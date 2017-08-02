import numpy as np
import random
import os
import json
import string
from collections import deque

import keras
from keras.models import Sequential, Model
from keras.layers import LSTM, Dense, Activation, Flatten, Concatenate, Input
from keras.optimizers import Adam
from keras.callbacks import TensorBoard

"""An 'experience' consists of a grouping of the previous states and actions we took"""
class Experience():
    def __init__(self):
        self.list = []

    def add(self, qstring, context, attempts, action):
        self.list.append({"qstring":qstring, "context":context, "attempts":attempts, "action":action})

"""This defines the shape of the model we're building in a mostly declarative way"""
class Agent():
    #input_len: Length of the input
    def __init__(self, input_len, context_len):

        chars = list(string.ascii_lowercase + string.digits + "=.;_ '()|%")
        print("Valid character set: ", chars)

        self.char_depth = len(chars)

        self.char_indices = dict((c, i) for i, c in enumerate(chars))
        self.indices_char = dict((i, c) for i, c in enumerate(chars))

        # Build the model
        context_input = Input(shape=(context_len, self.char_depth), name='context_input')
        context_layer_1 = LSTM(32, name='context_layer_1')(context_input)
        context_layer_3 = Dense(128, name='context_layer_3')(context_layer_1)

        qstring_input = Input(shape=(input_len, self.char_depth), name='qstring_input')
        qstring_layer_1 = LSTM(128, name='qstring_layer_1')(qstring_input)
        qstring_layer_3 = Dense(128, name='qstring_layer_3')(qstring_layer_1)

        attempts_input = Input(shape=(self.char_depth,), name='attempts_input')
        attempts_layer_1 = Dense(128, name='attempts_layer_1')(attempts_input)

        x = keras.layers.concatenate([context_layer_3, qstring_layer_3])
        x = Dense(64, name='hidden_layer_1')(x)
        x = keras.layers.concatenate([x, attempts_layer_1])

        # We stack a deep densely-connected network on top
        main_output = Dense(self.char_depth, activation='softmax', name="output_layer")(x)
        self.model = Model(inputs=[context_input, qstring_input, attempts_input], outputs=[main_output])
        print(self.model.summary())

        #"Compile" the model
        #XXX: Hyperparameters here. May need tinkering.
        self.supervised_reward = 1
        self.content = None
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.temperature = .2
        # We want a pretty steep dropoff here
        self.epsilon = .65
        self.input_len = input_len
        self.context_len = context_len

    #Given the current state, choose an action an return it
    #Stochastic! (ie: we choose an action at random, using each state as a probability)
    def act(self, qstring, context, attempts):
        qstring = self.onehot(qstring, self.input_len)
        context = self.onehot(context, self.context_len)
        attempts = self.encodeattempts(attempts)
        #[context_layer, qstring_layer, attempts_layer]
        predictions = self.model.predict_on_batch([context, qstring, attempts])
        action = self.sample(predictions[0], self.temperature)
        #print(predictions, action, self.indices_char[action])
        return self.indices_char[action]

    #Given a stochastic prediction, generate a concrete sample from it
    #temperature: How much we should "smear" the probability distribution. 0 means not at all, high numbers is more.
    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        with np.errstate(divide='ignore'):
            preds = np.asarray(preds).astype('float64')
            preds = np.log(preds) / temperature
            exp_preds = np.exp(preds)
            preds = exp_preds / np.sum(exp_preds)
            probas = np.random.multinomial(1, preds, 1)
            return np.argmax(probas)

    #Update the model for a single given experience
    def train_single(self, action, context, prev_state, attempts, reward):
        #make a one-hot array of our output choices, with the "hot" option
        #   equal to our discounted reward
        action = self.char_indices[action]
        prev_state = self.onehot(prev_state, self.input_len)
        reward_array = np.zeros((1, self.char_depth))
        reward_array[0, action] = reward
        attempts = self.encodeattempts(attempts)
        context = self.onehot(context, self.context_len)
        #[context_layer, qstring_layer, attempts_layer]
        self.model.train_on_batch([context, prev_state, attempts], reward_array)

    # Batch the training
    def train_batch(self, contents, batch_size, epochs, tensorboard=False):
        self.content = contents

        qstrings = np.zeros((len(self.content), self.input_len, self.char_depth))
        contexts = np.zeros((len(self.content), self.context_len, self.char_depth))
        attempts = np.zeros((len(self.content), self.char_depth))
        rewards = np.zeros((len(self.content), self.char_depth))

        for i in range(len(self.content)):
            entry = random.choice(self.content)

            qstrings[i] = self.onehot(entry["qstring"], self.input_len)
            contexts[i] = self.onehot(entry["context"], self.context_len)
            attempts[i] = self.encodeattempts(entry["attempts"])
            reward = self.supervised_reward
            if not entry["success"]:
                reward *= -0.1
            action = self.char_indices[entry["action"]]
            reward_array = np.zeros(self.char_depth)
            reward_array[action] = reward
            rewards[i] = reward_array
        callbacks = []
        if tensorboard:
            callbacks.append(TensorBoard(log_dir='./TensorBoard', histogram_freq=1, write_graph=True))
        self.model.fit([contexts, qstrings, attempts], rewards, callbacks=callbacks,
                        epochs=epochs, batch_size=batch_size, verbose=1, validation_split=0.2)

    # Given a full experience, go back and reward it appropriately
    def train_experience(self, experience, success):
        experience.list.reverse()
        reward = self.supervised_reward
        if not success:
            reward *= -0.1
        i = 0
        for item in experience.list:
            i += 1
            if i > 4:
                if item["action"] == "'":
                    return
                reward *= self.epsilon
                self.train_single(item["action"], item["context"], item["qstring"], item["attempts"], reward)

    #Encode a given string into a 2d array of one-hot encoded numpy arrays
    def onehot(self, string, length):
        assert len(string) <= length
        #First, pad the string out to be 'input_len' long
        string = string.ljust(length, "|")

        output = np.zeros((1, length, self.char_depth), dtype=np.bool)
        for index, item in enumerate(string):
            output[0, index, self.char_indices[item]] = 1
        return output

    def encodeattempts(self, attempts):
        output = np.zeros((1, self.char_depth))
        for i, item in enumerate(attempts):
            output[0, i] = 1
        return output

    def save(self, path):
        self.model.save_weights(path)
        print("Saved model to disk")

    def load(self, path):
        if os.path.isfile(path):
            self.model.load_weights(path)
            print("Loaded model from disk")
        else:
            print("No model on disk, starting fresh")
