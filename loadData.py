import csv, sqlite3
from numpy import genfromtxt
import numpy
import subprocess
import scipy.spatial.distance as dst

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE t (userID, itemID, styleID, rating);")

with open('training_tarea1.csv','rb') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['userID'], i['itemID'],i['styleID'],i['rating']) for i in dr]

cur.executemany("INSERT INTO t (userID, itemID, styleID, rating) VALUES (?, ?, ?, ?);", to_db)
con.commit()


############## Construct User - Item - Rating matrix ###################3
userMap = {}
userAntiMap={}

itemMap = {}
itemAntiMap = {}

userList = []
cur.execute("select distinct(userID) from t;")
i = 0
for row in cur.fetchall():
	userID = str(row[0])
	userList.append(userID)
	userMap[userID] = i
	userAntiMap[i] = userID
	i= i+1

itemList = []
cur.execute("select distinct(itemID) from t;")
i = 0
for row in cur.fetchall():
        itemID = str(row[0])
	itemList.append(itemID)
        itemMap[itemID] = i
	itemAntiMap[i] = itemID
        i= i+1


rows =  len(userMap)	
columns = len(itemMap)



userRatings = numpy.zeros((rows,columns) , dtype=numpy.float)

cur.execute("select userID, itemID, rating from t;")
for row in cur.fetchall():
	user = row[0]
	item = row[1]
	rating = row[2]
	userRatings[userMap[user],itemMap[item]] = rating


print "Saving userRatings matrix, please wait"
numpy.savetxt("userRatings.csv", userRatings, delimiter=',')
print "userRating matrix saved"

cur.execute("select userID, avg(rating) from t group by userID;")
userRatingAverages = {}
for row in cur.fetchall():
        userRatingAverages[row[0]] = float(row[1])

#### Review matrix in TOPCAT ###################
#subprocess.call(['java','-jar','/home/abarrien/topcat/topcat-full.jar','-f','csv','userRatings.csv'])

#####################################################


data = genfromtxt('training_tarea1.csv', delimiter=',')
data = numpy.delete(data, (0), axis=0)

