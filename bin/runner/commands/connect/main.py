#!/bin/python3
from command import CompositeCommand

class ConnectCmd(CompositeCommand):
    def __init__(self):
        self._name = 'connect'
        self._desc = 'Connect to a database'
        connections = [cls() for cls in Connection.__subclasses__()]
        super().__init__(exps)
