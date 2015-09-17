from loadData import *
from math import sqrt
from scipy.stats.mstats import pearsonr
import numpy as np

#a,b users
#rating_a_p rating of user a over item p
#P set of items rated by both A and B

#def pearsonCorrelation(userA,userB):	
	#avgRatingA = float(userRatingAverages[userA])
	#avgRatingB = float(userRatingAverages[userB])
	#cur.execute("select t1.rating,t2.rating from (select * from t where userID ='"+userA+"') t1, (select * from t where userID = '"+userB+"') t2 where t1.itemID = t2.itemID")
	#P = cur.fetchall()
	#if P == None:
		#return 0.
	
	#partialSum = 0.
	#for row in P:
		#ratingA = float(row[0])
		#ratingB = float(row[1])
		#partialSum = partialSum + (ratingA - avgRatingA)*(ratingB - avgRatingB)
	#numerator = partialSum
	#if numerator == 0.0:
		#return 0.
	#partialSum = 0.
	#for row in P:
                #ratingA = float(row[0])
                #partialSum = partialSum + (ratingA - avgRatingA)**2
	#den1 = sqrt(partialSum)
	#if den1 == 0.:
		#return 0.
	#partialSum = 0. 
	#for row in P:
                #ratingB = float(row[1])
                #partialSum = partialSum + (ratingB - avgRatingB)**2
	#den2 = sqrt(partialSum)
	#if den2 == 0:
		#return 0.
	#pearson = numerator / (den1*den2)
	#print "UserA : "+str(userA)+" UserB: "+str(userB)+" Pearson: "+str(pearson)
	#return pearson

if __name__ == '__main__':
	#create similarity matrix, start by creating the numpy structure
	pearsonMatrix = numpy.zeros((rows,rows) , dtype=numpy.float)
	counter = 1.
	totalrows = rows
	i = 0
	j = 0
	for userA in userList:
		for userB in userList:
			if userA <> userB:
				userARatings = userRatings[userMap[userA]]
				userBRatings = userRatings[userMap[userB]]
				#print userARatings.shape
				#print userBRatings.shape
				#pearsonMatrix[i,j] = pearsonCorrelation(userA,userB)
				if pearsonMatrix[i,j] == 0.:
					pearsonMatrix[i,j] = pearsonr(userARatings,userBRatings)[0]
					pearsonMatrix[j,i] = pearsonMatrix[i,j]
				j = j+1
		progress = round ((counter * 100)/totalrows,3)
                print "Progress: "+str(progress) + "%"
                counter = counter + 1	
		i = i+1
		j = 0.


print "Saving Pearson Similarity matrix, please wait"
numpy.savetxt("pearsonMatrix.csv", pearsonMatrix, delimiter=',')
print "Pearson matrix saved"
	

	  
