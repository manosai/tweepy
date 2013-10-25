#!/bin/python

import csv
import operator
from label_map import mturk_labels

class MajorityVoteGrader():
	"""
	Implements majority vote quality estimation.
	estimate_data_labels returns the most popular label for each tweet 
	estimate_worker_qualities returns, for each worker, the proportion of labels which matched the majority label
	"""	

	#Initialize grader with path to graded HITs csv
	def __init__(self, csv_path):
		self.csv_path = csv_path

	#Compile dictionary {tweet : {number of votes for each label}}
	def get_tweet_data_from_csv(self):
		tweet_data = dict()
		for hit in csv.DictReader(open(self.csv_path, 'rU')):
			for i in range(0,10): 
				tweetId = '%s-%d'%(hit['HITId'],i)
				if tweetId not in tweet_data : tweet_data[tweetId] = {'positive':0,'negative':0,'neutral':0}
				label = mturk_labels[hit['Answer.item%d'%i]]
				if not(label == 'NA') : tweet_data[tweetId][label] += 1
		return tweet_data 
	
	#Compile dictionary of {worker : {tweet : worker's label}}
	def get_worker_data_from_csv(self):
		worker_data = dict()
		for hit in csv.DictReader(open(self.csv_path, 'rU')):
			worker = hit['WorkerId']
			if worker not in worker_data : worker_data[worker] = {}
			for i in range(0,10): 
				tweetId = '%s-%d'%(hit['HITId'],i)
				label = mturk_labels[hit['Answer.item%d'%i]]
				if not(label == 'NA') : worker_data[worker][tweetId] = label 
		return worker_data 

	#Return a dictionary of {tweet : most popular label}	
	def estimate_data_labels(self):
		tweet_data = self.get_tweet_data_from_csv()
		label_estimates = list()
		for tweet in tweet_data:
			#get the most popular label for this tweet and store its value in the variable 'estimate'
			#See the method get_tweet_data_from_csv() to see what the variable 'tweet' contains
			positive_count = tweet_data[tweet]['positive']
			negative_count = tweet_data[tweet]['negative']
			neutral_count = tweet_data[tweet]['neutral']
			counts = [positive_count, negative_count, neutral_count]
			estimate = max(counts)
			label_estimates.append({'objectName':tweet, 'categoryName':estimate})
		return {w['objectName'] : w['categoryName'] for w in label_estimates}

	#Return a dictionary of {worker : average worker accuracy}		
	def estimate_worker_qualities(self):
		majority_labels = self.estimate_data_labels()
		worker_data = self.get_worker_data_from_csv()
		worker_estimates = list()
		for worker in worker_data:
			#TODO compute the proportion of this worker's labels which match the majority label
			#and store it in the variable 'accuracy'
			#You should look at the methods estimate_data_labels() and get_worker_data_from_csv()
			worker_tweets = worker_data[worker]
			correct = 0 
			# keep track of all the correctly labeled tweets 
			for tweet in worker_tweets:
				if worker_tweets[tweet] == majority_labels[tweet] : correct += 1
			accuracy = correct / len(worker_tweets)
			worker_estimates.append({'workerName':worker, 'value':accuracy})
		return {w['workerName'] : w['value'] for w in worker_estimates}
