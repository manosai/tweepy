#!/bin/python

from majority_vote import MajorityVoteGrader
from embedded_controls import ControlsGrader
from troia_em import EMGrader
import csv
import sys
from label_map import gold_labels, mturk_labels

CSV_PATH = sys.argv[1]

def map_tweet_id_to_tweet():
	tweet_map = dict()
	for hit in csv.DictReader(open(CSV_PATH, 'rU')):
		for i in range(0,10): 
			tweet_map['%s-%d'%(hit['HITId'],i)] = hit['Input.tweet%d'%i]
	return tweet_map

def map_tweet_id_to_workers():
	tweet_map = dict()
	for hit in csv.DictReader(open(CSV_PATH, 'rU')):
		for i in range(0,10): 
			tweet_id = '%s-%d'%(hit['HITId'],i)
        		correct_control_answer = hit['Input.label']
        		turker_control_answer = hit['Answer.item%s'%hit['Input.control']]
			if tweet_id not in tweet_map : tweet_map[tweet_id] = dict()
        		if mturk_labels[turker_control_answer] in gold_labels[correct_control_answer]:
				tweet_map[tweet_id][hit['WorkerId']] = (hit['Answer.item%d'%i], 'Approved')
			else: tweet_map[tweet_id][hit['WorkerId']] = (hit['Answer.item%d'%i], 'Rejected')
	return tweet_map
	
mv_grader = MajorityVoteGrader(CSV_PATH)
ec_grader = ControlsGrader(CSV_PATH)
em_grader = EMGrader(CSV_PATH)

#aggregate worker estimates from each grader
mv_worker_estimates = mv_grader.estimate_worker_qualities()	
ec_worker_estimates = ec_grader.estimate_worker_qualities()	
em_worker_estimates = em_grader.estimate_worker_qualities()	

csvwriter = csv.writer(open('worker_quality_estimates.csv','w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
csvwriter.writerow(['workerId', 'majority_vote', 'embedded_control', 'troia_em'])
for worker in mv_worker_estimates:
	csvwriter.writerow([worker, mv_worker_estimates[worker], ec_worker_estimates[worker], em_worker_estimates[worker]])

#aggregate worker estimates from each grader
mv_label_estimates = mv_grader.estimate_data_labels()	
ec_label_estimates = ec_grader.estimate_data_labels()	
em_label_estimates = []
for i in range(1,11):
	em_grader = EMGrader(CSV_PATH, num_iter=i)
	em_label_estimates.append(em_grader.estimate_data_labels())	

tweet_map = map_tweet_id_to_tweet()
worker_map = map_tweet_id_to_workers()

csvwriter = csv.writer(open('data_quality_estimates.csv','w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
headers = ['tweetId', 'tweet', 'majority_vote', 'embedded_control'] + ['troia_em_iter%d'%i for i in range(1,11)] + ['worker1', 'worker2', 'worker3']
csvwriter.writerow(headers)
for label in mv_label_estimates:
	row = [label, tweet_map[label], mv_label_estimates[label], ':'.join(list(ec_label_estimates[label]))] 
	for le in em_label_estimates:
		try : row.append(le[label])
		except KeyError: row.append('NA')
	row += ['%s:%s:%s'%(worker, worker_map[label][worker][0], worker_map[label][worker][1]) for worker in worker_map[label]]
	csvwriter.writerow(row)


