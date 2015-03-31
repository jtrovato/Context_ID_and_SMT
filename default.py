#!/usr/bin/env python
from __future__ import division
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-d", "--data", dest="train", default="wikidata/es/", help="Data filename prefix (default=data)")
optparser.add_option("-e", "--english", dest="english", default="orig.enu.snt", help="Suffix of English filename (default=e)")
optparser.add_option("-f", "--spanish", dest="spanish", default="orig.esn.snt", help="Suffix of French filename (default=f)")
optparser.add_option("-r", "--dict", dest="esdict", default="./dict.es", help="Spanish to English Dictionary")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()
s_data = "%s.%s" % (opts.train, opts.spanish)
e_data = "%s.%s" % (opts.train, opts.english)

#put each english sentence in file into a list
e_sents = [english.strip() for english in open(e_data)][:opts.num_sents]
#put each spanish sentence from file into a list
s_sents = [spanish.strip() for spanish in open(s_data)][:opts.num_sents]

es_lists = [line.strip().split() for line in open(opts.esdict)]

e_output = []
s_output = []

#make a dictionary from spanish word to list of english words
es_map = {}
for es_line in es_lists:
	es_map[es_line[0]] = es_line[1:]

for eindex, e in enumerate(e_sents):
	start = max(0, eindex - 5)
	end = min(len(s_sents), eindex + 5)
	aligned = false
	for s in s_sents[start:end]:
		if not aligned:
			count_overlap = 0
			for s_word in s.split():
				if s_word in es_map:
					translated = false
					translations = es_map[s_word]
					for e_word in e.split:
						if e_word in translations and not translated:
							translated = true
							count_overlap = count_overlap + 1
			score = count_overlap / len(e)
			if score > opts.threshold:
				aligned = true
				e_output.append(e)
				s_output.append(s)

			




