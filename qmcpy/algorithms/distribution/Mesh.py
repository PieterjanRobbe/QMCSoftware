''' Originally developed in MATLAB by Fred Hickernell. Translated to python by Sou-Cheng T. Choi and Aleksei Sorokin '''

from numpy import array, int64, log, random
from numpy.core._multiarray_umath import zeros
from third_party.magic_point_shop.digitalseq_b2g import digitalseq_b2g
from third_party.magic_point_shop.latticeseq_b2 import latticeseq_b2

from . import discreteDistribution


class Mesh(discreteDistribution):

    def __init__(self,distribData=None,trueD=None):
        state = []
        super().__init__(distribData,state,trueD=trueD)
        if trueD:
            self.distrib_list = [Mesh() for i in range(len(trueD))]
            # self now refers to self.distrib_list
            for i in range(len(self)):
                self[i].trueD = self.trueD[i]
                self[i].distribData = self.distribData[i] if self.distribData else None

    def genDistrib(self,n,m,j=1):
        # get j randomly shifted nxm arrays 
        mimicMeasure = self.trueD.measureName
        if mimicMeasure=='stdUniform':
            meshType = self.trueD.measureData['meshType']
            if meshType=='lattice': return self.get_RS_lattice_b2(n,m,j)
            elif meshType=='sobol': return self.get_RS_sobol_b2g(n,m,j)
            else: raise Exception("%s mesh cannot mimic %s distribution"%(meshType,mimicMeasure))
        else: raise Exception('Distribution not recognized')


    def get_RS_sobol_b2g(self,n,m,j):
        # generates j shifted nxm sobol digital sequences
        gen = digitalseq_b2g(Cs='./third_party/magic_point_shop/sobol_Cs.col',m=int(log(n)/log(2)),s=m)
        t = max(32,gen.t) # we will guarantee at least a depth of 32 bits for the shift
        ct = max(0,t-gen.t) # this is the correction factor to scale the integers
        shifts = random.randint(2**t, size=(j,m), dtype=int64) # generate random shift
        x = zeros((n,m),dtype=int64)
        for i,row in enumerate(gen):
            x[i,:] = gen.cur
        x_RS = array([(shift ^ (x * 2**ct)) / 2.**t for shift in shifts])
        return x_RS


    def get_RS_lattice_b2(self, n, m, j):  # generates j shifted nxm lattices
        x = array([row for row in latticeseq_b2(m=int(log(n) / log(2)), s=m)])
        shifts = random.rand(j, m)
        RS_x = array([(x + random.rand(m)) % 1 for shift in shifts])
        return RS_x

if __name__ == "__main__":
    from time import time

    t0 = time()

    n, m, j = 1024, 3, 16  # We want to generate j randomly shifted nxm lattices
    print('\nlattice_b2 without random shift:\n',
          array([row for row in latticeseq_b2(m=int(log(n) / log(2)), s=m)]))
    print('\n2 randomly shifted lattices:\n', get_RS_lattice_b2(n, m, j))

    t_delta = time() - t0
    print('\n\nRuntime:', t_delta)