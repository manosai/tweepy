#!/bin/python

import csv
from label_map import gold_labels, mturk_labels

class ControlsGrader():
	"""
	Implements embedded control quality estimation.
	estimate_data_labels returns a set of approved labels for each tweet, where the label is approved if it was provided by a worker who correctly labeled the control tweet
	estimate_worker_qualities returns, for each worker, the proportion of control tweets that were correctly labeled
	"""	

	#Initialize grader with path to graded HITs csv
	def __init__(self, csv_path):
		self.csv_path = csv_path

	#Compile dictionary {tweet : set of approved labels}
	def get_tweet_data_from_csv(self):
		tweet_data = dict()
		for hit in csv.DictReader(open(self.csv_path, 'rU')):
			for i in range(0,10): 
				tweetId = '%s-%d'%(hit['HITId'],i)
				if tweetId not in tweet_data : tweet_data[tweetId] = set()
        			correct_control_answer = hit['Input.label']
        			turker_control_answer = hit['Answer.item%s'%hit['Input.control']]
        			if mturk_labels[turker_control_answer] in gold_labels[correct_control_answer]:
					label = hit['Answer.item%d'%i]
					tweet_data[tweetId].add(label)
		return tweet_data 
	
	#Compile dictionary of {worker : {tweet : was_approved}}
	def get_worker_data_from_csv(self):
		worker_data = dict()
		for hit in csv.DictReader(open(self.csv_path, 'rU')):
			worker = hit['WorkerId']
			if worker not in worker_data : worker_data[worker] = {'approved' : 0, 'total' : 0}
			for i in range(0,10): 
        			correct_control_answer = hit['Input.label']
        			turker_control_answer = hit['Answer.item%s'%hit['Input.control']]
        			if mturk_labels[turker_control_answer] in gold_labels[correct_control_answer]:
					worker_data[worker]['approved'] += 1
				worker_data[worker]['total'] += 1
		return worker_data 
	
	#Return a dictionary of {tweet : most popular label}	
	def estimate_data_labels(self):
		tweet_data = self.get_tweet_data_from_csv()
		label_estimates = list()
		for tweet in tweet_data:
			estimate = tweet_data[tweet]
			label_estimates.append({'objectName':tweet, 'categoryName':estimate})
		return {w['objectName'] : w['categoryName'] for w in label_estimates}
	
	#Return a dictionary of {worker : average worker accuracy}	
	def estimate_worker_qualities(self):
		worker_data = self.get_worker_data_from_csv()
		worker_estimates = list()
		for worker in worker_data:
			accuracy = float(worker_data[worker]['approved']) / worker_data[worker]['total']
			worker_estimates.append({'workerName':worker, 'value':accuracy})
		return {w['workerName'] : w['value'] for w in worker_estimates}
