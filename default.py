#!/usr/bin/env python
from __future__ import division
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-d", "--data", dest="train", default="wikidata/es/", help="Data filename prefix (default=data)")
optparser.add_option("-e", "--english", dest="english", default="orig.enu.snt", help="Suffix of English filename")
optparser.add_option("-s", "--spanish", dest="spanish", default="orig.esn.snt", help="Suffix of French filename")
optparser.add_option("-o", "--output", dest="output", default="output", help="Prefix of filename to output to")
optparser.add_option("-r", "--dict", dest="esdict", default="./dict.es", help="Spanish to English Dictionary")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.01, type="float", help="Threshold (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()
s_data = "%s%s" % (opts.train, opts.spanish)
e_data = "%s%s" % (opts.train, opts.english)
s_file_name = "%s%s" % (opts.output, ".es")
e_file_name = "%s%s" % (opts.output, ".en")

#put each english sentence in file into a list
e_sents = [english.strip() for english in open(e_data) if len(english.strip()) > 0][:opts.num_sents]
#put each spanish sentence from file into a list
s_sents = [spanish.strip() for spanish in open(s_data) if len(spanish.strip()) > 0][:opts.num_sents]

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
	aligned = False
	for s in s_sents[start:end]:
		if not aligned:
			count_overlap = 0
			for s_word in s.split():
				if s_word in es_map:
					translated = False
					translations = es_map[s_word]
					for e_word in e.split():
						if e_word in translations and not translated:
							translated = True
							count_overlap = count_overlap + 1
			score = count_overlap / len(e)
			#append each sentence if above thresh
			if score > opts.threshold:
				aligned = True
				e_output.append(e)
				s_output.append(s)

s_file = open(s_file_name, "w")
e_file = open(e_file_name, "w")

for e in e_output:
	e_file.write(e + "\n")
for s in s_output:
	s_file.write(s + "\n")

sys.stdout.write(e_file_name + "\n")
sys.stdout.write(s_file_name + "\n")
