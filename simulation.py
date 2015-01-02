
import random 
import Agent 
import GraphGen as gg
import SimulationStats
import networkx as nx
from simutil import * 


########## Initialization code

def create_connectivity(agents, p, type='undirected_random'):
    if type == 'directed_random':
        conn = gg.random_undirected_graph(agents, p)
    elif type == 'spatial_random':
        conn = gg.spatial_random_graph(agents, p)
    elif type == 'hierarchy':
        conn = gg.hierarchy_graph(agents)
        for agent in agents[1:]:
            agent.uses_knowledge = False
        if p==1: ##team leaders can do filtering
            for agent in agents[1:5]:
                agent.uses_knowledge = True
    elif type == 'collaborative':
        conn = gg.collaborative_graph(agents)
        for agent in agents[1:]:
            agent.uses_knowledge = False
        if p==1: ##team leaders can do filtering
            for agent in agents[1:5]:
                agent.uses_knowledge = True
    else:
        conn = gg.random_directed_graph(agents, p)
        
    for agent1 in conn.nodes():
        agent1.connect_to(conn.neighbors(agent1))
    
    if type in ['hierarchy', 'collaborative']:
        return (1, len(agents))
    else:
        cc_conn = nx.connected_components(conn)
        ## return the number of connected components and 
        ## the size of the largest connected component
        return (len(cc_conn), len(cc_conn[0]))

def change_agent_property(agents, setup):
    """
    Setup is a dictionary that has new values and a ratio.
    It changes a proportion of agents given by the ratio to the 
    given values for the given properties.

    """
    who = range(len(agents))
    random.shuffle(who)
    ratio = setup['ratio']

    if ratio > 1 or ratio < -1:
        return ## error ratio, should return without changing anything

    cutoff = int(len(agents)*ratio)
    if 'competence' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].competence = setup['competence']
    if 'willingness' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].willingness = setup['willingness']
    if 'spammer' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].spammer = setup['spammer']
    if 'selfish' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].selfish = setup['selfish']


########## Run simulation

def one_step_simulation(agents):
    num_actions = 0
    actions_taken = []
    for agent in agents:
        actions_taken = agent.act()  ##list of (n, fact)
        for (n,fact) in actions_taken:
            num_actions += 1
            n.receive(fact, agent)
    return num_actions


def multi_step_simulation(NUM_FACTS, NUM_NOISE, NUM_AGENTS, \
                          AGENT_PER_FACT, CONNECTION_PROBABILITY, \
                          NUM_STEPS, WILLINGNESS, COMPETENCE, \
                          GRAPH_TYPE, AGENT_SETUP=[], \
                          SPAMMINESS=0, SELFISHNESS=0, \
                          TRUST_USED=True, INBOX_TRUST_SORTED=False, \
                          TRUST_FILTER_ON=True):
    
    facts = range(NUM_FACTS + NUM_NOISE)
    ##print "Created", len(facts), "facts"

    agents = []
    for i in xrange(NUM_AGENTS):
        agents.append ( Agent.Agent(WILLINGNESS, COMPETENCE, \
                                    NUM_FACTS, NUM_NOISE,\
                                    SPAMMINESS, SELFISHNESS, \
                                    TRUST_USED, INBOX_TRUST_SORTED, \
                                    TRUST_FILTER_ON) )

    ## Now, change the properties of some agents 
    ## based on the agent setup data
    for setup in AGENT_SETUP: ## each setup is a dictionary
        change_agent_property(agents, setup)

    ##print "Created" , len(agents), "agents"

    ## Create agent graph
    (num_cc, size_lcc) = create_connectivity(agents, CONNECTION_PROBABILITY, GRAPH_TYPE)

    ## Distribute facts to agents
    for i in facts:
        for j in xrange(AGENT_PER_FACT):
            ## find a random agent, and distribute fact i
            k = random.randint(0,NUM_AGENTS-1)
            agents[k].add_fact(i)
            
    ## Initialize agents to send everything that they think is valuable 
    ## in their outbox
    for agent in agents:
        agent.init_outbox()

    action_list = []
    all_stats = SimulationStats.SimulationStats(NUM_FACTS, \
                                                NUM_NOISE,\
                                                num_cc, \
                                                size_lcc)
    for i in xrange(NUM_STEPS):
        x = one_step_simulation(agents)
        action_list.append(x)
        if i%100 == 0:
            all_stats.update_stats(agents,i)

    return all_stats


def run_simulation(NUM_FACTS, NUM_NOISE, NUM_AGENTS, \
                   AGENT_PER_FACT, CONNECTION_PROBABILITY, \
                   NUM_STEPS,  WILLINGNESS, COMPETENCE, NUM_TRIAL,\
                   GRAPH_TYPE, AGENT_SETUP=[], \
                   SPAMMINESS=0, SELFISHNESS=0, \
                   TRUST_USED=True, INBOX_TRUST_SORTED = False,\
                   TRUST_FILTER_ON=True):
    all_stats = multi_step_simulation(NUM_FACTS,\
                                      NUM_NOISE, \
                                      NUM_AGENTS, \
                                      AGENT_PER_FACT,\
                                      CONNECTION_PROBABILITY,\
                                      NUM_STEPS, WILLINGNESS,\
                                      COMPETENCE, GRAPH_TYPE,\
                                      AGENT_SETUP, \
                                      SPAMMINESS, SELFISHNESS, \
                                      TRUST_USED, \
                                      INBOX_TRUST_SORTED, \
                                      TRUST_FILTER_ON )

    for i in xrange(1, NUM_TRIAL):
        new_stats = multi_step_simulation(NUM_FACTS, NUM_NOISE, \
                                          NUM_AGENTS, \
                                          AGENT_PER_FACT, \
                                          CONNECTION_PROBABILITY,\
                                          NUM_STEPS, WILLINGNESS,\
                                          COMPETENCE, GRAPH_TYPE, \
                                          AGENT_SETUP, \
                                          SPAMMINESS, SELFISHNESS, \
                                          TRUST_USED, \
                                          INBOX_TRUST_SORTED, \
                                          TRUST_FILTER_ON )
        all_stats.merge_stats(new_stats)

    summary_results = all_stats.process_sa()

    results = {}
    results['setup'] = {'num_facts':NUM_FACTS, \
                        'num_noise': NUM_NOISE,\
                        'num_agents':NUM_AGENTS, \
                        'agent_per_fact':AGENT_PER_FACT, \
                        'connection_probability_or_radius': CONNECTION_PROBABILITY, \
                        'num_steps': NUM_STEPS,\
                        'willingness': WILLINGNESS,\
                        'competence': COMPETENCE,\
                        'spamminess': SPAMMINESS, \
                        'selfishness': SELFISHNESS, \
                        'trust_used': TRUST_USED,\
                        'inbox_trust_sorted': INBOX_TRUST_SORTED, \
                        'trust_filter_on': TRUST_FILTER_ON, \
                        'num_trial': NUM_TRIAL,\
                        'graph_type': GRAPH_TYPE,\
                        'agent_setup': AGENT_SETUP}
    results['total_filtered'] = summary_results['total_filtered']
    results['num_cc'] = summary_results['num_cc']
    results['size_lcc'] = summary_results['size_lcc']
    results['summary_results'] = summary_results
    results['all_sa'] = all_stats.sa
    results['all_comm'] = all_stats.comm
    results['all_sa0'] = all_stats.sa0
    results['all_comm0'] = all_stats.comm0
    results['steps'] = all_stats.steps

    return (results)
    
########## Main body

if __name__ == '__main__':

    random.seed(10)

    NUM_FACTS = 50
    NUM_NOISE = 500
    NUM_AGENTS = 20
    AGENT_PER_FACT = 1
    CONNECTION_PROBABILITY = 0.5
    NUM_STEPS = 10000 ## how many steps to run each simulation
    WILLINGNESS = 1
    COMPETENCE = 1
    GRAPH_TYPE = 'spatial_random'

    NUM_TRIAL = 1
    ## number of times to repeat the simulation for averaging out values 

    # for i in xrange(5):
    #     w = 0.2 + 0.2*i
    #     for j in xrange(5):
    #         c = 0.2 + 0.2*j
    for i in xrange(2):
        w = 0.5 + 0.5*i
        for j in xrange(2):
            c = 0.5 + 0.5*j
            results = run_simulation(NUM_FACTS, \
                                         NUM_NOISE, NUM_AGENTS, \
                                         AGENT_PER_FACT,\
                                         CONNECTION_PROBABILITY, \
                                         NUM_STEPS, w, c, NUM_TRIAL, \
                                         GRAPH_TYPE, \
                                         AGENT_SETUP=[{ "ratio" : 0.2,\
                                                            "spammer" : 0.8, \
                                                            "competence":0.2 }])
            
            ##print results
            print 'w, c, num_cc, size_lcc'
            print w, c, results['num_cc'], results['size_lcc']
            print results
