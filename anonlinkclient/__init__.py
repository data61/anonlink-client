import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("anonlink-client").version
except pkg_resources.DistributionNotFound:
    __version__ = "development"

__author__ = "Data61"
