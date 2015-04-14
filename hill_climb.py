#!/usr/bin/env python
from __future__ import division
from nltk.corpus import stopwords
import optparse
import sys
import string
import math


optparser = optparse.OptionParser()
optparser.add_option("-d", "--data", dest="train", default="wikidata/es/", help="Data filename prefix (default=data)")
optparser.add_option("-e", "--english", dest="english", default="orig.enu.snt", help="Suffix of English filename")
optparser.add_option("-s", "--spanish", dest="spanish", default="orig.esn.snt", help="Suffix of French filename")
optparser.add_option("-o", "--output", dest="output", default="output", help="Prefix of filename to output to")
optparser.add_option("-r", "--dict", dest="esdict", default="./dict.es", help="Spanish to English Dictionary")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.01, type="float", help="Threshold (default=0.5)")
optparser.add_option("-p", "--PROPER_W", dest="PROPER_W", default=2.0, type="float", help="Proper Noun Weight (default=10.0)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
optparser.add_option("-w", "--windowsize", dest="win_size", default=5, type="int", help="Window size")
optparser.add_option("-l", "--stoplist", dest="stop_file", default="stopwords.txt", help="List of stop words")
(opts, _) = optparser.parse_args()
s_data = "%s%s" % (opts.train, opts.spanish)
e_data = "%s%s" % (opts.train, opts.english)
s_file_name = "%s%s" % (opts.output, ".es")
e_file_name = "%s%s" % (opts.output, ".en")

# load answer key for grading portion
answers_en = 'wikidata/es/pairs.enu.snt'
answers_es = 'wikidata/es/pairs.esn.snt'
answer_key = {}
answer_key = {e.strip(): s.strip() for (e,s) in zip(open(answers_en).readlines(), open(answers_es).readlines())}
f = open('pred.en', 'w')
for key in answer_key.keys():
	f.write(key + '\n')
f.close()
f = open('pred.es', 'w')
for val in answer_key.values():
	f.write(val + '\n')
f.close()

# create stopwords
stopwords = set([word.strip() for word in open(opts.stop_file)])
punct = string.punctuation
for p in punct:
    stopwords.add(p)
additions = ['-LRB-', '-RRB-', '\'\'', '``', '...']
for p in additions:
    stopwords.add(p)

#put each english sentence in file into a list
e_sents = [english.strip() for english in open(e_data) if len(english.strip()) > 0][:opts.num_sents]

#put each spanish sentence from file into a list
s_sents = [spanish.strip() for spanish in open(s_data) if len(spanish.strip()) > 0][:opts.num_sents]

es_lists = [line.strip().split() for line in open(opts.esdict)]

#make a dictionary from spanish word to list of english words
es_map = {}
for es_line in es_lists:
    es_map[es_line[0]] = es_line[1:]

## start hill climb
theta = [33,0.2,0.2] # w, t, p
dw = 32
dt = 0.1
dp = 0.1
dtheta = [[0,0,0],
          [-dw,0,0],
          [dw,0,0],
          [0,-dt,0],
          [0,dt,0],
          [0,0,-dp],
          [0,0,dp]]
num_samples = len(dtheta)
iteration = 0
max_iter = 5000

while iteration < max_iter:
	scores = [0.0 for i in xrange(0,num_samples)]
	for i,params in enumerate(dtheta):
		weights = [0,0,0]
		for j,p in enumerate(params):
			weights[j] = theta[j]+p
		e_output = []
		s_output = []

		PROPER_W = weights[2]

		for eindex, e in enumerate(e_sents):
			best_score = 0
			best_s = ""
			e_list = e.split()
			e_len = len(e_list)
			e_bit_vec = [0]*e_len
			start = max(0, eindex - int(weights[0]))
			end = min(len(s_sents), eindex + int(weights[0]))
			aligned = False
			for s in s_sents[start:end]:
				count_overlap = 0
				count_same = 0
				for s_word in s.split():
					translated = False
					if s_word.lower() in es_map:
						translations = es_map[s_word.lower()]
						for k, e_word in enumerate(e_list):
							if e_word.lower() in translations and not translated and e_bit_vec[k] == 0 and e_word not in stopwords:
								translated = True
								e_bit_vec[k] = 1
								count_overlap = count_overlap + 1
					else:
						for k, word in enumerate(e_list):
							if not e_bit_vec[k] and word == s_word and not translated and word not in stopwords:
								#sys.stderr.write(word + '   ' + s_word + '\n')
								count_same += 1
								translated = True
								e_bit_vec[k] = 1
				score = (count_overlap+PROPER_W*count_same) / e_len
				#append each sentence if above thresh
				if score > best_score:
					best_s = s
					best_score = score
			if best_score > weights[1]:
				e_output.append(e)
				s_output.append(best_s)

		########## grading
		preds = [(e.strip(),s.strip()) for (e,s) in zip(e_output, s_output)]


		num_preds = len(preds)
		num_ans = len(answer_key.keys())

		#parse the reference and prediction calculating score
		num_sents = len(answer_key)
		correct = 0 
		for (e,s) in preds:
			if e in answer_key:
				if answer_key[e] == s:
					correct +=1

		eps = 1e-10
		precision = float(correct)/num_preds
		recall = float(correct)/num_ans
		fscore = (2*precision*recall)/max((precision+recall), eps)
		scores[i] = fscore
		sys.stderr.write("precision = %f recall = %f score = %f weights: %f %f %f\n" % (precision, recall, fscore,weights[0],weights[1],weights[2]))

	max_idx = scores.index(max(scores))
	if max_idx == 0:
		dw *= 0.5
		dt *= 0.5
		dp *= 0.5
		if dw < 1:
			dw = 1
		
		dtheta = [[0,0,0],
				  [-dw,0,0],
				  [dw,0,0],
				  [0,-dt,0],
				  [0,dt,0],
				  [0,0,-dp],
				  [0,0,dp]]
	else:
		for j in xrange(0,len(weights)):
			theta[j] += dtheta[max_idx][j]

	sys.stderr.write("iteration: %d | score: %f | weights: %f %f %f\n" % (iteration,scores[max_idx],theta[0],theta[1],theta[2]))
	iteration += 1
