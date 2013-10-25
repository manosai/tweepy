#!/bin/python

import csv
import operator
import numpy as np
import matplotlib.pyplot as plt

#Read the data from the csvs that were output by quality_estimation.py
tweet_data = [row for row in csv.DictReader(open('data_quality_estimates.csv'))]
worker_data = [row for row in csv.DictReader(open('worker_quality_estimates.csv'))]


#Question 1 : What was your accuracy a) against the majority vote? b) against the controls? c) against the EM estimated labels? 
#Hint: (b) corresponds exactly to the percentage of HITs you approved, since you approved HITs if and only if the control was correct
correct = {'majority' : 0 , 'controls' : 0 , 'em' : [0,0,0,0,0,0,0,0,0,0]}
total = 0
for row in tweet_data:
	for i in [1, 2, 3]:
		total += 1
		turker, turker_label, approved = row['worker%d'%i].split(':')
		#HINT : look at data_quality_estimates.csv to see what your data looks like, and what the fields in tweet_data are
		#TODO check if worker's label is correct according to the majority vote rule, and increment correct['majority'] if so
		#TODO check if worker's label is correct according to the embedded controls rule, and increment correct['controls'] if so
		#TODO check if worker's label is correct according to the em maximum liklihood labels at each iteration, and increment correct['em'] 

#Question 1 : How does each algorithm rate your data's quality? How does EM's estimate change as you iterate?
#We will answer this question by looking at a graph of data quality. Because I really really like graphs.
plt.axhline(float(correct['majority'])/total, color='r')
plt.annotate("Majority Vote", (7,float(correct['majority'])/total), color='r')
plt.axhline(float(correct['controls'])/total, color='b')
plt.annotate("Embedded Controls", (7,float(correct['controls'])/total), color='b')
plt.plot([float(correct['em'][i])/total for i in range(0,10)], color='k')

plt.savefig('data_quality.png')
plt.clf()

#Question 2 : How does each algorithm rank your workers? Do they agree on which workers are most/least trustworthy? 
#We will answer this question by looking at a graph of worker qualities. Because...graphs.
workers = {'majority' : [] , 'controls' : [] , 'em' : []}
for row in worker_data:
	workers['majority'].append(float(row['majority_vote']))
	workers['controls'].append(float(row['embedded_control']))
	workers['em'].append(float(row['troia_em']))

#Sort the workers by decreasing quality, according to majority vote
data = zip(workers['majority'], workers['controls'], workers['em'])
data = sorted(data, key=operator.itemgetter(0), reverse=True)

plt.scatter([d[0] for d in data], [d[2] for d in data], marker='.', color='k')

for d in data: 
	if d[1] < 0.2 : c = 'r'
	elif d[1] < 0.8 : c = 'y'
	else : c = 'g'
	plt.annotate('%.02f'%d[1], (d[0],d[2]), xycoords='data', textcoords='data', size='small', color=c)

plt.title("Worker performance on controls")
plt.xlabel("Majority Vote")
plt.ylabel("EM")
plt.savefig('worker_quality.png')

