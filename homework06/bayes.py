from math import log
from typing import List


class NaiveBayesClassifier:

    def __init__(self, alpha):
        self.alpha = alpha
        self.words_dict = {}
        self.classes_dict = {}

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        for sentence, label in zip(X, y):
            word_list = sentence.split()
            for word in word_list:
                if word not in self.words_dict.keys():
                    self.words_dict[word] = {}
                    self.words_dict[word][label] = 1
                else:
                    try:
                        self.words_dict[word][label] += 1
                    except KeyError:
                        self.words_dict[word][label] = 1
                if label not in self.classes_dict.keys():
                    self.classes_dict[label] = 1
                else:
                    self.classes_dict[label] += 1

    def predict(self, X: List[str]) -> List[str]:
        """ Perform classification on an array of test vectors X. """
        predictions = []
        class_prob = 1 / len(self.classes_dict.keys())
        for sentence in X:
            sentence_list = sentence.split()
            curr_max = -1000000
            predicted_class = ''
            for class_ in self.classes_dict.keys():
                y = log(class_prob)
                for word in sentence_list:
                    if word not in self.words_dict.keys():
                        continue
                    else:
                        try:
                            word_prob = ((self.words_dict[word][class_] + self.alpha)
                                         / (self.classes_dict[class_] + self.alpha *
                                            len(self.words_dict.keys())))
                            y += log(word_prob)
                        except KeyError:
                            word_prob = (self.alpha / (
                                                       self.classes_dict[class_] + self.alpha *
                                                       len(self.words_dict.keys())))
                            y += log(word_prob)
                if y > curr_max:
                    predicted_class = class_
                    curr_max = y
            predictions.append(predicted_class)
        return predictions

    def score(self, X_test: List[str], y_test: List[str]) -> float:
        """ Returns the mean accuracy on the given test data and labels. """
        predicted = self.predict(X_test)
        correct_prediction = 0
        for predicted_label, label in zip(predicted, y_test):
            if predicted_label == label:
                correct_prediction += 1
        accuracy = correct_prediction / len(y_test)
        return accuracy
