# Resource constrained shortest path

From: http://people.brunel.ac.uk/~mastjjb/jeb/orlib/rcspinfo.html

There are currently 24 data files.

These data files are the 24 test problems from Table 1 of
J.E.Beasley and N.Christofides "An algorithm for the
resource constrained shortest path problem" Networks 19 (1989)
379-394.

Test problems 1, 2, ..., 24 from Table 1 of that paper are
available in files rcsp1, rcsp2, ..., rcsp24 respectively.

The format of these data files is:
number of vertices (n), number of arcs (m), number of resources (K)
for each resource k (k=1,...,K): the lower limit on the resources
consumed on the chosen path
for each resource k (k=1,...,K): the upper limit on the resources
consumed on the chosen path
for each vertex i (i=1,...,n): the amount of each resource k 
(k=1,...,K) consumed in passing through vertex i
for each arc j (j=1,...,m): vertex at start of the arc, vertex at 
end of the arc, cost of the arc, the amount of each resource k  
(k=1,...,K) consumed in traversing the arc

The value of the optimal solution for each of these data files 
is given in the above paper.

The largest file is rcsp21 of size 220Kb (approximately).
The entire set of files is of size 1800Kb (approximately).
