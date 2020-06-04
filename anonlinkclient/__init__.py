import pkg_resources
from .rest_client import RestClient, ServiceError

try:
    __version__ = pkg_resources.get_distribution('anonlink-client').version
except pkg_resources.DistributionNotFound:
    __version__ = "development"

__author__ = "Data61"