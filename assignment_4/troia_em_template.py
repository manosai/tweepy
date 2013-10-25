#!/bin/python

import sys
import csv
import json
import urllib2
from label_map import mturk_labels
import numpy as np
import matplotlib.pyplot as plt

class EMGrader():
	"""
	Implements EM quality estimation using Troia server. 
	estimate_data_labels returns the MLE estimates for the labels on each tweet
	estimate_worker_qualities returns the EM quality score of each worker
	"""	
	#initialize a job to run on troia server
	def __init__(self, csv_path, num_iter=10):
		self.csv_path = csv_path
		self.num_iter = num_iter
		self.base_url = "http://project-troia.com/api"
		self.initial_data = self.get_initial_data()
		self.worker_data, self.gold_data = self.get_tweet_data_from_csv()

		url = '%s/jobs'%self.base_url
		data = json.dumps(self.initial_data)
		req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
		result = json.loads(urllib2.urlopen(req).read())
	
		#A bit of hacky parsing to recover the job id. Why don't they just have the job id 
		#as its own field? Well, because that would be intuitive and practical.
		self.job_id = result['result'].split(':')[1].strip()
	
		#Send the labels to project troia
		url = '%s/jobs/%s/assigns'%(self.base_url,self.job_id)
		data = json.dumps(self.worker_data)
		req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
		result = json.loads(urllib2.urlopen(req).read())

		#uncomment to seed algorithm with gold data	
		#Send the gold labels to project troia
		url = '%s/jobs/%s/goldObjects'%(self.base_url,self.job_id)
		data = json.dumps(self.gold_data)
		req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
		result = json.loads(urllib2.urlopen(req).read())

		self.compute()

	#Formats csv data from MTurk into the format Troia wants for worker and gold data
	#Troia expects data formatted as a list of dictionary objects containing worker names and data labels
	#i.e. [ { "worker":"worker1", "object":"tweet text", "label":"positive" }, ...] 
	#and [ { "goldLabel": "positive", "name": "tweet text" } ]
	def get_tweet_data_from_csv(self):
		worker_data = list()
		gold_data = list()
		for hit in csv.DictReader(open(self.csv_path, 'rU')):
			gold = hit['Input.control']
			#as an id to uniquely identify a tweet, we will use the HIT id plus the tweet number
			gold_data.append({'name' : '%s-%s'%(hit['HITId'],gold), 'goldLabel' : mturk_labels[hit['Input.label']]})
			for i in range(0,10): 
				label = mturk_labels[hit['Answer.item%d'%i]]
				if not(label == 'NA') : 
					inst = {'worker':hit['WorkerId'], 'object':'%s-%d'%(hit['HITId'],i), 'label':label}
					worker_data.append(inst)
		return worker_data, gold_data
	
	#Data which tells Troia how to set up the run
	def get_initial_data(self):
		categories = ["positive", "negative", "neutral"]

		priors = [{"categoryName": "positive", "value": 0.33}, \
			 {"categoryName": "negative", "value": 0.33}, \
			 {"categoryName": "neutral", "value": 0.34}]

		costs = [{"from": "positive", "to": "negative", "value": 1.0}, \
			{"from": "positive", "to": "positive", "value": 0.0}, \
			{"from": "positive", "to": "neutral", "value": 1.0}, \
			{"from": "negative", "to": "negative", "value": 0.0}, \
			{"from": "negative", "to": "positive", "value": 1.0}, \
			{"from": "negative", "to": "neutral", "value": 1.0}, \
			{"from": "neutral", "to": "negative", "value": 1.0}, \
			{"from": "neutral", "to": "positive", "value": 1.0}, \
			{"from": "neutral", "to": "neutral", "value": 0.0}] #, \

		return { "categories": categories, \
			"algorithm": "BDS", \
			"iterations": self.num_iter, \
			"epsilon": 0.0001, \
			"scheduler": "NormalScheduler", \
			"prioritycalculator": "CostBased"}

	#Begin the EM computation
	def compute(self):
		url = '%s/jobs/%s/compute'%(self.base_url,self.job_id)
		req = urllib2.Request(url, '{}', {'Content-Type': 'application/json'})
		result = json.loads(urllib2.urlopen(req).read())
	
		#More hacky parsing to recover the response id. 
		response_id = result['redirect'].split('/')[1].strip()
		
		#Wait for job to finish
		complete = False
		while(not(complete)):
			url = '%s/responses/%s/POST/jobs/%s/compute'%(self.base_url,response_id,self.job_id)
			req = urllib2.Request(url)
			result = json.loads(urllib2.urlopen(req).read())
			print 'Checking job status...%s'%result['status']
			complete = (result['status'] == 'OK')
	
	#Get the label estimates for data
	def estimate_data_labels(self):
		url = '%s/jobs/%s/objects/prediction'%(self.base_url,self.job_id)
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
	
		url = '%s/%s'%(self.base_url,result['redirect'])
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
		return {w['objectName'] : w['categoryName'] for w in result['result']}
	
	#Get the quality estimates for workers
	def estimate_troia_worker_qualities(self):
		url = '%s/jobs/%s/workers/quality/estimated'%(self.base_url,self.job_id)
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
	
		url = '%s/%s'%(self.base_url,result['redirect'])
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
		return {w['workerName'] : w['value'] for w in result['result']}

	#Get the confusion matrices for workers
	def confusion_matrix(self):
		url = '%s/jobs/%s/workers/quality/matrix'%(self.base_url,self.job_id)
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
	
		url = '%s/%s'%(self.base_url,result['redirect'])
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
		return {w['workerName'] : w['value'] for w in result['result']}

	#Get the confusion matricies for workers
	def estimate_worker_qualities(self):
		url = '%s/jobs/%s/workers/quality/matrix'%(self.base_url,self.job_id)
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
	
		url = '%s/%s'%(self.base_url,result['redirect'])
		req = urllib2.Request(url)
		result = json.loads(urllib2.urlopen(req).read())
		return {w['workerName'] : self.accuracy(w['value']) for w in result['result']}

	def accuracy(self, matrix):
		#TODO Return the Turker's accuracy (the sum of the values on the diagonal of the confusion matrix
		#HINT : its a good idea to normalize by the sum of all the entries in the matrix, so that the error rate is between 0 and 1
		a = matrix
		norm = np.sum(a)
		rows, cols = a.shape
		for i in range(rows):
			for j in range(cols):
				a[i][j] = a[i][j] / norm
		return np.trace(a)