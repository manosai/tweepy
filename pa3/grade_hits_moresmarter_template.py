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

csvwriter = csv.writer(open('hits_graded_moresmarter.csv','w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

#Get the headers from the input file. We will use the same headers in the output file. 
headers = hit_data[0].keys()
csvwriter.writerow(headers)

#TODO: This is the same as in grade_hits_naive.py. I know code reuse is bad, but I like having these as two separate scripts so that it is easier for you to see what is happening. So, I am going to make you retype all of these. Sincere apologies.

gold_labels = {
		'YOUR POSITIVE LABEL' : ['strongly positive', 'positive'], 
		'YOUR NEUTRAL LABEL' : ['neutral'], 
		'YOUR NEGATIVE LABEL' : ['negative', 'strongly negative']
}

mturk_labels = {
		'YOUR STRONGLY POSITIVE LABEL' : 'strongly positive', 
		'YOUR POSITIVE LABEL' : 'positive', 
		'YOUR NEUTRAL LABEL' : 'neutral', 
		'YOUR NEGATIVE LABEL' : 'negative',
		'YOUR STRONGLY NEGATIVE LABEL' : 'strongly negative',
		'YOUR NOT RELEVANT LABEL' : 'NA',
		'' : 'NO ANSWER GIVEN' 
}

#We will use the protocol discussed in class for approving and rejecting Turkers, which looks at turkers overall accuracy on HITs over time, rather than looking at each HIT in isolation. As a recap, the protocol will be : 
# - if the total number of hits you have seen from this Turker is < 10, accept them (we'll call this PREAPPROVAL status)
# - if a Turker's average accuracy falls below REJECT_THRESHOLD, always reject (we'll call this BLOCKED status)
# - if a Turker's average accuracy rises above ACCEPT_THRESHOLD, always accept (we'll call this TRUSTED status)
# - otherwise, accept/reject proportionally to their accuracy. this corresponds to rejecting hits with incorrect controls and accepting those with correct controls. (we'll call this PENDING status)

# We will simulate this in a streaming manner, to make it more realistic. We will have to keep track of our workers cumulative accuracies each time we see a new label

worker_accuracies = {}
FREE_HITS = 5
REJECT_THRESHOLD = 0.2 #randomly guessing, 1 in 5
APPROVE_THRESHOLD = 0.8 #chosen arbitrarily, but seems pretty fair

#Grade each HIT
for hit in hit_data:
	
	#initialize a place in our dictionary to start tracking this worker
	worker = hit['WorkerId']
	if worker not in worker_accuracies : worker_accuracies[worker] = {'correct' : 0.0, 'total' : 0.0, 'status' : 'PREAPPROVE'}	

	correct_control_answer = #TODO get the correct answer for the control from this row of the CSV 
	turker_control_answer = #TODO get the Turker's answer for the control tweet 

	turker_correct = (mturk_labels[turker_control_answer] in gold_labels[correct_control_answer])
	
	#TODO Update the value at 'total' in worker_accuracies[worker] 
	#TODO Update the value at 'correct' in worker_accuracies[worker] based on the new information contained in this tweet

	#Update the worker's status based on the updated accuracies

	#Check if the worker has used up all his free hits. If yes, kick him out of preapproval status. 
	if (#TODO logic to see if free hits have been used up):
		worker_accuracies[worker]['status'] = 'PENDING' 
	if worker_accuracies[worker]['status'] == 'PENDING':
	#Check the worker's cumulative accuracy, and see if it requires a status update 
	#(and by that I mean facebook status update. "Hey guys. A2C1Z52F4B0CG1 just hit 60% accuracy!" These are the kinds of things I post...)
		acc = #TODO calculate accuracy of worker
		if acc < REJECT_THRESHOLD : #TODO update status
		elif acc > APPROVE_THRESHOLD : #TODO update status

	#Finally, approve or reject based on the worker's current status
	status = worker_accuracies[worker]['status']
	if status == 'PREAPPROVE' : 
		print 'Turker %s has only %d hits in database. Accepting.'%(worker, worker_accuracies[worker]['total'])
		hit['Approve'] = 'X'
	elif status == 'BLOCKED' : 
		print 'Turker %s has been blocked. Rejecting.'%worker
		hit['Reject'] = 'X'
	elif status == 'TRUSTED' : 
		print 'Turker %s is awesome! Hard worker, good listener, and all around standup guy. Accepting.'%worker
		hit['Approve'] = 'X'
	else : #status is PENDING
		print 'Turker %s pending at %.02f accuracy.'%(worker, acc)
		#TODO approve/reject based on the Turker's answer to this control (this is equivalent to the logic in grade_hits_naive.py

	csvwriter.writerow([hit[column] for column in headers])


