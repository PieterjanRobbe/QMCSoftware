""" Abstract Class TrueMeasure """

from .._util import DimensionError, TransformError, univ_repr, ParameterError

from abc import ABC
from numpy import array, int64, ndarray
from copy import deepcopy


class TrueMeasure(ABC):
    """ The True Measure of the Integrand """

    def __init__(self, dimension, **kwargs):
        """
        Args:
            dimension (ndarray): dimension(s) of the integrand(s)
            keys: string matching the measure mimiced by the discrete \
                distribution
            values: functions to transform a sample by the mimiced \
                measure into a sapmle by the true measure
        """
        prefix = 'A concrete implementation of TrueMeasure must have '
        if not hasattr(self, 'transforms'):
            raise ParameterError(prefix+'self.transforms')
        super().__init__()
        self.dimension = dimension
        for key, val in kwargs.items():
                setattr(self, key, array(val))
        if not dimension:  # construcing a sub-measure
            return
        # Type check dimension
        if isinstance(self.dimension, int):  # int -> ndarray
            self.dimension = array([self.dimension])
        if all(isinstance(i, int) or isinstance(i, int64)
               and i > 0 for i in self.dimension):  # all positive integers
            self.dimension = array(self.dimension)
        else:
            raise DimensionError(
                "dimension must be an numpy.ndarray/list of positive integers")
        # Type check measureData
        for key, val in kwargs.items():
            if not isinstance(kwargs[key], (list, ndarray)):
                # put single value into ndarray
                kwargs[key] = [kwargs[key]]
            if len(kwargs[key]) == 1 and len(self.dimension) != 1:
                # copy single-value to all levels
                kwargs[key] = kwargs[key] * len(self.dimension)
            if len(kwargs[key]) != len(self.dimension):
                raise DimensionError(
                    key + " must be a numpy.ndarray (or list) of len(dimension)")
        self.measures = [type(self)(None) for i in range(len(self.dimension))]
        # Create list of measures with proper dimensions and keyword arguments
        for i, _ in enumerate(self):
            self[i].dimension = self.dimension[i]
            for key, val in kwargs.items():
                setattr(self[i], key, array(val[i]))
            self[i].transforms = self.transforms

    def set_tm_gen(self, discrete_distrib):
        """
        Initialize gen_tm_samples method,
        a method that samples from the discrete_distribution
        and transforms to discrete distribution

        Args:
            discrete_distrib (DiscreteDistribution): the discrete
                distribution samples will be drawn from will use
                discrete_distrib.mimics to select transform from
                self[i].transforms (dict)
        """
        for measure_i in self:
            discrete_distrib_i = deepcopy(discrete_distrib)
            if discrete_distrib_i.mimics not in list(measure_i.transforms.keys()):
                raise TransformError(
                    "Cannot tranform %s to %s" %
                    (type(discrete_distrib_i).__name__, type(self).__name__))
            measure_i.gen_tm_samples = lambda r, n, self=measure_i: \
                self.transforms[discrete_distrib_i.mimics][0](self,
                    discrete_distrib_i.gen_dd_samples(r, n, self.dimension))

    def gen_tm_samples(self, r, n):
        """
        Generate r nxd samples mimicing the TrueMeasure (d = self.dimension
        inferred). This method is a wrapper around gen_dd_samples that applies a
        transform to the result.

        Args:
            r (int): Number of nxd matrices to generate (sample.size()[0])
            n (int): Number of observations (sample.size()[1])


        Returns:
            rxnxd (numpy array) with d being the dimension of the true
            measure space (sample.size()[2])

        Note:
            To initilize this method for each integrand, call ::

                true_measure_obj.set_tm_gen(discrete_distrib_obj)

            This method is not to be called directly on the original
            constructing object.
            Calls to this method should be from the i^th integrand.
            Example call: ::

                true_measure_obj[i].gen_tm_samples(n,r)

        Raises:
            TransformError if this method is called on the original \
            construcing TrueMeasure object or has not \
            been initialized for each true measure yet
        """
        raise TransformError('''
            To initilize this method for each integrand call:
                true_measure_obj.set_tm_gen(discrete_distrib_obj)
            To call this method for the ith integrand call:
                true_measure_obj[i].gen_tm_samples(n,r)
            ''')

    def set_f(self, integrand, discrete_distrib):
        """
        Initialize f method for each integrand:
        a method that takes in samples generated by gen_tm_samples
        and outputs the integrand samples values

        Args:
            discrete_distrib (DiscreteDistribution): the discrete
                distribution samples will be drawn from.
                discrete_distrib.mimics is uesd as key to
                self[i].transforms (dict)
            integrand (Integrand): the constructing integrand object
        """
        if len(integrand) != len(self):
            raise TransformError("Number of distributions must match number of integrands")
        for integrand_i, measure_i in zip(integrand, self):
            if discrete_distrib.mimics not in list(measure_i.transforms.keys()):
                raise TransformError(
                    "Cannot tranform %s to %s" %
                    (type(discrete_distrib).__name__, type(measure_i).__name__))
            integrand_i.f = lambda x, self=integrand_i, msr_obj=measure_i: \
                msr_obj.transforms[discrete_distrib.mimics][1](msr_obj, self.g(x))

    def transform(self, integrand, discrete_distrib):
        """
        Calls self.set_tm_gen(discrete_distrib) then
        calls self.set_f(integrand, discrete_distrib)
        Respectively, these two methods initialize
        true_measure_obj[i].gen_tm_samples(r,n)
        and integrand[i].f(x)
        for i=1,2,...,len(integrand_obj)
        Note: len(integrand_obj)=len(true_measure_obj)

        Args:
            discrete_distrib (DiscreteDistribution): the discrete
                distribution samples will be drawn from.
                discrete_distrib.mimics is uesd as key to
                self[i].transforms (dict)
            integrand (Integrand): the constructing integrand object
        """
        self.set_tm_gen(discrete_distrib)
        self.set_f(integrand, discrete_distrib)

    def __len__(self):
        return len(self.measures)

    def __iter__(self):
        for measure in self.measures:
            yield measure

    def __getitem__(self, i):
        return self.measures[i]

    def __setitem__(self, i, val):
        self.measures[i] = val

    def __repr__(self, attributes=[]):
        """
        Print important attribute values

        Args: 
            attributes (list): list of attributes to print
        
        Returns:
            string of self info
        """
        attributes = set(attributes + ['dimension'])
        return univ_repr(self, "True Measure", attributes)