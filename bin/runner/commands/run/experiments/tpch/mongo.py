#!/bin/python3
from command import Command

class TpchMongoExp(Command):
    def __init__(self):
        self._name = 'mongo'
        self._desc = 'Run TPCH queries for MongoDB only'
        
    def set_parser(self, parser):
        return self.__parser

    def create_parser(self, subparsers):
        subparser = subparsers.add_parser(
            self.get_name(),
            help=self.get_desc()
        )
        subparser.add_argument(
            '--with-indices', default=False, 
            action='store_true',
            help='Create indices before running experiment'
        ) 
        subparser.add_argument(
            '--load-collections-1by1', default=False, 
            action='store_true',
            help='Load collection and execute its respective queries thereafter'
        )       
        subparser.add_argument(
            '--with-scale', type=int, default=1,
            help='Scale (in GB) used to produce the dataset'
        )
        subparser.set_defaults(func=self.run)
        return subparser

    def run(self, args):
        if args.with_indices:
            print('TODO: add_indices')
        
        if args.load_collections_1by1:
            print('TODO: load_collections_1by1')

        print(args.load_collections_1by1)
