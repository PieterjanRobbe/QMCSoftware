from .._discrete_distribution import DiscreteDistribution
from .gail_lattice import gail_lattice_gen
from .mps_lattice import mps_lattice_gen
from ...util import ParameterError
from numpy import array, log2, repeat, vstack, random
import warnings


class Lattice(DiscreteDistribution):
    """
    Quasi-Random Lattice nets in base 2.
    
    >>> l = Lattice(2,seed=7)
    >>> l
    Lattice (DiscreteDistribution Object)
        dimension       2^(1)
        randomize       1
        seed            7
        backend         gail
        mimics          StdUniform
    >>> l.gen_samples(4)
    array([[0.076, 0.78 ],
           [0.576, 0.28 ],
           [0.326, 0.03 ],
           [0.826, 0.53 ]])
    >>> l.set_dimension(3)
    >>> l.gen_samples(n_min=4,n_max=8)
    array([[0.563, 0.348, 0.103],
           [0.063, 0.848, 0.603],
           [0.813, 0.598, 0.353],
           [0.313, 0.098, 0.853]])
    >>> Lattice(dimension=2,randomize=False,backend='GAIL').gen_samples(n_min=2,n_max=4)
    array([[0.25, 0.25],
           [0.75, 0.75]])
    >>> Lattice(dimension=2,randomize=False,backend='MPS').gen_samples(n_min=2,n_max=4)
    array([[0.25, 0.25],
           [0.75, 0.75]])

    References
        Sou-Cheng T. Choi, Yuhan Ding, Fred J. Hickernell, Lan Jiang, 
        Lluis Antoni Jimenez Rugama, Da Li, Jagadeeswaran Rathinavel, 
        Xin Tong, Kan Zhang, Yizhi Zhang, and Xuan Zhou, 
        GAIL: Guaranteed Automatic Integration Library (Version 2.3) 
        [MATLAB Software], 2019. Available from http://gailgithub.github.io/GAIL_Dev/

        F.Y. Kuo & D. Nuyens.
        Application of quasi-Monte Carlo methods to elliptic PDEs with random diffusion coefficients 
        - a survey of analysis and implementation, Foundations of Computational Mathematics, 
        16(6):1631-1696, 2016.
        springer link: https://link.springer.com/article/10.1007/s10208-016-9329-5
        arxiv link: https://arxiv.org/abs/1606.06613
        
        D. Nuyens, `The Magic Point Shop of QMC point generators and generating
        vectors.` MATLAB and Python software, 2018. Available from
        https://people.cs.kuleuven.be/~dirk.nuyens/

        Constructing embedded lattice rules for multivariate integration
        R Cools, FY Kuo, D Nuyens -  SIAM J. Sci. Comput., 28(6), 2162-2188.
    """

    parameters = ['dimension','randomize','seed','backend','mimics']
    
    def __init__(self, dimension=1, randomize=True, seed=None, backend='GAIL'):
        """
        Args:
            dimension (int): dimension of samples
            randomize (bool): If True, apply shift to generated samples    
            seed (int): seed the random number generator for reproducibility
            backend (str): backend generator must be either "GAIL" or "MPS". 
                "GAIL" provides standard point ordering but is slightly slower than "MPS".
        """
        self.dimension = dimension
        self.randomize = randomize
        self.seed = seed
        self.backend = backend.lower()            
        if self.backend == 'gail':
            self.backend_gen = gail_lattice_gen
        elif self.backend == 'mps':
            self.backend_gen = mps_lattice_gen
        else:
            raise ParameterError("Lattice backend must 'GAIL' or 'MPS'")
        self.mimics = 'StdUniform'
        self.set_seed(self.seed)
        super(Lattice,self).__init__()

    def gen_samples(self, n=None, n_min=0, n_max=8):
        """
        Generate lattice samples

        Args:
            n (int): if n is supplied, generate from n_min=0 to n_max=n samples. 
                Otherwise use the n_min and n_max explicitly supplied as the following 2 arguments
            n_min (int): Starting index of sequence. Must be 0 or n_max/2
            n_max (int): Final index of sequence. Must be a power of 2.

        Returns:
            ndarray: (n_max-n_min) x d (dimension) array of samples
        """
        if n:
            n_min = 0
            n_max = n     
        if log2(n_max) % 1 != 0:
            raise ParameterError("n_max must be a power of 2")
        if not (n_min == 0 or n_min == float(n_max)/2):
            raise ParameterError("n_min must be 0 or n_max/2")
        x_lat = self.backend_gen(n_min,n_max,self.dimension)
        if self.randomize: # apply random shift to samples
            x_lat = (x_lat + self.shift)%1
        return x_lat
    
    def set_seed(self, seed):
        """
        Reseed the generator to get a new scrambling.

        Args:
            seed (int): new seed for generator
        """
        self.seed = seed
        random.seed(self.seed)
        self.shift = random.rand(self.dimension)
    
    def set_dimension(self, dimension):
        """
        See abstract method. 

        Note:
            Will compute a new random shift to be applied to samples
        """
        self.dimension = dimension
        self.shift = random.rand(self.dimension)
