##good test case for corroboration threshold.
##try for different levels of decisiveness: 0.2/0.5/0.8
## keep everything intact but increase num_trials to 100 or higher
## keep competence low at around 0.6
## for higher competence, there is little gain with corroboration
## you can also run a test for competence of 0.8 to compare



import Cognitivesimulation as sim
import json
import sys
import time
import simplejson as sj

num_fpro = 50
num_fcon = 40
num_groups = 1
num_agents = 20
agent_per_fact = 3
num_steps = 10000
w = 1
cap = 100
num_trials = 100
#graph_type = "spatial_random"
graph_type = "newman_watts_strogatz_graph"
radius = 0.2
agent_setup = []
spam = 0
selfish = 0
trust_used = False
inbox_trust_sorted = False
trust_filter_on  = False
e = 0.8
corraboration_threshold = 1
fname = 'out.txt'

if len(sys.argv) > 1:
    fname = sys.argv[1]


f = open(fname,"a")

for decisiveness in [0.2, 0.5, 0.8]:
    for (num_npro, num_ncon,c) in [ (10,100,0.8), (50,100,0.6) ]:
        for corraboration_threshold in [1,2,4]:
                results = sim.run_simulation(num_fpro, \
                                             num_fcon, \
                                             num_npro,\
                                             num_ncon, \
                                             num_groups, \
                                             num_agents, \
                                             agent_per_fact,\
                                             radius, \
                                             num_steps, \
                                             w, c, e, decisiveness, \
                                             # CM # Missing!
                                             corraboration_threshold, \
                                             # DISC_W_AMBIG, DISP, OUT_CAPACITY,  # Missing!
                                             cap, \
                                             num_trials, \
                                             graph_type,\
                                             agent_setup,\
                                             spam, selfish,\
                                             trust_used,\
                                             inbox_trust_sorted, \
                                             trust_filter_on)


                f.write(sj.dumps(results) + "\n")

                infostr = "comp: %.2f, e: %.2f, good: %d/%d, bad: %d/%d, "\
                          "maxsa: %.2f, decisiveness: %.2f, agf: %d, cf: %d, capacity: %d" \
                          %(c, e, num_fpro, num_npro, num_fcon, num_ncon, \
                            results['all_sa'][-1][0]/90.,\
                            decisiveness, agent_per_fact, corraboration_threshold, cap)
                print infostr
                infostr = "correct/all: "
                for i in range(0,len(results['decisions'])):
                    if results['decisions'][i] == 0:
                        continue
                    infostr += " %d%%/%d "\
                        %(100*results['correct_decisions'][i]/(float(results['decisions'][i])), \
                          results['decisions'][i])
                    if results['decisions'][i] == 20 or \
                       (i > 0 and results['decisions'][i-1] == results['decisions'][i]):
                        break
                print infostr
                print
