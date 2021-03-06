from keras.models import Sequential
from keras.layers import Dense, Embedding, Bidirectional, Dropout
from keras.layers import LSTM, Input, TimeDistributed
from keras.preprocessing.sequence import pad_sequences
from sklearn.base import BaseEstimator, ClassifierMixin
from keras.preprocessing.text import Tokenizer
from word_embeddings import WordEmbeddings
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np

MAX_NB_WORDS = 20000

class PunRNNDetectionClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, graphic="combined"):
        """
        output can be one of:
            - word
            - sequence
            - binary
        """

        self.name = "Pun RNN Detection %s" % graphic
        self.embedding = WordEmbeddings()
        self.use_keras_caching = True # how to cache other properties not on model?

    def train(self, x_train, y_train):
        self.y_train = y_train
        self.fit_xs(x_train)
        self.x_train = self.format_xs(x_train)

        num_words = min(MAX_NB_WORDS, len(self.word_index) + 1)
        embedding_matrix = self.embedding.get_matrix(self.word_index, num_words)

        self.model = Sequential()
        self.model.add(
            Embedding(
                num_words,
                self.embedding.embedding_length,
                weights = [ embedding_matrix ],
            )
        )
        self.model.add(Dropout(.2))
        self.model.add(Bidirectional(
            LSTM(128, dropout=.8, input_dim=300),
            merge_mode='ave'
        ))
        self.model.add(Dense(1, activation='sigmoid'))
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        for i in range(1, 3):
            print("epoch ", i)
            for x, y in zip(self.x_train, self.y_train):
                x = x.reshape(1, len(x))
                y = np.asarray([y])

                self.model.fit(x, y, batch_size=1, epochs=1, verbose=0)

        return self.get_binary_predictions(self.x_train)

    def get_binary_predictions(self, xs):
        predictions = []
        for x in xs:
            x = x.reshape(1, len(x))
            prediction = self.model.predict_classes(x, batch_size=1, verbose=0)[0][0]
            predictions.append(prediction)

        return predictions

    def get_binary_predictions_with_probabilities(self, xs):
        predictions = []
        for x in xs:
            x = x.reshape(1, len(x))
            prediction = self.model.predict_proba(x, batch_size=1, verbose=0)[0][0]
            predictions.append([1-prediction, float(prediction)])

        return predictions


    def test(self, x_test):
        self.x_test = self.format_xs(x_test)

        return self.get_binary_predictions(self.x_test)

    def format_xs(self, xs):
        return np.asarray([np.asarray([self.word_index.get(t.lower(), 0) for t in x]) for x in xs])

    def fit_xs(self, xs):
        tokenizer = Tokenizer(num_words=MAX_NB_WORDS)
        tokenizer.fit_on_texts([' '.join(x) for x in xs])
        self.word_index = tokenizer.word_index

    def test_with_probabilities(self, x_test):
        self.x_test = self.format_xs(x_test)
        return self.get_binary_predictions_with_probabilities(self.x_test)

    def fit(self, x_train, y_train=None):
        self.train(x_train, y_train)

        return self

    def predict(self, x):
        return self.test(x)

    def predict_proba(self, x):
        return self.test_with_probabilities(x)

    def score(self, x, y, sample_weight=None):
        from sklearn.metrics import accuracy_score
        return accuracy_score(y, self.predict(x), sample_weight=sample_weight)

