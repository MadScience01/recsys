from loadData import *
import operator


def ubcf(userIndex,itemIndex):
	
	####  K Nearest Neighbors
	k = 20
	
	currentUserAverageRating = userRatingAverages[userAntiMap[userIndex]]
	fullneighborhood = pearsonMatrix[userIndex]
	k_neighborUsers = [ i for (i,j) in sorted(enumerate(fullneighborhood), key=operator.itemgetter(1),reverse=True)][0:k]
	print "Current User: " + str(userAntiMap[userIndex]) + " Current Item: "+str(itemAntiMap[itemIndex])
	print "K-Neighbors: "+str(k_neighborUsers)
	partialSum = 0.
	for neighbor in k_neighborUsers:
#		try:
#			print "NeighborIndex: "+str(neighbor)
#			print "Similarity: "+str(pearsonMatrix[userIndex,neighbor])
#			print "Rni: "+str(userRatings[neighbor,itemIndex])
#			print "Neighbor Rating Average: "+str(userRatingAverages[str(userAntiMap[neighbor])])
			partialSum = partialSum + pearsonMatrix[userIndex,neighbor]*(userRatings[neighbor,itemIndex] - userRatingAverages[str(userAntiMap[neighbor])])
			
#		except ValueError as e:
#			print "Error while trying to generate prediction for userIndex: "+str(userIndex)+" itemIndex: "+str(itemIndex)+ str(e)
	numerator = partialSum
#	print "Numerator: "+str(numerator)
	partialSum = 0.
        for neighbor in k_neighborUsers:
                partialSum = partialSum + pearsonMatrix[userIndex,neighbor]
	denominator = partialSum
#	print "Denominator: "+str(denominator)
	if denominator <> 0.:
		prod = numerator / denominator
	else:
		prod = 0.
	prediction = currentUserAverageRating + prod
	if prediction < 0.:
		prediction = 0.
		
	
	return prediction	
	######## return integer prediction #########
		
	#if prediction > 0 and (prediction % float(int(prediction))) > 0.5:
			#print "Prediction: "+str(int(prediction)+1)
			#return int(prediction)+1
	#else:
		#print "Prediction: "+str(int(prediction))
		#return int(prediction)

if __name__ == '__main__':
	print "Loading pearson similarity matrix, please wait"
	pearsonMatrix = genfromtxt('pearsonMatrix.csv', delimiter=',')
	print "Pearson matrix loaded."
	dataToRate = genfromtxt('ToRate.csv', delimiter=',')
	dataToRate = numpy.delete(dataToRate, (0), axis=0)
	datafile = open('rating.csv','wb')
	wr = csv.writer(datafile,quoting=csv.QUOTE_MINIMAL, delimiter=',')
	
	dataToRank = genfromtxt('ToRank.csv', delimiter=',')
	dataToRank = numpy.delete(dataToRank, (0), axis=0)

	dataRankFile = open('ranking.json','wb')
	wr2 = csv.writer(dataRankFile,quoting=csv.QUOTE_MINIMAL, delimiter=',')
	wr.writerow(["itemID","styleID","userID","Rating"])

	w = 0
	counter = 1.
	totalObjects = len(dataToRate)
	for row in dataToRate:
			currentUser = str(int(row[2]))
			currentItem = str(int(row[0]))
			currentStyle = str(int(row[1]))
			progress = round ((counter * 100)/totalObjects,3)
			print "Calculating prediction file with User Based CF, Progress: "+str(progress) + "%"
			try:
				prediction = ubcf(userMap[currentUser],itemMap[currentItem])
				wr.writerow([w,currentItem,currentStyle,currentUser,str(prediction)])
			except:
				print " Unable to predict for user: "+currentUser+" and item: "+currentItem + ", assigining default 0"
				wr.writerow([w,currentItem,currentStyle,currentUser,str(0)])
			w = w+1			
			counter = counter + 1

	########## Generate top ten list ####################
	##### this part takes 27 hours! #######
	#i = 0
	#ubcfFullUserRatings = userRatings
	#counter = 1.
	#totalObjects = rows*columns
	
	#for user in userRatings:
		#j = 0
		#for rating in user:
			##print "Current Rating: "+str(rating)
			#if rating == 0.0:
				#ubcfFullUserRatings[i,j] = ubcf(i,j)
			#progress = round ((counter * 100)/totalObjects,3)
			#print "i: "+str(i)+", j: "+str(j)
			#print "Generating ubcfFullUserRatings, Progress: "+str(progress) + "%"
			#counter = counter + 1	
			#j = j+1
		#i = i+1
	#print "Saving ubcdFullUserRatings.csv"
	#numpy.savetxt("ubcfFullUserRatings.csv", ubcfFullUserRatings, delimiter=',')
	#print "ubcfFullUserRatings.csv saved"


ubcfFullUserRatings = genfromtxt('ubcfFullUserRatings.csv', delimiter=',')


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
		currentRow = ubcfFullUserRatings[userMap[str(int(user))]]
		sortedItemIndex = [ i for (i,j) in sorted(enumerate(currentRow), key=operator.itemgetter(1),reverse=True)]
		topTenIndex = sortedItemIndex[0:10]
		print "TopTen Indexes:" + str(topTenIndex)
		strTopTen = []
		for topItem in topTenIndex:
			print "Rating: "+str(ubcfFullUserRatings[userMap[str(int(user))],topItem])
			strTopTen.append(str(itemAntiMap[topItem]))
		wr2.writerow([str(int(user))+'": '+str(strTopTen)])
		print "TopTen List: "+str(strTopTen)
		result = cur.fetchone()

wr2.writerow(["}"])
datafile.close()
dataRankFile.close()
subprocess.gc.collect()

subprocess.call(['sed','-i.bak','s/\'/"/g','ranking.json'])
subprocess.call(['sed','-i.bak','s/""/"/g','ranking.json'])
subprocess.call(['sed','-i.bak','s/]"/],/g','ranking.json'])

