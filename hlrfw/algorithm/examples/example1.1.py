import sys
sys.path.append('C:\\Users\\Administrator\\Desktop\\1111\\allpairs-master')
import metacomm.combinatorics.all_pairs2
all_pairs = metacomm.combinatorics.all_pairs2.all_pairs2

"""
Demo of the basic functionality - just getting pairwise/n-wise combinations
"""


# sample parameters are is taken from 
# http://www.stsc.hill.af.mil/consulting/sw_testing/improvement/cst.html


parameters = [ [ 0, 1 ]
             , [ 0, 1]
             , [ 0, 1, 2 ]
             , [ 0, 1, 2 ]
             , [ 0, 1, 2 ]
             ]

pairwise = all_pairs( parameters )

print "PAIRWISE:"
for i, v in enumerate(pairwise):
    print "%i:\t%s" % (i, str(v))


    