import matplotlib.pyplot as plt
import numpy as np
import string

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.decomposition import TruncatedSVD
from unicodedata import normalize
from wordcloud import WordCloud

def clean_text(doc):

    stop_words = stopwords.words('portuguese')
    stop_words.extend(stopwords.words('english'))
    stop_words.extend(list(string.punctuation))
    # stopwords específicas do domínio
    stop_words.extend(['cm', 'feature', 'features', 'informações', 'itens', 'leve', 'list', 'nulo', 'package', 'pacote', 'pacotes', 'recurso', 'tamanho', 'ver'])
    # remover da lista de stopwords a palavra sem para formar o bigrama "sem fio", relevante para o domínio
    # primeira rodada de classificação demonstrou que não foi uma boa escolha
    # stop_words.remove('sem')
    
    doc = doc.lower()
    doc = normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')

    tokens = [token for token in word_tokenize(doc) if token not in stop_words]
    doc = ' '.join(tokens)
    
    return doc

def plot_docs_matrix(docs_matrix, true_targets=None, predicted_targets=None):
    pca = TruncatedSVD(n_components=2)
    pca_matrix = pca.fit_transform(docs_matrix)
    scatter_x = pca_matrix[:, 0] # first principle component
    scatter_y = pca_matrix[:, 1] # second principle component
    
    if predicted_targets is None:
        fig,ax = plt.subplots(figsize=(5,5))
        if true_targets is not None:
            for group in np.unique(true_targets):
                ix = np.where(true_targets == group)
                ax.scatter(scatter_x[ix], scatter_y[ix], label=group, s=5)
                ax.set_title('Documents: true Classes')   
        else:
            ax.scatter(scatter_x, scatter_y, s=5)
            ax.set_title('Documents')
        ax.set_xticks([])
        ax.set_yticks([])
        
    else:
        fig,axs = plt.subplots(1,2,figsize=(10,5))
        if true_targets is not None:
            for group in np.unique(true_targets):
                ix = np.where(true_targets == group)
                axs[0].scatter(scatter_x[ix], scatter_y[ix], label=group, s=5)
                axs[0].set_title('Documents: true Classes')   
        else:
            axs[0].scatter(scatter_x, scatter_y, s=5)
            axs[0].set_title('Documents')
        
        for group in np.unique(predicted_targets):
            ix = np.where(predicted_targets == group)
            axs[1].scatter(scatter_x[ix], scatter_y[ix], label=group, s=5)
            axs[1].set_title('Documents: predicted Classes')

        for ax in axs.flat:
            ax.set_xticks([])
            ax.set_yticks([])
        
    plt.show()

def plot_wordcloud(wc_docs,max_words=50):
   
    wc = WordCloud(max_words=max_words,height=300).generate(wc_docs)
    wc_no_bigram = WordCloud(max_words=max_words,height=300,collocation_threshold=-1).generate(wc_docs)
    
    fig,ax = plt.subplots(1,2,figsize=(15,5))
    
    ax[0].imshow(wc, interpolation="bilinear")
    ax[0].axis("off")
    ax[0].set_title('Principais palavras com bigramas')
    
    ax[1].imshow(wc_no_bigram, interpolation="bilinear")
    ax[1].axis("off")
    ax[1].set_title('Principais palavras sem bigramas')
    plt.show()
    