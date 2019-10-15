#!/bin/python3
import sys
sys.path.append("./run")
from run.main import RunCmd
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    runCmd = RunCmd()
    runCmd.create_parser(subparsers)
    args = parser.parse_args(sys.argv[1:])
    args.func(args)

