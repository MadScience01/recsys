from loadData import *
import itertools
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab
import numpy as np
import operator

cur.execute('SELECT count(*) from t;')    
numRows = cur.fetchone()
print "Number of rows in dataset: %s" % numRows    
cur.execute('SELECT count(distinct(userId)) from t;')
numUsers = cur.fetchone()
print "Number of users in dataset: %s" % numUsers
cur.execute('SELECT count(distinct(itemId)) from t;')
numItems = cur.fetchone()
print "Number of distinct Items in dataset: %s" % numItems
cur.execute('SELECT count(distinct(styleId)) from t;')
numStyles = cur.fetchone()
print "Number of distinct Styles in dataset: %s" % numStyles

cur.execute('SELECT avg(rating) from t;')
avgRating = cur.fetchone()
print "Average Rating in dataset: %s" % avgRating

stddev = np.std(zip(*data)[3])

print "Ratings standard deviation: " + str(stddev)

cur.execute('select count(rating) from t')
totalNumberOfRatings =  cur.fetchall()[0][0]
sparsity = 1. - (totalNumberOfRatings / float((rows*columns)))

print "Sparsity: "+str(sparsity)

cur.execute('select itemID, count(rating) from t group by itemID order by count(itemID) DESC LIMIT 20;')
topRatedItems = cur.fetchall()
items = [row[0] for row in topRatedItems]
numberOfRatings = [row[1] for row in topRatedItems]

width = 1.0
fig, ax = plt.subplots()
ax.set_xlabel('itemID')
ax.set_ylabel('Number of Ratings')
plt.title('Top 20 Most Rated Items')
ind = np.arange(len(topRatedItems))
p1 = ax.bar(ind, numberOfRatings,   width, color='r')

ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()
plt.xticks(ind+width/6., items, size=6, rotation=80)

pylab.savefig('mostRatedItems-top20.png',bbox_inches=0)

cur.execute('select itemID, max(cast(rating as int)), count(itemID) from t group by itemID order by 2 DESC,3 DESC LIMIT 50;')
topRatedItems = cur.fetchall()
print topRatedItems

items = [row[0] for row in topRatedItems]
bestRatings = [round(float(row[1])) for row in topRatedItems]

width = 1.0
fig, ax = plt.subplots()
ax.set_xlabel('itemID')
ax.set_ylabel('Rating')
plt.title('Top 50 Best Rated Items')
ind = np.arange(len(topRatedItems))
p1 = ax.bar(ind, bestRatings,   width, color='r')

ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()
plt.xticks(ind+width/6., items, size=6, rotation=80)

pylab.savefig('bestRatedItems-top50.png',bbox_inches=0)




numberOfRatings = np.array(numberOfRatings)
print "Average number of ratings per item: " + str(np.average(numberOfRatings))


cur.execute('SELECT userID, count(userID) FROM t GROUP BY userID ORDER BY count(userID) DESC LIMIT 20;')
topRatingUsers = cur.fetchall()

users = [row[0] for row in topRatingUsers]
numberOfRatings = [row[1] for row in topRatingUsers]

width = 1.0
fig, ax = plt.subplots()
ax.set_xlabel('userID')
ax.set_ylabel('Number of Ratings')
plt.title('Number of Ratings per User (Top 20)')
ind = np.arange(len(topRatingUsers))
p1 = ax.bar(ind, numberOfRatings,   width, color='r')

ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()
plt.xticks(ind+width/6., users, size=6, rotation=80)
#plt.legend( (p1[0]), ('Number of Ratings',) )
#plt.draw()

pylab.savefig('numberOfRatingsPerUser-top20.png',bbox_inches=0)

numberOfRatings = np.array(numberOfRatings)
print "Average number of ratings per user: " + str(np.average(numberOfRatings))

cur.execute('SELECT styleID, count(styleID) FROM t GROUP BY styleID ORDER BY count(styleID) DESC LIMIT 20;')
numberOfRatingsPerStyle = cur.fetchall()

styles = [row[0] for row in numberOfRatingsPerStyle]
ratingsPerStyle = [row[1] for row in numberOfRatingsPerStyle]

width = 1.0
fig, ax = plt.subplots()
ax.set_xlabel('styleID')
ax.set_ylabel('Number of Ratings')
plt.title('Number of Ratings per Style (Top 20)')
ind = np.arange(len(numberOfRatingsPerStyle))
p1 = ax.bar(ind, ratingsPerStyle,   width, color='r')

ax.autoscale_view()
ax.grid(True)
fig.autofmt_xdate()
plt.xticks(ind+width/6., users, size=6, rotation=80)

pylab.savefig('numberOfRatingsPerStyle-top20.png',bbox_inches=0)

##########################  Ranking by Wilson Scores ###################################
dataToRank = genfromtxt('ToRank.csv', delimiter=',')
dataToRank = numpy.delete(dataToRank, (0), axis=0)

dataRankFile = open('wilsonranking.json','wb')
wr2 = csv.writer(dataRankFile,quoting=csv.QUOTE_MINIMAL, delimiter=',')
wr2.writerow(["{"])

cur.execute('''select itemID,
sum(case when rating >= '2.5' then 1 else 0 END) as positive_ratings, 
sum(case when rating < '2.5' then 1 else 0 END) as negative_ratings 
from t 
group by itemID;''')
wilsonScores = []
for row in cur.fetchall():
	itemID = row[0]
	positive = float(row[1])
	negative = float(row[2])
	score = ((positive + 1.9208) / (positive + negative) - 1.96 * math.sqrt((positive * negative) / (positive + negative) + 0.9604) / (positive + negative)) / (1 + 3.8416 / (positive + negative))
	#print "Item: "+str(itemID)+", Score: "+str(score)
	wilsonScores.append((itemID,score))
	
wilsonScores = np.array(wilsonScores)
#topTenWilsonscores = [ (i,j) for (i,j,k) in sorted(enumerate(wilsonScores), key=operator.itemgetter(2),reverse=True)][0:10]
topTenWilsonscores = sorted(wilsonScores, key=lambda i: (float(i[1]), float(i[0])), reverse=True)[0:10]
print 	"Top Ten Wilson Scores:"
for row in topTenWilsonscores:
	print str(row[0]) + ","+str(row[1]) 

for user in dataToRank:
	wr2.writerow([str(int(user))+'": '+str([str(row[0]) for row in topTenWilsonscores])])
wr2.writerow(["}"])
dataRankFile.close()

subprocess.call(['sed','-i.bak','s/\'/"/g','wilsonranking.json'])
subprocess.call(['sed','-i.bak','s/""/"/g','wilsonranking.json'])
subprocess.call(['sed','-i.bak','s/]"/],/g','wilsonranking.json'])
