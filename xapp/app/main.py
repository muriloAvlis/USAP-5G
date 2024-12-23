import argparse

from mdclogpy import Logger, Level
from .kpimon.kpimon import Kpimon


class usapXapp(object):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", dest="verbose", help="Verbose logging level",
                            required=False, type=int, default=2)

        args = parser.parse_args()

        if args.verbose == 0:
            loglevel = Level.ERROR
        if args.verbose == 1:
            loglevel = Level.WARNING
        elif args.verbose == 2:
            loglevel = Level.INFO
        elif args.verbose >= 3:
            loglevel = Level.DEBUG

        self.logger = Logger('usap-xapp', loglevel)
        self.kpimon = Kpimon()

    def print_gnb_list(self):
        gnb_lst = self.kpimon.get_gnb_list()
        self.logger.info(f'Gnb list connected to Near-RT RIC: {gnb_lst}')


def run():
    xapp = usapXapp()
    xapp.logger.info('Running usap-xapp!')
    xapp.print_gnb_list()
