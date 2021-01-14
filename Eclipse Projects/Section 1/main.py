import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from strategies.run_zipline import run_strategy
import zipline
import os


def main():
    zipline_dir = os.path.dirname(zipline.__file__)
    print("*** Zipline is installed @ {} ***".format(zipline_dir))
    print("*** PackPub - Hands-on Machine Learning for Algorithmic Trading Bots ***")
    print("*** SEC001/VID005: Build the Conventional Buy and Hold Strategy ***")
    perf = run_strategy("buy_and_hold")
    perf.to_csv("buy_and_hold.csv")


if __name__ == '__main__':
    main()