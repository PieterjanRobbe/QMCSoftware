""" Abstract Class TrueMeasure """

from abc import ABC
from numpy import array, int64, ndarray

from qmcpy._util import DimensionError, TransformError, univ_repr


class TrueMeasure(ABC):
    """ The True Measure of the Integrand """

    def __init__(self, dimension, transforms, **kwargs):
        """
        Args:
            dimension (ndarray): dimension's' of the integrand's'
            transforms (dict): functions that transform discrete distribution to true measure
                keys: string matching the measure mimiced by the discrete distribution
                values: functions to transform a sample by the mimiced measure into a sapmle by the true measure
        """
        self.dimension = dimension
        super().__init__()
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
            if type(kwargs[key]) != list and type(kwargs[key]) != ndarray:
                # put single value into ndarray
                kwargs[key] = [kwargs[key]]
            if len(kwargs[key]) == 1 and len(self.dimension) != 1:
                # copy single-value to all levels
                kwargs[key] = kwargs[key] * len(self.dimension)
            if len(kwargs[key]) != len(self.dimension):
                raise DimensionError(
                    key + " must be a numpy.ndarray (or list) of len(dimension)")
        self.measures = [type(self)(None)
                         for i in range(len(self.dimension))]
        # Create list of measures with proper dimensions and keyword arguments
        for i, _ in enumerate(self):
            self[i].dimension = self.dimension[i]
            for key, val in kwargs.items():
                setattr(self[i], key, val[i])
            self[i].transforms = transforms

    def transform_generator(self, discrete_distrib):
        """
        Create gen_tm_samples method,
        a method that samples from the discrete_distribution
        and transforms to discrete distribution

        Args:
            discrete_distrib (DiscreteDistribution): the discrete distribution samples will be drawn from
                will use discrete_distrib.mimics to select transform from self[i].transforms (dict)
        """
        for measure_i in self:
            if discrete_distrib.mimics not in list(measure_i.transforms.keys()):
                raise TransformError(
                    'Cannot tranform %s to %s' % \
                        (type(discrete_distrib).__name__, type(self).__name__))
            measure_i.gen_tm_samples = lambda r, n, self=measure_i: \
                self.transforms[discrete_distrib.mimics](self,
                    discrete_distrib.gen_dd_samples(int(r), int(n), int(self.dimension)))
    
    def gen_tm_samples(self, r, n):
        """
        Generate r nxd samples mimicing the TrueMeasure (d = self.dimension inferred)
        This method is a wrapper around gen_dd_samples that applies a transform to the result

        Args:
            r (int): Number of nxd matrices to generate (sample.size()[0])
            n (int): Number of observations (sample.size()[1])
            Inferred: d (int): Number of dimensions (sample.size()[2])

        Returns:
            rxnxd (numpy array)
        
        Note:
            To initilize this method for each integrand call
                    true_measure_obj.transform_generator(discrete_distrib_obj)
            This method is not to be called directly on the original constructing object
            Calls to this method should be from the i^th integrand
                Example call: true_measure_obj[i].gen_tm_samples(n,r)

        Raises: 
            TransformError if this method is called on the original construcing TrueMeasure object
        """
        raise TransformError('To initilize this method for each integrand call:\n\t\
                            true_measure_obj.transform_generator(discrete_distrib_obj)\n\
                        To call this method for the ith integrand call:\n\t\
                            true_measure_obj[i].gen_tm_samples(n,r)')

    def summarize(self):
        """ Print important attribute values """
        header_fmt = "%s (%s)"
        attrs_vals_str = ""
        attrs_vals_str += header_fmt \
            % (type(self).__name__, "True Distribution Object")
        print(attrs_vals_str)

    def __len__(self):
        return len(self.measures)

    def __iter__(self):
        for measure in self.measures:
            yield measure

    def __getitem__(self, i):
        return self.measures[i]

    def __setitem__(self, i, val):
        self.measures[i] = val

    def __repr__(self):
        return univ_repr(self, "True Distribution")


# API
from .measures import *
