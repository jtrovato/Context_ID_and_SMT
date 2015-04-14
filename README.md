For Students attempting the homework:

There are two python files that you will use to complete this assignment. 

default.py takes in command line arguements specificy parallel wikipedia articels and outputs two filenames, the first contains english sentences from the input data and the second contains the corresponding aligned spanish sentences.

grade.py takes in two filenames, in the format mentioned above, adn output a score for the alignment based on hand aligned data. 

These scripts can be used with pipes like so...

./default | ./grade

The data you will be using is contained in ./wikidata/es/ . In this directory, you find the original wikipedia articles that look like orig.enu.snt  and the test file that have a ",test" appended tot he file name. In this folder, their are also aligned sentence in files that begin with "pairs"

For CIS526 Staff:

Everything mentioned for the students also applies to you. Also in this directory are python scipts for the baseline performance as well as 6 extensions that all offer improvement on the baseline implementation. If released as a homework the   *.test files should be removed and be sed for calculating leaderboard positions. Similarly, the baseline and extension files should also be removed. 