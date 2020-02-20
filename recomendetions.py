import sqlite3
import nltk
import random
import os


def createUserProfile(userID):


    books=c.execute('SELECT ISBN,"Book-Rating" FROM "BX-Book-Ratings" WHERE ISBN IN (SELECT ISBN FROM "BX-Books") AND "User-ID"="'+ str(userID[0])+'" ORDER BY "Book-Rating" DESC limit 3').fetchall()
    profile=[]
    for i in books:
        isbn=i[0]
        key=c.execute('SELECT Keyword,"Book-Author","Year-Of-Publication" FROM "BX-Books" where "ISBN"="'+str(isbn)+'"').fetchall()
        profile.append(key)
    
    keyword=[]
    author=[]
    year=[]
    for i in profile:
        keyword.append(i[0][0])
        author.append(i[0][1])
        year.append(i[0][2])
    k=str(keyword).replace('[','').replace(']','').replace("'",'')

    a=str(author).replace('[','').replace(']','')

    y=str(year).replace('[','').replace(']','')

    return k,a,y

def createBookProfile(key):
    keyword=[]
    author=[]
    year=[]
    keyword.append(key[0])
    author.append(key[1])
    year.append(key[2])

    k=str(keyword).replace('[','').replace(']','').replace("'",'')

    a=str(author).replace('[','').replace(']','')

    y=str(year).replace('[','').replace(']','')
    return (k,a,y)

def distance(x, y):
    if x >= y:
        result = x - y
    else:
        result = y - x
    return result

def jaccard(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union

def similarityWithJacard(userProfile,bookProfile):
    #calculate jacard
    userKey=userProfile[0].split(', ')
    bookKey=bookProfile[0].split(', ')
    jac=jaccard(userKey,bookKey)

    #Author
    userAuth=userProfile[1].split(', ')
    bookAuth=bookProfile[1].split(', ')
    auth=0.0
    for i in userAuth:
        if(i==bookAuth[0]):
            auth=0.4
            
        
    #Year

    userYear=userProfile[2].split(', ')
    bookYear=bookProfile[2].split(', ')

    max=0
    for i in userYear:
        if(i<'9999' and i>'0' and bookYear[0]<'9999' and bookYear[0]>'0'):
            if(1-(distance(int(i),int(bookYear[0]))/2005)>max):
                max=1-(distance(int(i),int(bookYear[0]))/2005)

    sim=jac*0.2+auth+max*0.4
    

    return(sim)

def dice_coefficient(a, b):
    """dice coefficient 2nt/(na + nb)."""
    a_bigrams = set(a)
    b_bigrams = set(b)
    overlap = len(a_bigrams & b_bigrams)
    return overlap * 2.0/(len(a_bigrams) + len(b_bigrams))

def similarityWithDice(userProfile,bookProfile):
    #calculate Dice
    userKey = userProfile[0].split(', ')
    bookKey = bookProfile[0].split(', ')
    dic=dice_coefficient(userKey,bookKey)

    #Author
    userAuth = userProfile[1].split(', ')
    bookAuth = bookProfile[1].split(', ')
    auth=0.0
    for i in userAuth:
        if(i==bookAuth[0]):
            auth=0.3
            
        
    #Year

    userYear = userProfile[2].split(', ')
    bookYear = bookProfile[2].split(', ')

    max=0
    for i in userYear:
        if(i<'9999' and i>'0' and bookYear[0]<'9999' and bookYear[0]>'0'):
            if(1-(distance(int(i),int(bookYear[0]))/2005)>max):
                max=1-(distance(int(i),int(bookYear[0]))/2005)

    sim=dic*0.5+auth+max*0.2

    return(sim)

def findRecomandedBooks(profile,userID):
    unrated=conn.cursor().execute('SELECT Keyword,"Book-Author","Year-Of-Publication","Book-Title",ISBN FROM "BX-Books" WHERE ISBN NOT IN(SELECT ISBN FROM "BX-Book-Ratings" WHERE "User-ID"="'+str(userID[0])+'" )').fetchall()
 
    recomendedJac=[]
    recomendedDice=[]

    for book in unrated:
        bookProfile=createBookProfile(book)


        jac = similarityWithJacard(profile,bookProfile)
        jacardSimilarity = [book[4],book[3],jac]
        recomendedJac.append(jacardSimilarity)

        dic = similarityWithDice(profile,bookProfile)
        diceSimilarity=[book[4],book[3],dic]
        recomendedDice.append(diceSimilarity)
    
    recomendedJac = sorted(recomendedJac, key = lambda i: i[2],reverse=True)[:10]
    recomendedDice = sorted(recomendedDice, key = lambda i: i[2],reverse=True)[:10]

    return (recomendedJac,recomendedDice)

def calculateOverlap(similarities):
    
    jac=[]
    dic=[]
    sum=0
    for i in range(10):
        jac.append(similarities[0][i][0])
        dic.append(similarities[1][i][0])
        intersection=list(set(jac) & set(dic))
        sum+=len(intersection)/(i+1)*(1.0)
    return (sum/10)
    
def findGoldenStandard(similarities):

    goldenStandard=[]

    for i in similarities[0]:
        count=1
        for j in similarities[1]:
            if(i[0] in j ):
                count=2
        goldenStandard.append(tuple([i[0],i[1],i[2],count]))
    
    for i in similarities[1]:
        count=1
        for j in similarities[0]:
            if(i[0] in j ):
                count=2
        goldenStandard.append(tuple([i[0],i[1],i[2],count]))
    
    

    items_to_remove=[]

    for i in goldenStandard:
        for j in goldenStandard:
            if(i!=j):
                if(i[0]==j[0]):
                    if(i[2]<j[2]):
                        items_to_remove.append(i)
                    else:
                        items_to_remove.append(j)
    
    for i in set(items_to_remove):
        goldenStandard.remove(i)
    


    goldenStandard=sorted(goldenStandard, key = lambda x: (x[3], x[2]),reverse=True)[:10]

    return goldenStandard

def writeToFiles(fileName,id,similarity):
    file1=open(fileName+'.txt','w',encoding='utf-8')
    file1.write("UserID: "+id+"\n")
    file1.write("----------------------------------------------------------------------\n")
    count=1
    for j in similarity:
        file1.write("Book: "+str(count)+"\n")
        file1.write("ISBN: "+str(j[0])+"\nTittle: "+str(j[1])+"\nSimilarity: "+str(j[2])+"\n")
        file1.write("\n")
        count+=1
    file1.close()


conn = sqlite3.connect('books.db')
c = conn.cursor()

id = c.execute('SELECT "User-ID" FROM "BX-Users"').fetchall()
users = random.sample(range(0, len(id)-1), 5)

file1 = open("overlaps"+'.txt','w',encoding='utf-8')

for i in range(5):
    profile  =[]
    profile = createUserProfile(id[users[i]])
    recomandedJacard,recomendedDice = findRecomandedBooks(profile,id[0])
    goldenStandard = findGoldenStandard([recomandedJacard,recomendedDice])

    #Write to recomendet books to txt Files

    writeToFiles("jacard_"+str(id[users[i]][0]),str(id[users[i]][0]),recomandedJacard)
    writeToFiles("dice_"+str(id[users[i]][0]),str(id[users[i]][0]),recomendedDice)

    print("\nUser "+str(i+1)+" ID: "+ str(id[users[i]][0]))
    print("---------------------------------------------------------")
    print("Overlap Jaccard - Dice Coefficient = "+str(calculateOverlap([recomandedJacard,recomendedDice])))
    print("Overlap Golden Standard - Jaccard  = "+str(calculateOverlap([recomandedJacard,goldenStandard])))
    print("Golden Standard - Dice Coefficient = "+str(calculateOverlap([goldenStandard,recomendedDice])))

    file1.write("\nUser "+str(i+1)+" ID: "+ str(id[users[i]][0])+"\n")
    file1.write("---------------------------------------------------------"+"\n")
    file1.write("Overlap Jaccard - Dice Coefficient = "+str(calculateOverlap([recomandedJacard,recomendedDice]))+"\n")
    file1.write("Overlap Golden Standard - Jaccard  = "+str(calculateOverlap([recomandedJacard,goldenStandard]))+"\n")
    file1.write("Golden Standard - Dice Coefficient = "+str(calculateOverlap([goldenStandard,recomendedDice]))+"\n")

file1.close()

conn.close()

os.system("pause")