import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import nltk
nltk.download('stopwords')
from sklearn.feature_extraction import text
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

#import data
pd.set_option('display.max_columns', 100)
df = pd.read_csv("imdb_top_1000.csv",index_col=False)

#Feature Ekstraction
df = df[['Series_Title', 'Overview', 'Genre', 'Director','Star1' ,'Star2' ,'Star3' ,'Star4']]
df["Actor"] = df['Star1'].str.cat(df[["Star2", "Star3", "Star4"]].copy(), sep=" ")
df.drop(['Star1', 'Star2', 'Star3', 'Star4'], inplace=True, axis=1)
df["Director"].str.replace(' ', '')
df.head()

#Data yang akan digunakan
df["Bag_of_Word"] = df['Overview'].str.cat(df[["Overview", "Genre", "Director", "Actor"]].copy(), sep=" ")
df.drop(["Overview", "Genre", "Actor", "Director"], inplace=True, axis=1)
df.head()

# Data Preprocessing
# Data cleaning
df['Bag_of_Word'] = df['Bag_of_Word'].str.replace(r'[^\w\s]+', '').str.replace('\d+', '')

#Case Folding
df['Bag_of_Word'] = df['Bag_of_Word'].str.lower()

#Stopword Removal
stop = stopwords.words('english')
df['Bag_of_Word'] = df['Bag_of_Word'].apply(lambda x: ' '.join([item for item in x.split() if item not in stop]))

#Stemming
porter_stemmer = PorterStemmer()
def stem_sentences(sentence):
    tokens = sentence.split()
    stemmed_tokens = [porter_stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

df['Bag_of_Word_stem'] = df['Bag_of_Word'].apply(stem_sentences)

#Lematisasi

wordnet_lemmatizer = WordNetLemmatizer()

def lema_wordNet(sentence):

    tokens = sentence.split()
    lema_tokens = [wordnet_lemmatizer.lemmatize(token, pos="v") for token in tokens]
    return ' '.join(lema_tokens)
    
df['Bag_of_Word_lema'] = df['Bag_of_Word'].apply(lema_wordNet)

#Data siap pakai
df.set_index('Series_Title')
#df.head()

# Bag of Word

#membangun matriks trnasformasi stemmer
count = CountVectorizer()
count_matrix = count.fit_transform(df['Bag_of_Word_stem'])


#membangun matriks trnasformasi lematisasi
count2 = CountVectorizer()
count_matrix2 = count2.fit_transform(df['Bag_of_Word_lema'])

#menyimpan indeks untuk judul
indices = pd.Series(df.Series_Title)
indices[:5]

# Model Cosine Similarity
#cosine sim stemmer
cosine_sim = cosine_similarity(count_matrix, count_matrix)
#cosine_sim

#cosine sim lema
cosine_sim2 = cosine_similarity(count_matrix2, count_matrix2)
#cosine_sim2


#Fungsi Rekomendasi
def recomend (title, cosine_sim):
    
    result = []
    idx = indices[indices == title].index[0]
    #print (idx)
    
    score = pd.Series(cosine_sim[idx]).sort_values(ascending = False)
    top_10 = list(score.iloc[1:6].index)
    result = indices[top_10]
    return result 

# Seluruh rekomendasi dari setiap data 
Result_of_recomendation = []
for i in df["Series_Title"]:
    result = recomend(i, cosine_sim).index.to_list()
    Result_of_recomendation.append(result)

df["Top 5 stem"] = Result_of_recomendation

Result_of_recomendation = []
for i in df["Series_Title"]:
    result = recomend(i, cosine_sim2).index.to_list()
    Result_of_recomendation.append(result)

df["Top 5 lema"] = Result_of_recomendation

#mengambil judul berdsarkan stemming
def Hasil_Stemm (title) :
    
    x = indices
    x = x.tolist()
    if title in x :
    
        result = [] 
        idx = indices[indices == title].index[0]        
        score = pd.Series(cosine_sim[idx]).sort_values(ascending = False)
        top_10 = list(score.iloc[1:6].index)
        result = indices[top_10]
        result = result.to_frame().reset_index()
        result.drop(["index"], inplace=True, axis=1)
       # print (result)
        return result
    else : return("no film like that")

#mengambil judul berdsarkan lematisasi
def Hasil_Lema (title) :
    
    x = indices
    x = x.tolist()
    if title in x :
    
        result = [] 
        idx = indices[indices == title].index[0]        
        score = pd.Series(cosine_sim2[idx]).sort_values(ascending = False)
        top_10 = list(score.iloc[1:6].index)
        result = indices[top_10]
        result = result.to_frame().reset_index()
        result.drop(["index"], inplace=True, axis=1)
        print (result.values)
        return result
    else : return ("no")

# validasi ketersediaan fil,
def Validator (title) :
    x = indices
    x = x.tolist()
    if title in x :
        return True
    else : return False

df.to_csv('SiapPakaiFilm2.csv')


# EVALUASI
pd.set_option('display.max_columns', 100)
df2 = pd.read_csv('DataValidator.csv', delimiter=',')

df2['Aktual'] = df2.apply(lambda x: list([x['A1'],x['A2'],x['A3'],x['A4'],x['A5']]),axis=1) 

int_df = pd.merge(df, df2, how='inner', on=['Series_Title'])

int_df['Mae_lema'] = [5 - len(set(a) & set(b)) for a, b in zip(int_df['Top 5 lema'], int_df['Aktual'])]
int_df['Mae_stem'] = [5 - len(set(a) & set(b)) for a, b in zip(int_df['Top 5 stem'], int_df['Aktual'])]

df_final = pd.DataFrame().assign(ID=int_df['ID'], Judul=int_df['Series_Title'], R_Stem=int_df['Top 5 stem'],T_Lema=int_df['Top 5 lema'],Aktual=int_df['Aktual'],
                                 MAE_Stem=int_df['Mae_stem'],MAE_Lema=int_df['Mae_lema'])


def passing_final () :
    return df_final

print(df_final.head())