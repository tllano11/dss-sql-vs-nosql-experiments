import numpy as np
import pandas as pd
import matplotlib.cm as cmx
import matplotlib.colors as clrs
import matplotlib.pyplot as plt
from itertools import cycle
from abc import ABCMeta, abstractmethod

class Chart:
    __ctypes = [
        { 
            "name": "traversal_comparison",
            "description": "Compare the cost of traversal within the collection",
            "func": "_traversal_comparison_plotter"
        },
        {
            "name": "lookup_cost",
            "description": "Compare the cost of the same query with different lookup orders",
            "func": "_lookup_cost_plotter"
        }
    ]
    
    def get_plotter(self, ctype):
        for t in self,__ctypes:
            if t.get("name", None) == ctype:
                plotter = t["func"]
                return getattr(self, plotter)
        raise Exception("Chart type is not defined")
        
    def _traversal_comparison_plotter(self):
        pass

    def _lookup_cost_plotter(self):
        pass
