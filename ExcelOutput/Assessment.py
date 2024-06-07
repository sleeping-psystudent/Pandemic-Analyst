import numpy as np
import joblib
import pandas as pd

from sklearn.model_selection import LeaveOneOut
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA

def DataTrain(model, y, X):
    # Leave One Out
    loo = LeaveOneOut()
    best_score = 0

    for train_index, test_index in loo.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        
        # train
        model.fit(X_train, y_train)
        # predict
        y_pred = model.predict(X_test)
        # evalute
        score = accuracy_score(y_test, y_pred)
        if score > best_score:
            # store the model
            joblib.dump(model, "logr46.pkl")

def Train():
    file_path = "Analyze.xlsx"
    df = pd.read_excel(file_path)
    re_df = df.iloc[:,2:14]
    re_df['Status'] = re_df['Status'].map({'Watchlist': 1, 'Low': 2, 'Medium': 3})

    X=re_df.iloc[:,1:]
    y=re_df[['Status']]

    # PCA
    pca = PCA(n_components=6)
    newX = pca.fit_transform(re_df)
    joblib.dump(pca, 'pcaˊ.pkl')
    # extract y value
    newy = y['Status'].values
    # train model
    logr = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
    DataTrain(logr, newy, newX)

def Analyze(scores):
    pca = joblib.load('pca46.pkl')
    logr = joblib.load('logr46.pkl')

    re_scores = np.array([scores])
    pca_scores = pca.transform(re_scores)
    prediction = logr.predict(pca_scores)

    if prediction == 3:
        return "Medium"
    elif prediction == 2:
        return "Low"
    elif prediction == 1:
        return "Watchlist"
    return "Error"