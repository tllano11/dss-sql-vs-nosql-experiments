#!/bin/python3
import sys
sys.path.append("./experiments")
import abc
import argparse
from experiments.experiment import *

class Command (abc.ABC):
    @abc.abstractmethod
    def create_parser(self):
        pass

class CompositeCommand(Command):
    def __init__(self, cmdList=None):
        if cmdList is None:
            self.__cmds = []
        else:
            self.__cmds = cmdList

    def add(self, cmd):
        __commands.append(command)

    def create_parser(self):
        for cmd in self.__cmds:
            cmd.create_parser()
        
class RunCmd(CompositeCommand):
    def __init__(self, subparsers):
        parser = subparsers.add_parser('run', help='Run experiment')
        self.__subparser = parser
        exps = [ExpCmd(parser, cls()) for cls in Experiment.__subclasses__()]
        super().__init__(exps)

    def __create_parser(self):
        super().create_parser()

class ExpCmd(Command):
    def __init__(self, subparser, exp):
        self.__subparser = subparser
        self.__exp = exp
        
    def create_parser(self):
        parser = self.__exp.create_parser(self.__subparser)
        parser.add_argument(
            '--output',
            help='Directory where results will be stored'
        )        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    runCmd = RunCmd(subparsers)
    runCmd.create_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(args)
    
