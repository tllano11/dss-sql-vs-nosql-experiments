#!/bin/python3
import abc
import sys
from command import CompositeCommand

class Experiment(CompositeCommand):
    @abc.abstractmethod
    def __init__(self, cmdList=None):
        super().__init__(cmdList)

    @abc.abstractmethod
    def run(self):
        pass
