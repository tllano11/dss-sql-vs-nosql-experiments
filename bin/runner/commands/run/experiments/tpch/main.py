from experiments.main import Experiment
from .mongo import TpchMongoExp

class Tpch(Experiment):
    def __init__(self):
        self.__name = 'tpch'
        self.__desc = 'Type of TPCH queries to run'
        exps = [ TpchMongoExp() ]
        super().__init__(exps)

    def get_name(self):
        return self.__name

    def get_desc(self):
        return self.__desc

    def run(self):
        pass
