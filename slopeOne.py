from loadData import *

from numpy import genfromtxt
import numpy
import csv

import operator

######### Slope One Per User Average implementation ###########
cur.execute("select userID, avg(rating) from t group by userID;")
userRatingAverages = {}
for row in cur.fetchall():
	userRatingAverages[row[0]] = float(row[1])
###############################################################

#itemCosineDistances = genfromtxt('itemCosineDistances.csv', delimiter=',')
#userCosineDistances = genfromtxt('userCosineDistances.csv', delimiter=',')

#### make a copy of the original user/item/rating matrix 
#slopeOneFullUserRatings = userRatings


#print "populating empty spaces in userRating matrix with average rating per user" 
#print userRatings.shape
#i = 0
#for user in userRatings:
	#j = 0
	#userRatingAvg = userRatingAverages[userAntiMap[i]]
	#print "User "+str(i)+": "+str(user) + " average rating: "+str(userRatingAvg)
	#for rating in user:
		##print "Current Rating: "+str(rating)
		#if rating == 0.0:
			#slopeOneFullUserRatings[i,j] = userRatingAvg
		#j = j+1
	#i = i+1

#numpy.savetxt("slopeOneFullUserRatings.csv", userRatings, delimiter=',')
#print "slopeOneFullUserRatings.csv saved"






dataToRate = genfromtxt('ToRate.csv', delimiter=',')
dataToRate = numpy.delete(dataToRate, (0), axis=0)
dataToRank = genfromtxt('ToRank.csv', delimiter=',')
dataToRank = numpy.delete(dataToRank, (0), axis=0)




#print dataToRate.shape

datafile = open('rating.csv','wb')
wr = csv.writer(datafile,quoting=csv.QUOTE_MINIMAL, delimiter=',')

dataRankFile = open('ranking.json','wb')
wr2 = csv.writer(dataRankFile,quoting=csv.QUOTE_MINIMAL, delimiter=',')

wr.writerow([",","itemID","styleID","userID","Rating"])

i = 0
print "Writing prediction file with Slope-One"
for row in dataToRate:
	currentUser = str(int(row[2]))
	currentItem = str(int(row[0]))
	currentStyle = str(int(row[1]))
	predictedRating = userRatingAverages[currentUser]
	wr.writerow([i,currentItem,currentStyle,currentUser,str(predictedRating)])		
	i = i+1


slopeOneFullUserRatings = genfromtxt('slopeOneFullUserRatings.csv', delimiter=',')

wr2.writerow(["{"])
for user in dataToRank:
	#Check if the user exists, since the list is short we don't need to do a single query with all the items.
	cur.execute('select distinct(userID) from t where userID = \''+str(int(user))+'\'')
	result = cur.fetchone()
	#print "result: "+str(result)
	if result == None:
		print 'select distinct(userID) from t where userID = \''+str(int(user))+'\''
	while result <> None:	
		#print "SQL Result: "+str(result)
		print "User: "+str(int(user))+" userMap: "+str(userMap[str(int(user))])
		currentRow = slopeOneFullUserRatings[userMap[str(int(user))]]
		sortedUserIndex = [ i for (i,j) in sorted(enumerate(currentRow), key=operator.itemgetter(1), reverse=True)]
		topTenIndex = sortedUserIndex[0:10]
		print "TopTen Indexes:" + str(topTenIndex)
		strTopTen = []
		for topItem in topTenIndex:
			strTopTen.append(str(itemAntiMap[topItem]))
		wr2.writerow([str(int(user))+'": '+str(strTopTen)])
		print "TopTen List: "+str(strTopTen)
		result = cur.fetchone()

wr2.writerow(["}"])
datafile.close()
dataRankFile.close()

subprocess.call(['sed','-i.bak','s/\'/"/g','ranking.json'])
subprocess.call(['sed','-i.bak','s/""/"/g','ranking.json'])
subprocess.call(['sed','-i.bak','s/]"/],/g','ranking.json'])

