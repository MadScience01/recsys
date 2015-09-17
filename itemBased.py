from loadData import *
import csv

import operator

def itemBasedPred(userIndex,itemIndex):
	
	####  K Nearest Items
	k = 20
	
	fullneighborhood = itemCosineDistances[itemIndex]
	k_neighborItems = [ i for (i,j) in sorted(enumerate(fullneighborhood), key=operator.itemgetter(1),reverse=True)][0:k]
	
	print "Current User: " + str(userAntiMap[userIndex]) + " Current Item: "+str(itemAntiMap[itemIndex])
	print "K-Neighbor Items: "+str(k_neighborItems)
	partialSum = 0.
	for neighborItemIndex in k_neighborItems:
		partialSum = partialSum + itemCosineDistances[itemIndex,neighborItemIndex]*userRatings[userIndex,neighborItemIndex]
	numerator = partialSum
	
	partialSum = 0.
	for neighborItemIndex in k_neighborItems:
		partialSum = partialSum + itemCosineDistances[itemIndex,neighborItemIndex]
	denominator = partialSum

	if denominator <> 0.:
		prod = numerator / denominator
	else:
		prod = userRatingAverages[userAntiMap[userIndex]]
		
		
	return prod
	
if __name__ == '__main__':
	print "Loading item Cosine similarity matrix, please wait"
	itemCosineDistances = genfromtxt('itemCosineDistances.csv.bak', delimiter=',')
	print "item Cosine matrix loaded."
	dataToRate = genfromtxt('ToRate.csv', delimiter=',')
	dataToRate = numpy.delete(dataToRate, (0), axis=0)
	dataToRank = genfromtxt('ToRank.csv', delimiter=',')
	dataToRank = numpy.delete(dataToRank, (0), axis=0)
	
	datafile = open('itemBasedRating.csv','wb')
	wr = csv.writer(datafile,quoting=csv.QUOTE_MINIMAL, delimiter=',')
	dataRankFile = open('itemBasedRanking.json','wb')
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
			print "Calculating prediction file with Item Based CF, Progress: "+str(progress) + "%"
			try:
				prediction = itemBasedPred(userMap[currentUser],itemMap[currentItem])
				wr.writerow([w,currentItem,currentStyle,currentUser,str(prediction)])
			except:
				print " Unable to predict for user: "+currentUser+" and item: "+currentItem + ", assigining user average rating: "+str(userRatingAverages[currentUser])
				wr.writerow([w,currentItem,currentStyle,currentUser,str(userRatingAverages[currentUser])])
			w = w+1			
			counter = counter + 1

wr2.writerow(["{"])
for user in dataToRank:
	#For each user, tell me which one was his best rated item, and give me a top ten based on that item.
	cur.execute('select itemID, cast(rating as float) from t  where userID = \''+str(int(user))+'\' order by 2 desc limit 1')
	result = cur.fetchone()
	#print "result: "+str(result)
	if result == None:
		print 'select itemID, cast(rating as float) from t  where userID = \''+str(int(user))+'\' order by 2 desc limit 1'
	while result <> None:	
		print "SQL Result: "+str(result)
		print "User: "+str(int(user))+" Best Item: "+str(result[0])
		bestItemIndex = itemMap[str(int(result[0]))]
		print "Best Item Index: "+str(bestItemIndex)
		currentRow = itemCosineDistances[bestItemIndex]
		sortedItemIndex = [ i for (i,j) in sorted(enumerate(currentRow), key=operator.itemgetter(1),reverse=True)]
		topTenIndex = sortedItemIndex[0:10]
		print "TopTen Indexes:" + str(topTenIndex)
		strTopTen = []
		for topItem in topTenIndex:
			#print "Rating: "+str(ubcfFullUserRatings[userMap[str(int(user))],topItem])
			strTopTen.append(str(itemAntiMap[topItem]))
		wr2.writerow([str(int(user))+'": '+str(strTopTen)])
		print "TopTen List: "+str(strTopTen)
		result = cur.fetchone()

wr2.writerow(["}"])
datafile.close()
dataRankFile.close()
subprocess.gc.collect()

subprocess.call(['sed','-i.bak','s/\'/"/g','itemBasedRanking.json'])
subprocess.call(['sed','-i.bak','s/""/"/g','itemBasedRanking.json'])
subprocess.call(['sed','-i.bak','s/]"/],/g','itemBasedRanking.json'])
