#!/bin/python3
import os
import re
import sys
import csv
import numpy as np
import argparse
import pandas as pd
import matplotlib.cm as cmx
import matplotlib.colors as clrs
import matplotlib.pyplot as plt
from itertools import cycle

def read(fname):
    with open(fname) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ')
        content = []
        for row in csvreader:
            query = row[0]
            time = float(row[1])
            content.append([query, time])
    return content
