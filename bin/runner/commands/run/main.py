#!/bin/python3
import sys
sys.path.append("./experiments")
import argparse
from command import CompositeCommand
from experiments.main import Experiment

class RunCmd(CompositeCommand):
    def __init__(self):
        self._name = 'run'
        self._desc = 'Run experiment'
        exps = [cls() for cls in Experiment.__subclasses__()]
        super().__init__(exps)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    runCmd = RunCmd(subparsers)
    runCmd.create_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func(args)
