#!/usr/bin/env python
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-d", "--data", dest="train", default="wikidata/es/", help="Data filename prefix (default=data)")
optparser.add_option("-e", "--english", dest="english", default="orig.enu.snt", help="Suffix of English filename (default=e)")
optparser.add_option("-f", "--french", dest="french", default="orig.esn.snt", help="Suffix of French filename (default=f)")
optparser.add_option("-r", "--dict", dest="esdict", default=
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()
s_data = "%s.%s" % (opts.train, opts.spanish)
e_data = "%s.%s" % (opts.train, opts.english)


#put each english sentence in file into a list
e_sents = [english for english in open(e_data)[:opts.num_sents]]
#put each spanish sentence from file into a list
s_sents = [spanish for spanish in open(s_data)[:opts.num_sents]]

for eindex, e in enumerate(e_sents):
	start = max(0, eindex - 5)
	end = min(len(s_sents), eindex + 5)
	for s in s_sents[start:end]:

