#!/usr/bin/env python
from __future__ import division
import optparse
import sys
import subprocess
from collections import namedtuple

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

# put stopwords from file into a list
stop_words = [word.strip() for word in open(opts.stop_file)]

# put each english sentence in file into a list
e_sents = [english.strip().split() for english in open(e_data) if len(english.strip()) > 0][:opts.num_sents]

# put each spanish sentence from file into a list
s_sents = [spanish.strip().split() for spanish in open(s_data) if len(spanish.strip()) > 0][:opts.num_sents]

# put the dictionary entries into a list
es_lists = [line.strip().split() for line in open(opts.esdict)]


# make a dictionary from spanish word to list of english words
es_map = {}
for es_line in es_lists:
    es_map[es_line[0]] = es_line[1:]

def bitmap(sequence):
    """ Generate a coverage bitmap for a sequence of indexes """
    return reduce(lambda x,y: x|y, map(lambda i: long('1'+'0'*i,2), sequence), 0)

phrase = namedtuple("phrase", "english, logprob")
def TM(filename, k):
    tm = {}
    for line in open(filename).readlines():
        (f, e, logprob) = line.strip().split(" ||| ")
        tm.setdefault(tuple(f.split()), []).append(phrase(e.strip(), float(logprob)))
    for f in tm: # prune all but top k translations
        tm[f].sort(key=lambda x: -x.logprob)
        del tm[f][k:]
    for word in set(sum(map(lambda x: tuple(x), s_sents),())):
        if (word,) not in tm:
            tm[(word,)] = [phrase(word, 0.0)]
    return tm

def find_alignments(tm, e, f):
    alignments = [[] for _ in e]
    for fi in xrange(len(f)):
        for fj in xrange(fi+1,len(f)+1):
            if f[fi:fj] in tm:
                for phrase in tm[f[fi:fj]]:
                    ephrase = tuple(phrase.english.split())
                    for ei in xrange(len(e)+1-len(ephrase)):
                        ej = ei+len(ephrase)
                        if ephrase == e[ei:ej]:
                            alignments[ei].append((ej, phrase.logprob, fi, fj))

def score_translation(tm, e, f, alignments):
    chart = [{} for _ in e] + [{}]
    chart[0][0] = 0.0
    for ei, sums in enumerate(chart[:-1]):
        for v in sums:
            for ej, logprob, fi, fj in alignments[ei]:
                if bitmap(range(fi,fj)) & v == 0:
                    new_v = bitmap(range(fi,fj)) | v
                    if new_v in chart[ej]:
                        chart[ej][new_v] = logadd10(chart[ej][new_v], sums[v]+logprob)
                    else:
                        chart[ej][new_v] = sums[v]+logprob
    goal = bitmap(range(len(f)))
    if goal in chart[len(e)]:
        return chart[len(e)][goal]
    else:
        return None

def align():
    # make lists for the aligned sentences that we will output
    e_output = []
    s_output = []
    tm = TM('tm', 50)
    for i, s_sent in enumerate(s_sents):
        best_score = 0.0
        best_sent = None
        for e_sent in e_sents[i-opts.win_size:i+opts.win_size]:
            alignments = find_alignments(tm, tuple(e_sent), tuple(s_sent))
            if alignments:
                score = score_translation(tm, e_sent, s_sent, alignments)
                if score > best_score:
                    best_sent = e_sent
        if best_sent:
            e_output.append(best_sent.join(" "))
            s_output.append(s_sent.join(" "))
    return (e_output, s_output)

def align_and_print():
    (e_output, s_output) = align()
    # create output files
    s_file = open(s_file_name, "w")
    e_file = open(e_file_name, "w")
    # write all the aligned sentences to the two output files
    for e in e_output:
        e_file.write(e + "\n")
    for s in s_output:
        s_file.write(s + "\n")
    # write the filenames containing the aligned sentences to stdout
    # this way we can pipe the output of this file into grade.py
    sys.stdout.write(e_file_name + "\n")
    sys.stdout.write(s_file_name + "\n")

align_and_print()
