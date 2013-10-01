#!/bin/python

import csv

naive_grades = [line for line in csv.DictReader(open('hits_graded_naive.csv', 'rU'))]
smart_grades = [line for line in csv.DictReader(open('hits_graded_moresmarter.csv', 'rU'))]

app_naive = len([line for line in naive_grades if line['Approve'] == 'X'])
rej_naive = len([line for line in naive_grades if line['Reject'] == 'X'])
app_smart = len([line for line in smart_grades if line['Approve'] == 'X'])
rej_smart = len([line for line in smart_grades if line['Reject'] == 'X'])

print '\t\tnaive\tsmart'
print 'Approved\t%d\t%d'%(app_naive, app_smart)
print 'Rejected\t%d\t%d'%(rej_naive, rej_smart)
