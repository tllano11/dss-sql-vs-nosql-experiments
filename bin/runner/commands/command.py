#!/bin/python3
import sys
import abc
import argparse

class Command (abc.ABC):
    @abc.abstractmethod
    def __init__():
        self._name = None
        self._desc = None

    @abc.abstractmethod
    def create_parser(self):
        pass

    def get_name(self):
        return self._name

    def get_desc(self):
        return self._desc

class CompositeCommand(Command):
    def __init__(self, cmdList=None):
        if cmdList is None:
            self._cmds = []
        else:
            self._cmds = cmdList

    def add(self, cmd):
        _commands.append(command)

    def create_parser(self, parsers):
        parser = parsers.add_parser(
            self.get_name(), 
            help=self.get_desc()
        )
        parser.set_defaults(func=lambda x: parser.print_usage())
        subparsers = parser.add_subparsers(help='sub-command help')
        for cmd in self._cmds:
            cmd.create_parser(subparsers)    

