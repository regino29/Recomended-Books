import sqlite3
import nltk
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,RegexpTokenizer
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')

conn = sqlite3.connect('books.db')
c=conn.cursor()

def editData(data):
    stop_words = set(stopwords.words('english'))
    tokenizer = RegexpTokenizer(r'\w+')
    text = tokenizer.tokenize(data)

    filtered_sentence = [] 

    for w in text: 
        if w.lower() not in stop_words: 
            filtered_sentence.append(w)
    
    filtered_sentence=set(filtered_sentence)

    ps = PorterStemmer()
    keywords = [ps.stem(w) for w in filtered_sentence]

    return keywords

try:
    c.execute('DELETE FROM `BX-Books` where ISBN in (select ISBN from `BX-Book-Ratings` br group by br.ISBN having count(ISBN) < 10);')
    conn.commit()

    c.execute('DELETE FROM "BX-Users" WHERE "User-ID" NOT IN (SELECT "User-ID" FROM "BX-Book-Ratings" WHERE ISBN IN (SELECT ISBN FROM "BX-Books") GROUP BY "User-ID" HAVING count("User-ID") > 5)')
    conn.commit()

    conn.cursor().execute('ALTER TABLE "BX-Books" ADD "Keyword" TEXT;')

    print("Database is Updating. Please wait till update is finished. ")
    print("This may take a while!!")

    for i in c.execute('SELECT ISBN,"Book-Title" FROM "BX-Books"').fetchall():
        c.execute('UPDATE "BX-Books" SET Keyword=? WHERE ISBN=?',(', '.join(editData(i[1])),i[0]))
        conn.commit()
    print("DONE")
except:
    print("Databse is already updated")

conn.close()

os.system("pause")