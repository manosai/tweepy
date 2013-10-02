#!/bin/python
"""
This code grades the HITs based on the embedded control tweets. 
It takes as input the csv file containing the submitted HITs.
It outputs hits_graded.csv, which contains the columns 'Approve' and 'Reject', one of which contains an 'X' for each HIT, according to the Turker's performance on controls.
"""
import sys
import csv 
import random

#DictReader returns an iterator object, so we can only iterate through the list once
#We use python's list-compression sytax to save the instances into a list that we can interate repeatedly
hit_data = [d for d in csv.DictReader(open(sys.argv[1], 'rU'))]

csvwriter = csv.writer(open('hits_graded_naive.csv','w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

#Get the headers from the input file. We will use the same headers in the output file. 
headers = hit_data[0].keys()
csvwriter.writerow(headers)

#You may have used slightly different labelings when you annotated the gold standard tweets and when you recorded the Turkers' answers. You will need to map all the answers into a common notation so you can compare. For example, if you used 0=positive, 1=negative, 2=neutral in the HIT, fill that in here. If you used the same labeling in both cases, then these data structures will be unnecessary. That's okay, just fill them in anyway.

#I think most of you (I know this is true for myself) annotated the gold standard tweets in the first assignment using a three-point scale (positive, neutral, negative) but then asked Turkers to use a five-point scale (strongly positive, positive, neutral, negative, strongly negative). That is okay, we will map your labels to a list of acceptable answers. So if you called a tweet 'positive', you might accept a turker's response if they say either 'positive' or 'strongly positive'. You can also be very lenient and accept +/- one degree in either direction. That is your call.
gold_labels = {
		'positive' : ['strongly positive', 'positive'], 
		'neutral' : ['neutral'], 
		'negative' : ['negative', 'strongly negative']
}

mturk_labels = {
		'Choice5' : 'strongly positive', 
		'Choice4' : 'positive', 
		'Choice3' : 'neutral', 
		'Choice2' : 'negative',
		'Choice1' : 'strongly negative',
		'Choice6' : 'NA',
		'' : 'NO ANSWER GIVEN' #your turker was a lazy $%&*!. Blank answers will get treated as wrong.
}

#Grade each HIT
#Remember, here 'hit' is a dictionary data structure corresponding to one row of your input CSV. It maps the CSV headers to the corresponding values for each row.
for hit in hit_data:
	# get the correct answer for the control from this row of the CSV 
	correct_control_answer = hit['Input.label']
	# get the Turker's answer for the control tweet 
	index = hit['Input.control']
	key = 'Answer.Q' + str(index)
	turker_control_answer = hit[key]
	if mturk_labels[turker_control_answer] in gold_labels[correct_control_answer]:
		print 'Turker answered %s. Expected %s. Approving.' %(turker_control_answer, correct_control_answer)
		# approve the worker by marking the appropriate column in the CSV with an 'X'
		hit['Approve'] = 'X'
	else : 
		print 'Turker answered %s. Expected %s. Rejecting.' %(turker_control_answer, correct_control_answer)
		# reject the worker by marking the appropriate column in the CSV with an 'X'
		hit['Reject'] = 'X'
	csvwriter.writerow([hit[column] for column in headers])

