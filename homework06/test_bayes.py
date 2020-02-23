import csv
import string

from bayes import NaiveBayesClassifier


def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


with open(f"C:\cs102\homework06\data\SMSSpamCollection",
          encoding='UTF-8') as f:
    data = list(csv.reader(f, delimiter="\t"))
    X, y = [], []
    for target, msg in data:
        X.append(msg)
        y.append(target)
    X = [clean(x).lower() for x in X]
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
    model = NaiveBayesClassifier(alpha=1)
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))
