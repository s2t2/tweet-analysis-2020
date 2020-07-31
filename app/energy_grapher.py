

from functools import lru_cache

#from app.botcode_v2 import _______, ______, _______

class EnergyGrapher():
    def __init__(self, rt_graph):
        self.rt_graph = rt_graph

    @property
    @lru_cache(maxsize=None)
    def prior_probabilities(self):
        return dict.fromkeys(list(self.rt_graph.nodes), 0.5) # set all screen names to 0.5

    @property
    @lru_cache(maxsize=None)
    def energy_graph(self):
        return self.compile_energy_graph()

    def compile_energy_graph(self):
        pass # TODO
