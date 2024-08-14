

import pandas as pd
from nltk.corpus import stopwords

from joblib import dump

from sklearn import __version__ as sklearn_version

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score


FILE_ITEMS = r'Z:\anatel\inova-fiscaliza\dados-pacp\datasets\label_issues\20240423\results\items.parquet'


if __name__ == '__main__':
    
    df_items = pd.read_parquet(FILE_ITEMS)
       
    map_passivel = {0: 'Não', 1: 'Sim'}
    target_names = list(map_passivel.values())
    
    # stop words
    stop_words = stopwords.words('portuguese')
    stop_words.extend(stopwords.words('english'))
    
    # vetorizar as palavras por contagem
    vectorizer = CountVectorizer(ngram_range=(1,2),stop_words=stop_words)

    # transformar vetores aplicando TF-IDF
    transformer = TfidfTransformer()

    # classificardor SGD
    clf = SGDClassifier(alpha=1e-5, loss='log_loss', penalty='l2')

    # juntar tudo em pipeline
    pipe = Pipeline(steps=[('vectorizer',vectorizer),('transformer',transformer),('clf',clf)])

    # 
    docs = df_items[df_items['passivel_homologacao']<2]['nome']
    labels = df_items[df_items['passivel_homologacao']<2]['passivel_homologacao']

    X_train, X_test, y_train, y_test = train_test_split(docs, labels, test_size=0.25, random_state=123)

    pipe.fit(X_train,y_train)
    
    # persist model
    file_model_name = f'Z:\\anatel\\inova-fiscaliza\\dados-pacp\\model_trainning\\clf_mktplaces_3\\clf_marketplaces_scikit-learn-{sklearn_version}.joblib'
    dump(pipe, file_model_name) 

    predicted = pipe.predict(X_test)
    y_scores = pipe.decision_function(X_test)
    auc_sgd = roc_auc_score(y_test,pipe.predict_proba(X_test)[:,1])


    print('Accuracy of SGD classifier on training set: {:.3f}'
        .format(pipe.score(X_train, y_train)))
    print('Accuracy of SGD classifier on test set: {:.3f}'
        .format(pipe.score(X_test, y_test)))
    print('AUC of SGD classifier on training set: {:.3f}'
        .format(roc_auc_score(y_train,pipe.predict_proba(X_train)[:,1])))
    print('AUC of SGD classifier on test set: {:.3f}'
        .format(roc_auc_score(y_test,pipe.predict_proba(X_test)[:,1])))

    print()
    print(classification_report(y_test, predicted, target_names=target_names))