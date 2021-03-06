# -*- coding: utf-8 -*-
"""Heart_disease.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ixrS8lhW86yAH-YJ0eNxSJhLN9AycFrB
"""

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import xgboost as xgb
from sklearn.model_selection import KFold, StratifiedKFold,RandomizedSearchCV
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report, roc_auc_score
import itertools

# Grid search cross validation
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold, learning_curve,StratifiedShuffleSplit
from xgboost import plot_importance

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion Matrix')

    print("confusion matrix:\n%s" % cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=85)
    plt.yticks(tick_marks, classes)
    plt.grid(False)
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    #plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def algorithm_pipeline(X_train_data, X_test_data, y_train_data, y_test_data, 
                       model, param_grid, cv=10, scoring_fit='accuracy',
                       do_probabilities = False):
   # Thanks to CASPER HANSEN-- https://mlfromscratch.com/gridsearch-keras-sklearn/#/
    gs = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_grid, 
        cv=cv, 
        n_jobs=-1, 
        scoring=scoring_fit,
        verbose=2,
        random_state=2017
    )
    
    fitted_model = gs.fit(X_train_data, y_train_data)
    
    if do_probabilities:
      pred = fitted_model.predict_proba(X_test_data)
    else:
      pred = fitted_model.predict(X_test_data)
    
    return fitted_model, pred,gs.cv_results_

"""Load Data"""

heart_data=pd.read_csv("/content/heart.csv")
df1 = heart_data.groupby(['target']).size().reset_index(name='Count')
print(df1)

heart_data_feature = heart_data.loc[:, heart_data.columns != 'target']
labels=heart_data.loc[:, heart_data.columns== 'target']

"""# Balance Split Data"""

features=heart_data_feature.columns.values
stratSplit = StratifiedShuffleSplit(n_splits=2, test_size=0.3, random_state=2019)

for train_index, test_index in stratSplit.split(heart_data_feature, labels):
    print("TRAIN:", train_index, "TEST:", test_index)
    X_train, X_test = heart_data.iloc[train_index][features], heart_data.iloc[test_index][features]
    y_train, y_test = labels.iloc[train_index], labels.iloc[test_index]

"""Baseline Model"""

baselineXGBM = xgb.XGBClassifier(objective='binary:logistic')
kfold=10

kfold = StratifiedKFold(n_splits=10, random_state=7)
results = cross_val_score(baselineXGBM, X_train, y_train, cv=kfold)
# array([0.77272727, 0.81818182, 0.80952381, 0.95238095, 0.9047619 ,
#       0.76190476, 0.57142857, 0.66666667, 0.85714286, 0.66666667])
print("Accuracy: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))  # Accuracy: 77.81% (11.09%)

baselineXGBM.fit(X_train,y_train)
Baseline_prediction=baselineXGBM.predict(X_test)


accuracy_score(y_test, Baseline_prediction)# 0.8131868131868132

# Analysis
label_name=['0','1']

cm = confusion_matrix(y_test, Baseline_prediction, labels=None)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cm, classes=label_name,title='Confusion Matrix')
plt.show()

print(classification_report(y_test, Baseline_prediction))

# Feature Importances

print(baselineXGBM.feature_importances_)


xgb.plot_importance(baselineXGBM)
plt.show()

"""# Hyperparameter tuning"""

param_grid = {'objective':['binary:logistic'],
              'learning_rate': [0.1,0.3,0.5,0.7,1], #so called `eta` value
              'max_depth': [1, 2, 3, 4, 5, 6, 7],
              'min_child_weight': [1e-5, 1e-3, 1e-2],
              'subsample': [0.3,0.5,0.7,1],
              'colsample_bytree': [0.7,1],
              'n_estimators': [100, 200, 300, 400, 500]}


model_XGBM = xgb.XGBClassifier()

fit_xgb_model, pred,cv_results_ = algorithm_pipeline(X_train, X_test, y_train, y_test, model_XGBM, param_grid=param_grid, cv=10)

fit_xgb_model.best_params_

fit_xgb_model.best_score_

accuracy_score(y_test, pred)

"""# Fit model to best parameters and 10-fold cross validaton"""

modelXGBM = xgb.XGBClassifier(colsample_bytree= 1,learning_rate=0.1,max_depth=4,
                              min_child_weight=1e-05,n_estimators=200,
                              objective='binary:logistic',subsample=0.5)
kfold=10

kfold = StratifiedKFold(n_splits=10, random_state=2017)
results = cross_val_score(modelXGBM, X_train, y_train, cv=kfold)

results

print("Accuracy: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))  # Accuracy: 82.12% (7.47%)

modelXGBM.fit(X_train,y_train)
model_prediction=modelXGBM.predict(X_test)

accuracy_score(y_test, model_prediction)

roc_auc_score(y_test, model_prediction)

"""# Analysis"""

label_name=['0','1']

cm = confusion_matrix(y_test, model_prediction, labels=None) # change pred
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cm, classes=label_name,title='Confusion Matrix')
plt.show()

print(classification_report(y_test, model_prediction)) #change predication

# Feature Importances

print(modelXGBM.feature_importances_)


xgb.plot_importance(modelXGBM)
plt.show()

imp_feature=modelXGBM.get_booster().get_score(importance_type='weight')
imp_feature

"""{'age': 415,
 'ca': 131,
 'chol': 345,
 'cp': 162,
 'exang': 37,
 'fbs': 35,
 'oldpeak': 198,
 'restecg': 48,
 'sex': 94,
 'slope': 60,
 'thal': 92,
 'thalach': 333,
 'trestbps': 254}
"""



modelXGBM.get_booster().get_score(importance_type='gain')

imp_featureColName=imp_feature.keys()

imp_featureColName

dict_keys(['thal', 'ca', 'oldpeak', 'chol', 'cp', 'age', 'thalach', 'sex', 'restecg', 'trestbps', 'slope', 'exang', 'fbs'])

# plot decision tree
from numpy import loadtxt
from xgboost import XGBClassifier
from xgboost import plot_tree
import matplotlib.pyplot as plt

plot_tree(modelXGBM,num_trees=2)
fig = plt.gcf()
fig.set_size_inches(150, 100)
fig.savefig('tree2.png')

"""# General Analysis"""

#Using Pearson Correlation
plt.figure(figsize=(20,20))
cor = heart_data.corr()
sns.heatmap(cor, annot=True, cmap=plt.cm.Reds, annot_kws={"size":18})

plt.show()

heart_data_0= heart_data[heart_data['target']==0]
print(heart_data_0.shape)
heart_data_1= heart_data[heart_data['target']==1]
print(heart_data_1.shape)

heart_data_0= heart_data


f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
sns.distplot(heart_data_0["age"], ax=ax1,bins=50, kde=True, color='green', label="No Heart Disease")
sns.distplot(heart_data_1["age"], ax=ax2,bins=50, kde=True, color='red', label="With Heart Disease")

f.legend()
plt.show()

"""# Cholestrol  Analysis"""


ax = sns.boxplot(x="cp", y="age", hue="target",
                 data=heart_data, palette="Set3")

ax = sns.boxplot(x="target", y="chol", hue="target",
                 data=heart_data, palette="Set3")

import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.cm as cm
import seaborn

heart_data

bins = [15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

df2 = heart_data.groupby(pd.cut(heart_data['age'], bins=bins)).agg({'target': 'mean', 
                                                   'chol': 'mean'})

df6 = df2.fillna(0)

np.arange(0, 300, 15)

f, ax = plt.subplots(figsize=(10,5))
pt = sns.barplot(df6.index,df6['chol'] , palette= plt.cm.PuBuGn(df6['target']))
plt.xticks(rotation=50)
plt.yticks(np.arange(100, 315, 15))
plt.ylim(100,300)
plt.title("Cholestrol Within Age Group With CVD")
plt.ylabel("Average Cholestrol Level (mg/dL)")
plt.xlabel('Age')
plt.axhline(y=200,linewidth=2, color='sienna')

i=0
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.annotate('{:.0%}'.format(df6['target'].values[i]), (x, y + height + 2.5))
    i=i+1

"""# Age  Analysis"""


bins = [15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

df3 = heart_data.groupby(pd.cut(heart_data['age'], bins=bins)).agg({'target': 'mean', 
                                                   'age': 'count'})

df3

df3 = df3.fillna(0)
df3

font=14
f, ax = plt.subplots(figsize=(10,5))
pt = sns.barplot(df3.index,df3['age'] , palette= plt.cm.Blues(df3['target']))
plt.xticks(rotation=50)
plt.yticks(np.arange(0, 80, 5))
plt.ylim(0,80)
plt.title("% of People With CVD",fontsize=16)
plt.ylabel("# of people",fontsize=font)
plt.xlabel('Age',fontsize=font)
i=0
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.annotate('{:.0%}'.format(df3['target'].values[i]), (x, y + height + 2.5), fontsize=12)
    i=i+1

"""# HEART RATE"""

bins = np.arange(20, 90, 10)

df4 = heart_data_1.groupby(pd.cut(heart_data_1['age'], bins=bins)).agg({ 
                                                   'thalach': 'mean'})

df4 = df4.fillna(0)

f, ax = plt.subplots(figsize=(10,5))
pt = sns.barplot(df4.index,df4['thalach'])
plt.xticks(rotation=50)
plt.yticks(np.arange(0, 215, 15))
plt.ylim(0,215)
plt.title("Avg Maximum Heart Rate With CVD")
plt.ylabel("Avg Maximum Heart Rate (bpm)")
plt.xlabel('Age')

i=0
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.annotate('{:.2f}'.format(height), (x, y + height + 2.5))
    i=i+1

np.arange(20, 90, 10)

bins = np.arange(20, 90, 10)

df5 = heart_data_0.groupby(pd.cut(heart_data_0['age'], bins=bins)).agg({ 
                                                   'thalach': 'mean'})
df5 = df5.fillna(0)
df5

f, ax = plt.subplots(figsize=(10,5))
pt = sns.barplot(df5.index,df5['thalach'])
plt.xticks(rotation=50)
plt.yticks(np.arange(0, 215, 15))
plt.ylim(0,180)
plt.title("Avg Maximum Heart Rate With No CVD", fontsize=16)
plt.ylabel("Avg Maximum Heart Rate (bpm)", fontsize=14)
plt.xlabel('Age', fontsize=14)

i=0
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.annotate('{:.2f}'.format(height), (x, y + height + 2.5), fontsize=14)
    i=i+1

