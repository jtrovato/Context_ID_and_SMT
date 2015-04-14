#!/usr/bin/env python
import optparse
import sys
import math

file1 = sys.stdin.readline().strip()
file2 = sys.stdin.readline().strip()

optparser = optparse.OptionParser()
optparser.add_option("-e", "--ans_en", dest="answers_en", default="wikidata/es/pairs.enu.snt", help="File containing the english article")
optparser.add_option("-s", "--ans_es", dest="answers_es", default="wikidata/es/pairs.esn.snt", help="File containing the spanish article")
optparser.add_option("-p", "--pred_en", dest="preds_en", default=file1, help="File containing the english preds")
optparser.add_option("-q", "--pred_es", dest="preds_es", default=file2, help="File containing the english preds")
optparser.add_option("-v", "--verbosity", dest="verbosity", default=1, type="int", help="Verbosity level, 0-3 (default=1)")
opts = optparser.parse_args()[0]

answer_key = {}
answer_key = {e.strip(): s.strip() for (e,s) in zip(open(opts.answers_en).readlines(), open(opts.answers_es).readlines())}
preds = [(e.strip(),s.strip()) for (e,s) in zip(open(opts.preds_en).readlines(), open(opts.preds_es).readlines())]

f = open('pred.en', 'w')
for key in answer_key.keys():
	f.write(key + '\n')
f.close()
f = open('pred.es', 'w')
for val in answer_key.values():
	f.write(val + '\n')
f.close()

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
sys.stderr.write("precision = %f recall = %f\n" % (precision, recall))
sys.stderr.write("score = %f\n" % fscore)

