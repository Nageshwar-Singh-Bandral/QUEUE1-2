import random
import simpy
import numpy as np
import math
from queueing.probabilities import *
import pandas as pd
import scipy.stats as st


class Queue(object):
    """
    Create the initial object queue
    """

    def __init__(self, env, servers, servicetime):
        self.env = env
        self.server = simpy.Resource(env, servers)
        self.servicetime = servicetime

    def service(self, customer, servicetime):
        """The process"""
        yield self.env.timeout(np.random.exponential(1/servicetime, 1)[0])


def customer(env, name, qu, servicetime):
    """Each customer has a ``name`` and requests a server
    Subsequently, it starts a process.
    need to do sthis differently though...
    """

    global arrivals

    a = env.now
    # print(f'{name} arrives at the servicedesk at {a:.2f}')
    # arrivals += 1

    with qu.server.request() as request:
        yield request

        global counter
        global waiting_time
        global leavers

        b = env.now
        # print('%s enters the servicedesk at %.2f.' % (name, b))
        waitingtime = (b - a)
        # print(f'{name} waiting time was {waitingtime:.2f}')
        waiting_time += waitingtime
        counter += 1

        yield env.process(qu.service(name, servicetime))
        # print('%s leaves the servicedesk at %.2f.' % (name, env.now))
        # leavers += 1


def setup(env, servers, servicetime, Lambda):
    """Create a queue, a number of initial customers and keep creating customers
    approx. every 1/lambda*60 minutes."""
    # Generate queue
    queue = Queue(env, servers, servicetime)

    # Create 1 initial customer
    # for i in range(1):
    i = 0
    env.process(customer(env, f'Customer {i}', queue, servicetime))

    # Create more customers while the simulation is running
    while True:
        yield env.timeout(np.random.exponential(1/Lambda, 1)[0])
        i += 1
        env.process(customer(env, f'Customer {i}', queue, servicetime))




# Setup and start the simulation
print('QUEUE SIMULATION\n')

# Set servers = 1
# set the amount of simulations
SIMULATIONS = 500
column = ['RHO', 'SIM_TIME', 'AVG_WAIT']
data_sims = []
servers =[1,2,4] # fixed
rho = 0.9
MU = 1
SIM_TIME = 5000 # 1/lambda is exponential inter arrival times

for SERVERS in servers:
    LAMBDA = rho * (MU * SERVERS)
    # Create dataframe to store important values to calculate statistics
    data = pd.DataFrame(columns=column)
    for s in range(SIMULATIONS):

        waiting_time = 0
        counter = 0

        # Create an environment and start the setup process
        env = simpy.Environment()
        env.process(setup(env, SERVERS, MU, LAMBDA))

        # Execute the simulation
        env.run(until=SIM_TIME)

        avg_waiting = waiting_time/(counter)

        data.loc[s] = [rho, SIM_TIME, avg_waiting]

    data.to_csv(f'data/s{SIM_TIME}-{SERVERS}.txt', sep='\t', index=False)
