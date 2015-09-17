from loadData import *
import csv
import numpy
import scipy.spatial.distance as dst


####### Construct user similarity matrix, cosine based ########

#simUsers = numpy.zeros((rows,rows), dtype=numpy.float)

#print "Constructing cosine based user similarity matrix"
#totalObjects = rows*rows

#counter = 1.
#for i in range(1,rows):
        #for j in range(1,rows):
                #if i <> j:
                        #simUsers[i,j] = dst.cosine(userRatings[i-1,:], userRatings[j-1,:])
                #progress = round ((counter * 100)/totalObjects,3)
                #print "i: "+str(i)+", j: "+str(j)
                #print "Progress: "+str(progress) + "%"
                #counter = counter + 1

#print "Saving User cosineDistances matrix"
#numpy.savetxt("userCosineDistances.csv", simUsers, delimiter=',')
#print "User cosineDistances matrix saved."


###### Construct item similarity matrix, cosine based ########

simItems = numpy.zeros((columns,columns), dtype=numpy.float)
#print userRatings[:,i]

print "Constructing cosine based item similarity matrix"
totalObjects = columns*columns

counter = 1.
for i in range(1,columns):
        for j in range(1,columns):
			if i <> j:
				if simItems[i,j] == 0.0:
					### prepare item vectors
					cur.execute("select t1.rating,t2.rating from (select * from t where itemID ='"+str(itemAntiMap[i])+"') t1, (select * from t where itemID = '"+str(itemAntiMap[j])+"') t2 where t1.userID = t2.userID")
					commonItemRatings = cur.fetchall()
					ratingsA =  [float(row[0]) for row in commonItemRatings]
					ratingsB = [float(row[1]) for row in commonItemRatings]
					#print commonItemRatings
					#print "Ratings A: "+str(ratingsA)
					#print "Ratings B: "+str(ratingsB)
					if commonItemRatings <> []:
						simItems[i,j] = dst.cosine(ratingsA, ratingsB)
						#print simItems[i,j]
					#Item similarity is simmetric.
					simItems[j,i] = simItems[i,j]
			if i == j:
						simItems[i,j] = 1.0
			progress = round ((counter * 100)/totalObjects,3)
			print "i: "+str(i)+", j: "+str(j)
			print "Progress: "+str(progress) + "%"
			counter = counter + 1

print "Saving Item cosineDistances matrix"
numpy.savetxt("itemCosineDistances.csv", simItems, delimiter=',')
print "Item cosineDistances matrix saved."



