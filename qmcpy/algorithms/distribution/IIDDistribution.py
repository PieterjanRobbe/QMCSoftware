''' Originally developed in MATLAB by Fred Hickernell. Translated to python by Sou-Cheng T. Choi and Aleksei Sorokin '''
from numpy import random

from . import DiscreteDistribution

class IIDDistribution(DiscreteDistribution):
    '''
    Specifies and generates the components of :math:`\dfrac{1}{n} \sum_{i=1}^n \delta_{\mathbf{x}_i}(\cdot)`
    where the :math:`\mathbf{x}_i` are IIDDistribution uniform on :math:`[0,1]^d` or IIDDistribution standard Gaussian
    '''
    
    def __init__(self, trueD=None, distrib_data=None, rngSeed=None):
        accepted_measures = ['StdUniform','StdGaussian']
        if rngSeed: random.seed(rngSeed)
        super().__init__(accepted_measures, trueD, distrib_data)

    def gen_distrib(self, n, m, j=1):
        if type(self.trueD).__name__=='StdUniform': return random.rand(j,int(n),int(m)).squeeze()
        elif type(self.trueD).__name__=='StdGaussian': return random.randn(j,int(n),int(m)).squeeze()