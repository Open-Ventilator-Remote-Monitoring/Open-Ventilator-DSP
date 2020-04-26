import numpy as np

class WelfordRunningStat(object):
    def __init__(self):
        self.std = 1
        self.tick = 1
        self.mean = 0
        self.var = 1

    def increment(self, x):
        old_mean = self.mean
        old_var = self.var
        self.mean = old_mean + (x - old_mean) / (self.tick+1)
        self.var = old_var + (x - old_mean)*(x - self.mean)
        self.tick += 1

    def reset(self):
        self.std = np.sqrt(self.var / self.tick)
        self.tick = 2
        self.mean = 0
        self.var = 0

class PowerStat(object):
    def __init__(self):
        self.tick = 1
        self.power = 0

    def increment(self,x):
        self.power += x*x
        self.tick += 1

    def reset(self):
        self.power = 0
        self.tick = 1

    @property
    def std(self):
        return self.power / self.tick