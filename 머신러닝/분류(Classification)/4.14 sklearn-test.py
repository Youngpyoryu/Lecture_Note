import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
######data load
from sklearn.datasets import load_breast_cancer
#####
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score


###model
from sklearn.tree import DecisionTreeClassifier
##metric
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import mean_squared_error

cancer = load_breast_cancer()

X = cancer.data
y = cancer.target
X_train,X_test, y_train,y_test = train_test_split(X,y, stratify = cancer.target, random_state = 42)



training_accuracy = []
test_accuracy = []

max_dep = range(1,15)
neighbors_setting = range(1,15)
for md in max_dep:
    tree = DecisionTreeClassifier(max_depth=md,random_state=0)
    tree.fit(X_train,y_train)
    training_accuracy.append(tree.score(X_train, y_train))
    test_accuracy.append(tree.score(X_test, y_test))
 
plt.plot(max_dep,training_accuracy, label='Accuracy of the training set')
plt.plot(neighbors_setting,test_accuracy, label='Accuracy of the test set')
plt.ylabel('Accuracy')
plt.xlabel('Max Depth')
plt.legend()
plt.show()