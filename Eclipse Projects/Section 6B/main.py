import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from strategies.run_zipline import run_strategy


def main():
    print("*** PackPub - Hands-on Machine Learning for Algorithmic Trading Bots ***")
    print("*** SEC005/VID002: Implement Scalping Strategy ***")
    perf = run_strategy("scalping")
    perf.to_csv("scalping.csv")


if __name__ == '__main__':
    main()
