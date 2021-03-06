# Evaluation for pun detection classifiers
# Might compute accuracy, precision, f-measure, etc...

from pandas_ml import ConfusionMatrix
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from functools import reduce
import numpy as np

class Eval:

    DetectionReports = []
    LocationReports = []

    # From this one method, call everything that we want to evaluate the system's performance on pun detection.
    # This way only this one function need be called from main.
    @staticmethod
    def evaluateDetection(classifierName, y_pred, y_true):
        accuracy = Eval.evaluateAccuracy(y_pred, y_true)
        Eval.evaluatePrecisionAndRecall(y_pred, y_true)
        Eval.confusion_matrix(y_pred, y_true)
        Eval.DetectionReports.append({'name': classifierName, 'accuracy': accuracy})

    @staticmethod
    def evaluateLocation(classifierName, y_pred, y_true):
        accuracy = Eval.evaluateAccuracy(y_pred, y_true)
        Eval.LocationReports.append({'name': classifierName, 'accuracy': accuracy})

        correct = len([1 for true, pred in zip(y_true, y_pred) if true == pred])
        guesses = len(y_true)

        precision = recall = correct / guesses
        f_1 = (2 * precision * recall) / (precision + recall)

        print("Precision: %s" % precision)
        print("Recall: %s" % recall)
        print("F1: %s" % f_1)

    @staticmethod
    def confusion_matrix(y_pred, y_true):
        confusion_matrix = ConfusionMatrix(y_true, y_pred)
        print("Confusion matrix:\n%s" % confusion_matrix)

    @staticmethod
    def evaluateAccuracy(y_pred, y_train, type='test'):
        accuracy = accuracy_score(y_pred, y_train)
        print("Accuracy on %s set: %f" % (type, accuracy))
        return accuracy

    @staticmethod
    def evaluatePrecisionAndRecall(y_pred, y_true):
        score = precision_recall_fscore_support(y_true, y_pred, average='weighted')
        print("Precision: %s" % score[0])
        print("Recall: %s" % score[1])
        # Eval.plot_precision_recall(y_pred, y_true)

    @staticmethod
    def print_reports():
        if(len(Eval.DetectionReports)):
            print("\nDetection Classifier Rankings")
            Eval.print_report(Eval.DetectionReports)
        if(len(Eval.LocationReports)):
            print("\nLocation Classifier Rankings")
            Eval.print_report(Eval.LocationReports)

    @staticmethod
    def print_report(report):
        s = sorted(report, key=lambda x:x['accuracy'], reverse=True)
        for index, item in enumerate(s):
            print("%d: %s, Accuracy: %f" % (index+1, item['name'], item['accuracy']))


    @staticmethod
    def plot_precision_recall(y_pred, y_true):
        # All this code has been taken from http://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html
        average_precision = average_precision_score(y_true, y_pred)

        print('Average precision-recall score: {0:0.2f}'.format(
            average_precision))

        precision, recall, _ = precision_recall_curve(y_true, y_pred)

        plt.step(recall, precision, color='b', alpha=0.2,
                 where='post')
        plt.fill_between(recall, precision, step='post', alpha=0.2,
                         color='b')

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title('2-class Precision-Recall curve: AP={0:0.2f}'.format(average_precision))

        plt.show()


