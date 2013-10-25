#!/bin/python

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
		'Choice1' : 'negative',
		'Choice6' : 'NA',
		'' : 'NO ANSWER GIVEN' #your turker was a lazy $%&*!. Blank answers will get treated as wrong.
}
