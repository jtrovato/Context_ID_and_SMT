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
optparser.add_option("-t", "--threshold", dest="threshold", default=0.05, type="float", help="Threshold (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
optparser.add_option("-w", "--windowsize", dest="win_size", default=100, type="int", help="Window size")
optparser.add_option("-l", "--stoplist", dest="stop_file", default="stopwords.txt", help="List of stop words")
(opts, _) = optparser.parse_args()
s_data = "%s%s" % (opts.train, opts.spanish)
e_data = "%s%s" % (opts.train, opts.english)
s_file_name = "%s%s" % (opts.output, ".es")
e_file_name = "%s%s" % (opts.output, ".en")

#put stopwords from file into a list
stop_words = [word.strip() for word in open(opts.stop_file)]

#put each english sentence in file into a list
e_sents = [english.strip() for english in open(e_data) if len(english.strip()) > 0][:opts.num_sents]

#put each spanish sentence from file into a list
s_sents = [spanish.strip() for spanish in open(s_data) if len(spanish.strip()) > 0][:opts.num_sents]

#put the dictionary entries into a list
es_lists = [line.strip().split() for line in open(opts.esdict)]

#make lists for the aligned sentences that we will output
e_output = []
s_output = []

#make a dictionary from spanish word to list of english words
es_map = {}
for es_line in es_lists:
	es_map[es_line[0]] = es_line[1:]

for eindex, e in enumerate(e_sents):
	#only look at spanish sentences within the distance window
	start = max(0, eindex - opts.win_size)
	end = min(len(s_sents), eindex + opts.win_size)
	
	#keep track of best aligned score and sentence
        best_s = ''
        best_score = 0.0
	for s in s_sents[start:end]:
                count_overlap = 0
		#for this spanish sentence, count the number of spanish words
		#that have a dictionary translation in the english sentence
                for s_word in s.split():
                        if s_word in es_map:
                                translations = es_map[s_word]
                                for e_word in e.split():
                                        if e_word in translations and e_word not in stop_words:
                                                count_overlap += 1
                                                break
		#give the sentence a score normalized for length of the sentence
                score = float(count_overlap)/len(s)
                if score > best_score:
                        best_score = score
                        best_s = s
        #append each sentence if best alignment above thresh
        if best_score > opts.threshold:
                e_output.append(e)
                s_output.append(best_s)

#create output files
s_file = open(s_file_name, "w")
e_file = open(e_file_name, "w")

#write all the aligned sentences to the two output files
for e in e_output:
	e_file.write(e + "\n")
for s in s_output:
	s_file.write(s + "\n")

#write the filenames containing the aligned sentences to stdout
#this way we can pipe the output of this file into grade.py
sys.stdout.write(e_file_name + "\n")
sys.stdout.write(s_file_name + "\n")
